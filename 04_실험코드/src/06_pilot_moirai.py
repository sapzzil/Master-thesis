# -*- coding: utf-8 -*-
"""
pilot_moirai.py
================
5단계 파일럿 검증: Moirai(사전학습 TSFM, 분위수/혼합분포 출력형)가
zero-shot으로 CRPS 계산 가능한 확률적 출력을 실제로 내놓는지 확인한다.

주의(중요): 이 샌드박스 환경은 조직 네트워크 정책상 huggingface.co /
hf-mirror.com 등 외부 모델 허브에 대한 아웃바운드 접속이 전면 차단되어
있어(프록시 403), Salesforce/moirai-1.0-R-small 의 사전학습 가중치를
실제로 다운로드할 수 없었다. 이는 results.md에 상세히 기록한다.

대안: uni2ts가 실제로 사용하는 것과 동일한 아키텍처
(MoiraiModule: patch embedding + Transformer encoder + Mixture 분포
출력 헤드[StudentT + NegativeBinomial + LogNormal + NormalFixedScale])를
공개된 moirai-1.0-R-small 하이퍼파라미터로 "무작위 초기화" 상태로 구성하여,
"파이프라인/API 수준"에서 다음이 실제로 동작하는지를 검증한다:
  1) context -> MoiraiForecast -> GluonTS predictor 로 확률적 예측 생성
  2) 예측 객체에서 분위수(quantile) 추출 가능 여부
  3) 예측 객체에서 샘플(sample) 추출 가능 여부
  4) CRPS 계산 가능 여부 (pinball loss 근사 및 gluonts 유틸)
  5) PIT 값 계산 가능 여부

즉, 이 파일럿은 "사전학습 지식이 반영된 예측 품질"이 아니라
"Moirai의 확률적 출력 구조에서 CRPS/PIT을 계산하는 본실험 파이프라인이
기술적으로 성립하는가"를 검증하는 데 초점을 둔다.
"""

import time
import warnings
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

RNG_SEED = 42
CONTEXT_LEN = 512
HORIZON = 24
N_SERIES = 10
N_SAMPLES = 100  # Moirai 예측 시 뽑을 샘플 수
QUANTILE_LEVELS = [0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95]

# =========================================================================
# 1. 합성 데이터 생성: GARCH(1,1)로 변동성 군집(volatility clustering) 재현
# =========================================================================
def simulate_garch11(n, omega=0.05, alpha=0.10, beta=0.85, seed=0):
    """
    GARCH(1,1) 재귀식으로 변동성 군집을 가진 수익률 시계열을 생성한다.
        sigma_t^2 = omega + alpha * eps_{t-1}^2 + beta * sigma_{t-1}^2
        r_t = sigma_t * z_t,  z_t ~ N(0,1)
    이후 누적합(cumsum)으로 "가격 유사" 레벨 시계열을 만들어
    Moirai 입력(연속값 시계열)에 맞춘다.
    """
    rng = np.random.default_rng(seed)
    eps = np.zeros(n)
    sigma2 = np.zeros(n)
    sigma2[0] = omega / (1 - alpha - beta)  # 무조건부 분산으로 초기화
    z = rng.standard_normal(n)
    eps[0] = np.sqrt(sigma2[0]) * z[0]
    for t in range(1, n):
        sigma2[t] = omega + alpha * eps[t - 1] ** 2 + beta * sigma2[t - 1]
        eps[t] = np.sqrt(sigma2[t]) * z[t]
    # 수익률 -> 가격 레벨 (100에서 시작하는 누적합, 시계열 모델 입력에 적합)
    price = 100 + np.cumsum(eps)
    return price, eps, np.sqrt(sigma2)


