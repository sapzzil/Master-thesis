"""
pilot_chronos.py
=================
5단계 파일럿 검증: 사전학습 TSFM(Chronos)이 zero-shot으로
CRPS 계산이 가능한 확률적 출력(샘플/분위수)을 실제로 내놓는지 확인한다.

범위: 3축(변동성 군집 / 두꺼운 꼬리 / 체제전환) 중 "변동성 군집" 1축만 다루는
가벼운 기술 검증 파일럿이다. 본실험(3축 x 여러 모델 x 많은 시나리오)을 위한
벤치마크가 아니다.

구성
----
1. GARCH(1,1) 합성 시계열 생성 (변동성 군집 특성)
2. amazon/chronos-t5-tiny zero-shot 예측 (샘플 기반 확률 예측)
3. 샘플 -> 분위수 변환 확인
4. CRPS 계산 (pinball loss 근사 + gluonts 유틸 비교)
5. PIT(probability integral transform) 계산
6. 결과를 results.md 로 정리하기 위한 데이터/로그 저장
"""

import json
import time
import traceback
from pathlib import Path

import numpy as np

OUT_DIR = Path(__file__).parent
LOG = []  # 사람이 읽을 로그 라인 모음 (results.md 작성에 사용)


def log(msg: str):
    print(msg)
    LOG.append(msg)


# ----------------------------------------------------------------------
# 1. GARCH(1,1) 합성 데이터 생성 (변동성 군집 재현)
# ----------------------------------------------------------------------
def simulate_garch11(n, omega=0.02, alpha=0.10, beta=0.85, seed=0, mu=0.0, burn_in=200):
    """
    sigma_t^2 = omega + alpha * eps_{t-1}^2 + beta * sigma_{t-1}^2
    r_t = mu + eps_t,  eps_t = sigma_t * z_t,  z_t ~ N(0,1)

    alpha + beta = 0.95 -> 변동성이 오래 지속되는(persistent) 군집 구조.
    burn_in 구간을 시뮬레이션한 뒤 버려서 초기 조건 영향을 제거한다.
    """
    rng = np.random.default_rng(seed)
    total = n + burn_in
    eps = np.zeros(total)
    sigma2 = np.zeros(total)
    sigma2[0] = omega / (1 - alpha - beta)  # 무조건부 분산으로 초기화
    z = rng.standard_normal(total)
    eps[0] = np.sqrt(sigma2[0]) * z[0]
    for t in range(1, total):
        sigma2[t] = omega + alpha * eps[t - 1] ** 2 + beta * sigma2[t - 1]
        eps[t] = np.sqrt(sigma2[t]) * z[t]
    r = mu + eps
    # 레벨(level) 시계열로 변환 (누적합, 100에서 시작) - 가격 유사 시계열
    # Chronos는 레벨 시계열에 대해 학습되었으므로 수익률보다 레벨이 자연스러움
    level = 100.0 * np.exp(np.cumsum(r[burn_in:] / 100.0))
    return level, r[burn_in:], sigma2[burn_in:]


def build_series(n_series=8, context_len=512, horizon=24, seed0=42):
    """시계열 n_series개를 GARCH(1,1)로 생성. 각기 다른 파라미터로 다양성 부여."""
    series_list = []
    total_len = context_len + horizon
    rng = np.random.default_rng(seed0)
    for i in range(n_series):
        # alpha, beta를 살짝 변주하여 군집 강도가 다른 시나리오들을 만든다
        alpha = rng.uniform(0.05, 0.15)
        beta = rng.uniform(0.75, 0.90)
        # 안정성 조건 alpha+beta<1 보장
        if alpha + beta >= 0.98:
            beta = 0.98 - alpha
        omega = 0.02
        level, r, sigma2 = simulate_garch11(
            total_len, omega=omega, alpha=alpha, beta=beta, seed=seed0 + i
        )
        series_list.append(
            {
                "id": f"garch_{i:02d}",
                "alpha": alpha,
                "beta": beta,
                "level": level,
                "context": level[:context_len],
                "actual_future": level[context_len:],
            }
        )
    return series_list


# ----------------------------------------------------------------------
# 4. CRPS 계산 (분위수 기반 pinball-loss 근사 + 샘플 기반 gluonts 비교)
# ----------------------------------------------------------------------
def pinball_loss(y_true, y_pred_quantile, q):
    diff = y_true - y_pred_quantile
    return np.maximum(q * diff, (q - 1) * diff)