def build_dataset():
    total_len = CONTEXT_LEN + HORIZON
    series_list = []
    for i in range(N_SERIES):
        # 시계열마다 GARCH 파라미터를 살짝 흔들어 다양성 부여(변동성 군집 강도 차이)
        rng_p = np.random.default_rng(1000 + i)
        omega = 0.03 + 0.04 * rng_p.random()
        alpha = 0.05 + 0.10 * rng_p.random()
        beta = 0.80 + 0.10 * rng_p.random()
        # 안정성 조건(alpha+beta<1) 강제
        if alpha + beta >= 0.999:
            beta = 0.999 - alpha
        price, eps, sigma = simulate_garch11(
            total_len, omega=omega, alpha=alpha, beta=beta, seed=2000 + i
        )
        series_list.append(
            {
                "series_id": f"garch_{i:02d}",
                "price": price,
                "context": price[:CONTEXT_LEN],
                "target": price[CONTEXT_LEN:],
                "omega": omega,
                "alpha": alpha,
                "beta": beta,
            }
        )
    return series_list


# =========================================================================
# 2. Moirai 모델 준비
# =========================================================================
def load_moirai_pretrained():
    """사전학습 체크포인트 로딩 시도. 실패 시 (None, 에러메시지) 반환."""
    from uni2ts.model.moirai import MoiraiModule

    try:
        module = MoiraiModule.from_pretrained("Salesforce/moirai-1.0-R-small")
        return module, None
    except Exception as e:  # noqa: BLE001
        return None, f"{type(e).__name__}: {e}"


def build_moirai_random_init():
    """
    moirai-1.0-R-small 의 공개된 하이퍼파라미터로 동일 아키텍처를
    무작위 초기화하여 구성한다 (네트워크 차단으로 사전학습 가중치를
    받을 수 없을 때의 파이프라인 검증용 대체 경로).
    """
    from uni2ts.model.moirai.module import MoiraiModule
    from uni2ts.distribution import (
        MixtureOutput,
        StudentTOutput,
        NegativeBinomialOutput,
        LogNormalOutput,
        NormalFixedScaleOutput,
    )

    distr_output = MixtureOutput(
        components=[
            StudentTOutput(),
            NormalFixedScaleOutput(),
            NegativeBinomialOutput(),
            LogNormalOutput(),
        ]
    )
    module = MoiraiModule(
        distr_output=distr_output,
        d_model=384,
        num_layers=6,
        patch_sizes=(8, 16, 32, 64, 128),
        max_seq_len=512,
        attn_dropout_p=0.0,
        dropout_p=0.0,
        scaling=True,
    )
    return module


# =========================================================================
# 3. GluonTS 어댑터로 zero-shot 예측 실행
# =========================================================================
def run_forecast(module, series_list, patch_size=32):
    """
    MoiraiForecast(GluonTS 어댑터)로 각 시계열의 context를 넣고
    horizon 구간을 확률적으로 예측한다. Forecast 객체에서
    분위수(quantile)와 샘플(sample) 추출이 실제로 가능한지 확인한다.
    """
    from uni2ts.model.moirai import MoiraiForecast
    from gluonts.dataset.pandas import PandasDataset

    model = MoiraiForecast(
        module=module,
        prediction_length=HORIZON,
        context_length=CONTEXT_LEN,
        patch_size=patch_size,
        num_samples=N_SAMPLES,
        target_dim=1,
        feat_dynamic_real_dim=0,
        past_feat_dynamic_real_dim=0,
    )
    predictor = model.create_predictor(batch_size=8, device="cpu")

    # GluonTS PandasDataset 구성 (context 구간만 입력으로 사용)
    dfs = {}
    for s in series_list:
        idx = pd.date_range("2020-01-01", periods=CONTEXT_LEN, freq="D")
        dfs[s["series_id"]] = pd.Series(s["context"], index=idx)
    ds = PandasDataset(dfs)

    t0 = time.time()
    forecasts = list(predictor.predict(ds))
    elapsed = time.time() - t0
    return forecasts, elapsed


def extract_quantiles_and_samples(forecast):
    """Forecast 객체에서 분위수/샘플 추출을 시도하고 결과를 반환."""
    out = {"quantiles": None, "samples": None, "errors": []}
    # 샘플 기반 추출 (SampleForecast)
    try:
        samples = forecast.samples  # shape: (num_samples, horizon)
        out["samples"] = np.asarray(samples)
    except Exception as e:  # noqa: BLE001
        out["errors"].append(f"samples 추출 실패: {e}")

    # 분위수 추출 (quantile() 메서드 - QuantileForecast/SampleForecast 공통 API)
    try:
        q_arr = np.stack(
            [forecast.quantile(q) for q in QUANTILE_LEVELS], axis=0
        )  # shape: (n_quantiles, horizon)
        out["quantiles"] = q_arr
    except Exception as e:  # noqa: BLE001
        out["errors"].append(f"quantile() 추출 실패: {e}")

    return out


# =========================================================================
# 4. CRPS 계산 (pinball loss 평균 근사) + gluonts 유틸 시도
# =========================================================================
def pinball_loss(y_true, y_pred, q):
    diff = y_true - y_pred
    return np.mean(np.maximum(q * diff, (q - 1) * diff))


def crps_from_quantiles(y_true, quantile_preds, quantile_levels):
    """
    분위수 기반 CRPS 근사: 여러 분위수에서 pinball loss를 평균한 값의 2배는
    분위수 개수가 촘촘할수록 CRPS에 수렴한다 (Gneiting & Raftery, 2007).
    quantile_preds: shape (n_quantiles, horizon), y_true: shape (horizon,)
    """
    losses = []
    for qi, q in enumerate(quantile_levels):
        losses.append(pinball_loss(y_true, quantile_preds[qi], q))
    return 2 * np.mean(losses)


def crps_from_samples_gluonts(y_true, samples):
    """gluonts 내장 CRPS 유틸(샘플 기반)을 시도. 실패 시 None."""
    try:
        from gluonts.evaluation import Evaluator  # noqa: F401
        # gluonts 0.14+에는 샘플 기반 CRPS 직접 함수가 없어 Evaluator 경로가
        # 아닌, empirical CDF 기반 근사로 대체 (아래 직접 구현 사용)
        return None
    except Exception:  # noqa: BLE001
        return None


def crps_from_samples_empirical(y_true, samples):
    """
    샘플 기반 CRPS의 empirical 근사 (energy form):
    CRPS(F, y) ~= E|X - y| - 0.5 * E|X - X'|
    """
    samples = np.asarray(samples)  # (n_samples, horizon)
    n = samples.shape[0]
    term1 = np.mean(np.abs(samples - y_true[None, :]), axis=0)
    # E|X-X'| 근사 (샘플 쌍 전체는 비용이 크므로 부분 샘플링)
    idx1 = np.random.default_rng(0).integers(0, n, size=min(n, 200))
    idx2 = np.random.default_rng(1).integers(0, n, size=min(n, 200))
    term2 = np.mean(np.abs(samples[idx1] - samples[idx2]), axis=0)
    crps_per_step = term1 - 0.5 * term2
    return np.mean(crps_per_step)


# =========================================================================
# 5. PIT (Probability Integral Transform) 계산
# =========================================================================
def pit_from_samples(y_true, samples):
    """
    각 시점에서 y_true가 예측 샘플 분포의 empirical CDF 상 어디에 위치하는지
    (경험적 PIT 값)를 계산한다. 캘리브레이션이 잘 되면 PIT ~ Uniform(0,1).
    """
    samples = np.asarray(samples)  # (n_samples, horizon)
    pit_vals = []
    for h in range(samples.shape[1]):
        pit = np.mean(samples[:, h] <= y_true[h])
        pit_vals.append(pit)
    return np.array(pit_vals)