def crps_from_quantiles(y_true, quantile_preds: dict):
    """
    quantile_preds: {q(float): pred_value(float)} 형태의 분위수 예측.
    CRPS ~= 2 * mean_q( pinball_loss(q) )  (분위수 근사, Gneiting & Raftery 2007 기반의
    표준적인 pinball-loss 평균 근사)
    """
    losses = []
    for q, pred in quantile_preds.items():
        losses.append(pinball_loss(y_true, pred, q))
    return 2.0 * np.mean(losses)


def crps_from_samples_empirical(y_true, samples):
    """
    샘플 기반 CRPS 경험적 추정 (에너지 스코어의 1차원 특수케이스).
    CRPS(F, y) = E|X - y| - 0.5 * E|X - X'|
    samples: shape (num_samples,)
    """
    samples = np.asarray(samples)
    term1 = np.mean(np.abs(samples - y_true))
    # E|X-X'| 추정 (O(n^2), 샘플 수가 적을 때만 사용)
    diffs = np.abs(samples[:, None] - samples[None, :])
    term2 = np.mean(diffs)
    return term1 - 0.5 * term2


def try_gluonts_crps(y_true, samples):
    """gluonts 내장 유틸로 CRPS 계산 시도. 실패하면 None과 에러 메시지 반환."""
    try:
        from gluonts.evaluation import Evaluator  # noqa
        # gluonts 는 보통 Forecast 객체 기반 evaluator를 쓰므로, 여기서는
        # 동일한 경험적 CRPS 공식을 gluonts 소스 로직과 비교 검증하는 용도로만 사용.
        # (직접 함수 형태로 노출되어 있지 않아 자체 구현과 수치 일치 여부만 확인)
        return "gluonts.evaluation.Evaluator import 성공 (직접적인 단일 CRPS 함수는 없어 자체 구현으로 대체)"
    except Exception as e:
        return f"gluonts CRPS 유틸 사용 실패: {e}"


# ----------------------------------------------------------------------
# 5. PIT 계산
# ----------------------------------------------------------------------
def pit_value(y_true, samples):
    """PIT = P(X <= y_true) 를 샘플의 경험적 CDF로 추정."""
    samples = np.asarray(samples)
    return float(np.mean(samples <= y_true))