# =========================================================================
# 메인 실행부
# =========================================================================
def main():
    log = []

    def logprint(msg):
        print(msg)
        log.append(msg)

    logprint("=" * 70)
    logprint("Moirai 파일럿 검증 시작")
    logprint("=" * 70)

    # --- 1. 데이터 생성 ---
    t0 = time.time()
    series_list = build_dataset()
    logprint(f"[1] GARCH(1,1) 합성 데이터 {N_SERIES}개 생성 완료 "
              f"(context={CONTEXT_LEN}, horizon={HORIZON}) "
              f"- {time.time()-t0:.2f}s")

    # --- 2. 모델 로딩 시도 ---
    t0 = time.time()
    module, err = load_moirai_pretrained()
    load_time = time.time() - t0
    pretrained_ok = module is not None
    if pretrained_ok:
        logprint(f"[2] 사전학습 체크포인트 로딩 성공 - {load_time:.2f}s")
        used_pretrained = True
    else:
        logprint(f"[2] 사전학습 체크포인트 로딩 실패: {err}")
        logprint("    -> 네트워크 정책으로 HuggingFace 접근 차단 확인됨.")
        logprint("    -> 동일 아키텍처(무작위 초기화)로 파이프라인 검증 대체 진행.")
        t0 = time.time()
        module = build_moirai_random_init()
        logprint(f"    무작위 초기화 MoiraiModule 구성 완료 - {time.time()-t0:.2f}s")
        used_pretrained = False

    # --- 3. 예측 실행 ---
    t0 = time.time()
    try:
        forecasts, predict_time = run_forecast(module, series_list)
        forecast_ok = True
        forecast_err = None
    except Exception as e:  # noqa: BLE001
        forecast_ok = False
        forecast_err = f"{type(e).__name__}: {e}"
        forecasts, predict_time = [], time.time() - t0
    logprint(f"[3] 예측 실행 {'성공' if forecast_ok else '실패'} - {predict_time:.2f}s")
    if not forecast_ok:
        logprint(f"    에러: {forecast_err}")

    results = []
    quantile_extract_ok = False
    sample_extract_ok = False

    if forecast_ok:
        for s, fc in zip(series_list, forecasts):
            extracted = extract_quantiles_and_samples(fc)
            y_true = s["target"]

            row = {"series_id": s["series_id"]}

            if extracted["quantiles"] is not None:
                quantile_extract_ok = True
                crps_q = crps_from_quantiles(y_true, extracted["quantiles"], QUANTILE_LEVELS)
                row["crps_quantile_approx"] = crps_q
            else:
                row["crps_quantile_approx"] = None

            if extracted["samples"] is not None:
                sample_extract_ok = True
                crps_s = crps_from_samples_empirical(y_true, extracted["samples"])
                row["crps_sample_empirical"] = crps_s
                pit_vals = pit_from_samples(y_true, extracted["samples"])
                row["pit_mean"] = float(np.mean(pit_vals))
                row["pit_std"] = float(np.std(pit_vals))
                row["pit_values"] = pit_vals.tolist()
            else:
                row["crps_sample_empirical"] = None
                row["pit_mean"] = None
                row["pit_std"] = None
                row["pit_values"] = None

            if extracted["errors"]:
                row["errors"] = "; ".join(extracted["errors"])
            else:
                row["errors"] = ""

            results.append(row)

    logprint(f"[4] 분위수 추출 가능 여부: {quantile_extract_ok}")
    logprint(f"[5] 샘플 추출 가능 여부: {sample_extract_ok}")

    # --- 결과 요약 저장 ---
    df = pd.DataFrame(results)
    df.to_csv("pilot_moirai_results.csv", index=False)

    summary = {
        "pretrained_loaded": pretrained_ok,
        "used_pretrained": used_pretrained,
        "forecast_ok": forecast_ok,
        "quantile_extract_ok": quantile_extract_ok,
        "sample_extract_ok": sample_extract_ok,
        "n_series": len(series_list),
        "predict_time_sec": predict_time,
        "hf_load_error": err,
    }
    if len(df) > 0 and "crps_quantile_approx" in df.columns:
        summary["mean_crps_quantile_approx"] = df["crps_quantile_approx"].mean()
    if len(df) > 0 and "crps_sample_empirical" in df.columns:
        summary["mean_crps_sample_empirical"] = df["crps_sample_empirical"].mean()
    if len(df) > 0 and "pit_mean" in df.columns:
        summary["mean_pit"] = df["pit_mean"].mean()

    logprint("=" * 70)
    logprint("요약:")
    for k, v in summary.items():
        logprint(f"  {k}: {v}")
    logprint("=" * 70)

    # 로그 파일 저장 (results.md 작성용 원자료)
    with open("pilot_run_log.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(log))

    return summary, df


if __name__ == "__main__":
    main()