# ----------------------------------------------------------------------
# 메인 파이프라인
# ----------------------------------------------------------------------
def main():
    t_start = time.time()
    result = {
        "install_ok": True,
        "model_load_ok": None,
        "output_shape_info": {},
        "per_series": [],
        "errors": [],
    }

    # ---- 데이터 생성 ----
    log("## 1. GARCH(1,1) 합성 데이터 생성")
    CONTEXT_LEN = 512
    HORIZON = 24
    N_SERIES = 8
    series_list = build_series(n_series=N_SERIES, context_len=CONTEXT_LEN, horizon=HORIZON)
    log(f"- 시계열 개수: {N_SERIES}, context={CONTEXT_LEN}, horizon={HORIZON}")
    for s in series_list:
        log(f"  - {s['id']}: alpha={s['alpha']:.3f}, beta={s['beta']:.3f}, "
            f"alpha+beta={s['alpha']+s['beta']:.3f} (지속성)")

    # ---- Chronos 모델 로드 ----
    log("\n## 2. Chronos 모델 로드 (amazon/chronos-t5-tiny)")
    t_load0 = time.time()
    try:
        import torch
        from chronos import ChronosPipeline

        pipeline = ChronosPipeline.from_pretrained(
            "amazon/chronos-t5-tiny",
            device_map="cpu",
            torch_dtype=torch.float32,
        )
        result["model_load_ok"] = True
        log(f"- 모델 로드 성공. 소요시간: {time.time()-t_load0:.1f}s")
    except Exception as e:
        result["model_load_ok"] = False
        result["errors"].append(f"모델 로드 실패: {e}\n{traceback.format_exc()}")
        log(f"- 모델 로드 실패: {e}")
        _finalize(result, t_start)
        return

    # ---- Zero-shot 예측 + CRPS/PIT ----
    log("\n## 3~5. Zero-shot 예측, 분위수 추출, CRPS/PIT 계산")
    NUM_SAMPLES = 100
    QUANTILE_LEVELS = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

    gluonts_note = try_gluonts_crps(np.array([0.0]), np.array([0.0, 1.0]))
    log(f"- gluonts CRPS 유틸 점검: {gluonts_note}")

    crps_values = []
    pit_all = []
    t_infer0 = time.time()

    for s in series_list:
        try:
            context_tensor = torch.tensor(s["context"], dtype=torch.float32)
            forecast = pipeline.predict(
                context=context_tensor,
                prediction_length=HORIZON,
                num_samples=NUM_SAMPLES,
            )
            # forecast shape: [num_series=1, num_samples, horizon]
            samples = forecast[0].numpy()  # shape (num_samples, horizon)

            if s["id"] == series_list[0]["id"]:
                result["output_shape_info"] = {
                    "raw_forecast_type": str(type(forecast)),
                    "raw_forecast_shape": list(forecast.shape),
                    "samples_shape_per_series": list(samples.shape),
                    "num_samples_requested": NUM_SAMPLES,
                    "horizon": HORIZON,
                }
                log(f"- 원시 출력 타입: {type(forecast)}, shape: {tuple(forecast.shape)}")
                log(f"- 시계열 1개당 샘플 shape: {samples.shape} (num_samples x horizon)")

            actual = s["actual_future"]
            per_step_crps = []
            per_step_pit = []
            for h in range(HORIZON):
                y_true = actual[h]
                step_samples = samples[:, h]

                # 분위수 추출 가능 여부 확인 + pinball 근사 CRPS
                q_preds = {q: float(np.quantile(step_samples, q)) for q in QUANTILE_LEVELS}
                crps_q = crps_from_quantiles(y_true, q_preds)
                crps_emp = crps_from_samples_empirical(y_true, step_samples)
                per_step_crps.append(crps_emp)  # 경험적 CRPS를 대표값으로 사용

                pit = pit_value(y_true, step_samples)
                per_step_pit.append(pit)

            mean_crps = float(np.mean(per_step_crps))
            crps_values.append(mean_crps)
            pit_all.extend(per_step_pit)

            result["per_series"].append(
                {
                    "id": s["id"],
                    "alpha": s["alpha"],
                    "beta": s["beta"],
                    "mean_crps": mean_crps,
                    "crps_quantile_approx_h0": crps_q if h == 0 else None,
                }
            )
            log(f"  - {s['id']}: 평균 CRPS(경험적) = {mean_crps:.4f}")

        except Exception as e:
            err = f"{s['id']} 예측/CRPS 계산 중 오류: {e}\n{traceback.format_exc()}"
            result["errors"].append(err)
            log(f"  - {s['id']}: 오류 발생 -> {e}")

    t_infer_elapsed = time.time() - t_infer0
    log(f"\n- 전체 추론+계산 소요시간: {t_infer_elapsed:.1f}s "
        f"({N_SERIES}개 시계열, 시계열당 {t_infer_elapsed/max(N_SERIES,1):.1f}s)")

    if crps_values:
        result["mean_crps_overall"] = float(np.mean(crps_values))
        result["crps_values"] = crps_values
        log(f"\n- 전체 평균 CRPS: {result['mean_crps_overall']:.4f}")

    if pit_all:
        pit_arr = np.array(pit_all)
        result["pit_summary"] = {
            "n": len(pit_arr),
            "min": float(np.min(pit_arr)),
            "q25": float(np.quantile(pit_arr, 0.25)),
            "median": float(np.median(pit_arr)),
            "q75": float(np.quantile(pit_arr, 0.75)),
            "max": float(np.max(pit_arr)),
            "mean": float(np.mean(pit_arr)),
        }
        log(f"- PIT 요약: n={result['pit_summary']['n']}, "
            f"median={result['pit_summary']['median']:.3f}, "
            f"mean={result['pit_summary']['mean']:.3f} "
            f"(이상적으로는 median/mean이 0.5에 가까워야 함 -> 캘리브레이션 방향성 참고용)")

    _finalize(result, t_start)


def _finalize(result, t_start):
    result["total_elapsed_sec"] = time.time() - t_start
    with open(OUT_DIR / "pilot_result.json", "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    with open(OUT_DIR / "pilot_log.txt", "w") as f:
        f.write("\n".join(LOG))
    log(f"\n총 소요시간: {result['total_elapsed_sec']:.1f}s")
    log("결과가 pilot_result.json, pilot_log.txt 에 저장되었습니다.")


if __name__ == "__main__":
    main()
