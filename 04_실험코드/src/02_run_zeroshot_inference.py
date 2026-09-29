# -*- coding: utf-8 -*-
"""
02_run_zeroshot_inference.py
============================
학위논문 제5단계: Zero-shot 예측 일괄 추론기 (Chronos / Moirai / Baselines)

[역할]
- 합성 시나리오 (15개) 및 실측 시장 데이터 (미국 5종목 + KODEX 200)에 대해,
  사전학습 TSFM (Chronos-Tiny / Moirai-Small / Base) 및 대조군(Random Walk, GARCH-t)의
  100개 확률 경로(샘플)를 생성하여 Parquet으로 원자적(Atomic) 저장한다.

[출력]
- results/raw_forecasts/{model_name}_{dataset_type}_{scenario_id}.parquet
  컬럼: series_id, model, step_h (1~20), y_true, sample_000 ~ sample_099
"""

import argparse
import sys
import time
from pathlib import Path
import numpy as np
import pandas as pd
import torch

ROOT = Path(__file__).resolve().parents[1]  # 04_실험코드/
DATA_SYNTHETIC = ROOT / "data" / "synthetic"
DATA_RAW = ROOT / "data" / "raw"
OUT_DIR = ROOT / "results" / "raw_forecasts"
OUT_DIR.mkdir(parents=True, exist_ok=True)

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


# -------------------------------------------------------------------------
# 1. 베이스라인 1: Naive Random Walk (Persistent Drift) 100개 경로 생성
# -------------------------------------------------------------------------
def predict_random_walk(context, horizon=20, num_samples=100, seed=42):
    """
    Random Walk with drift: y_{t+h} = y_t + h * mu + sqrt(h) * sigma * z
    100개의 몬테카를로 경로 생성 (shape: [num_samples, horizon])
    """
    rng = np.random.default_rng(seed)
    diffs = np.diff(context)
    mu_drift = np.mean(diffs)
    sigma_res = np.std(diffs, ddof=1) if len(diffs) > 1 else 0.01
    if sigma_res < 1e-6:
        sigma_res = 0.01

    h_steps = np.arange(1, horizon + 1)  # (20,)
    # z: (num_samples, horizon)
    z = rng.standard_normal((num_samples, horizon))
    # samples: (num_samples, horizon)
    samples = context[-1] + h_steps[None, :] * mu_drift + np.sqrt(h_steps)[None, :] * sigma_res * z
    return samples


# -------------------------------------------------------------------------
# 2. 베이스라인 2: GARCH(1,1)-Student-t 100개 경로 생성
# -------------------------------------------------------------------------
def predict_garch_t(context, horizon=20, num_samples=100, seed=42):
    """
    GARCH(1,1)-Student-t 몬테카를로 시뮬레이션 경로 생성
    arch 패키지로 모수 추정 후 20스텝 시뮬레이션
    """
    from arch import arch_model

    rng = np.random.default_rng(seed)
    # 로그 수익률 계산 (%)
    log_ret = np.diff(np.log(np.maximum(context, 1e-6))) * 100.0

    try:
        am = arch_model(log_ret, vol="Garch", p=1, q=1, dist="StudentsT", rescale=False)
        res = am.fit(disp="off", show_warning=False)

        omega = res.params.get("omega", 0.01)
        alpha = res.params.get("alpha[1]", 0.05)
        beta = res.params.get("beta[1]", 0.90)
        nu = res.params.get("nu", 5.0)
        mu = res.params.get("Const", 0.0)

        # 마지막 조건부 분산
        last_sigma2 = res.conditional_volatility[-1] ** 2
        last_eps = log_ret[-1] - mu

        # 100개 시뮬레이션 경로 생성
        sim_prices = np.zeros((num_samples, horizon))
        scale_t = np.sqrt((nu - 2.0) / nu) if nu > 2.0 else 1.0

        for s in range(num_samples):
            curr_sigma2 = last_sigma2
            curr_eps = last_eps
            curr_price = context[-1]

            for h in range(horizon):
                curr_sigma2 = omega + alpha * (curr_eps ** 2) + beta * curr_sigma2
                z_t = rng.standard_t(df=max(nu, 2.1)) * scale_t
                sim_ret = (mu + np.sqrt(max(curr_sigma2, 1e-6)) * z_t) / 100.0
                curr_price = curr_price * np.exp(sim_ret)
                sim_prices[s, h] = curr_price
                curr_eps = sim_ret * 100.0 - mu

        return sim_prices

    except Exception:
        # GARCH 적합 실패 시 Random Walk로 폴백
        return predict_random_walk(context, horizon, num_samples, seed)


# -------------------------------------------------------------------------
# 3. Chronos 모델 로더 및 추론
# -------------------------------------------------------------------------
_CHRONOS_PIPELINE = {}

def get_chronos_pipeline(model_id="amazon/chronos-t5-tiny"):
    global _CHRONOS_PIPELINE
    if model_id not in _CHRONOS_PIPELINE:
        print(f"  [Chronos 로딩] {model_id} (device={DEVICE})...")
        from chronos import ChronosPipeline
        _CHRONOS_PIPELINE[model_id] = ChronosPipeline.from_pretrained(
            model_id,
            device_map=DEVICE,
            torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32,
        )
    return _CHRONOS_PIPELINE[model_id]


def predict_chronos(context, model_id="amazon/chronos-t5-tiny", horizon=20, num_samples=100):
    pipeline = get_chronos_pipeline(model_id)
    context_tensor = torch.tensor(context, dtype=torch.float32)
    # forecast shape: (1, num_samples, horizon)
    forecast = pipeline.predict(context_tensor, prediction_length=horizon, num_samples=num_samples)
    return forecast[0].cpu().numpy()


# -------------------------------------------------------------------------
# 3-B. Moirai 모델 로더 및 추론 (Salesforce/moirai-1.0-R-small / base)
# -------------------------------------------------------------------------
_MOIRAI_MODEL = {}

def get_moirai_model(model_id="Salesforce/moirai-1.0-R-small", horizon=20, context_len=512, num_samples=100):
    global _MOIRAI_MODEL
    key = (model_id, horizon, context_len, num_samples)
    if key not in _MOIRAI_MODEL:
        print(f"  [Moirai 로딩] {model_id} (device={DEVICE})...")
        from uni2ts.model.moirai import MoiraiForecast, MoiraiModule
        module = MoiraiModule.from_pretrained(model_id)
        model = MoiraiForecast(
            module=module,
            prediction_length=horizon,
            context_length=context_len,
            patch_size=32,
            num_samples=num_samples,
            target_dim=1,
            feat_dynamic_real_dim=0,
            past_feat_dynamic_real_dim=0,
        ).to(DEVICE)
        model.eval()
        _MOIRAI_MODEL[key] = model
    return _MOIRAI_MODEL[key]


def predict_moirai(context, model_id="Salesforce/moirai-1.0-R-small", horizon=20, num_samples=100, seed=42):
    torch.manual_seed(seed)
    L = len(context)
    model = get_moirai_model(model_id, horizon=horizon, context_len=L, num_samples=num_samples)
    past_target = torch.tensor(context, dtype=torch.float32, device=DEVICE).view(1, L, 1)
    past_observed_target = torch.ones(1, L, 1, dtype=torch.bool, device=DEVICE)
    past_is_pad = torch.zeros(1, L, dtype=torch.bool, device=DEVICE)
    with torch.no_grad():
        preds = model(
            past_target=past_target,
            past_observed_target=past_observed_target,
            past_is_pad=past_is_pad,
            num_samples=num_samples,
        )
    # preds shape: (1, num_samples, horizon)
    return preds[0].cpu().numpy()


# -------------------------------------------------------------------------
# 4. 시계열 배치 추론 실행기
# -------------------------------------------------------------------------
def run_inference_on_series_dict(series_data, model_name, scenario_id, horizon=20, num_samples=100):
    """
    series_data: dict {series_id: {'context': np.array, 'target': np.array}}
    """
    out_file = OUT_DIR / f"{model_name}_{scenario_id}.parquet"
    print(f"  [추론 시작] 모델: {model_name} | 시나리오: {scenario_id} | 계열 수: {len(series_data)}")

    rows = []
    t0 = time.time()

    for s_idx, (s_id, s_info) in enumerate(series_data.items()):
        context = s_info["context"]
        target = s_info["target"]

        if model_name.startswith("chronos"):
            model_id = "amazon/chronos-t5-tiny" if "tiny" in model_name else "amazon/chronos-t5-base"
            samples = predict_chronos(context, model_id=model_id, horizon=horizon, num_samples=num_samples)
        elif model_name.startswith("moirai"):
            model_id = "Salesforce/moirai-1.0-R-small" if "small" in model_name else "Salesforce/moirai-1.0-R-base"
            samples = predict_moirai(context, model_id=model_id, horizon=horizon, num_samples=num_samples, seed=42 + s_idx)
        elif model_name == "random_walk":
            samples = predict_random_walk(context, horizon=horizon, num_samples=num_samples, seed=42 + s_idx)
        elif model_name == "garch_t":
            samples = predict_garch_t(context, horizon=horizon, num_samples=num_samples, seed=42 + s_idx)
        else:
            raise ValueError(f"알 수 없는 모델: {model_name}")

        # samples: (100, 20) -> h=1..20 각 스텝별로 기록
        for h in range(horizon):
            row = {
                "series_id": s_id,
                "model": model_name,
                "scenario": scenario_id,
                "step_h": h + 1,
                "y_true": float(target[h]),
            }
            for s in range(num_samples):
                row[f"s_{s:03d}"] = float(samples[s, h])
            rows.append(row)

    df_out = pd.DataFrame(rows)
    df_out.to_parquet(out_file, index=False)
    elapsed = time.time() - t0
    print(f"  [완료] -> {out_file.name} ({len(df_out)}행, 소요시간: {elapsed:.2f}초)")
    return out_file


# -------------------------------------------------------------------------
# 5. 메인 함수 (합성 및 실측 일괄 처리)
# -------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Zero-shot Multi-Model Inference Runner")
    parser.add_argument("--model", type=str, default="chronos-tiny",
                        choices=["chronos-tiny", "chronos-base", "moirai-small", "moirai-base", "moirai_all", "random_walk", "garch_t", "all_tier1", "all_tier2", "all_models"],
                        help="Model to run")
    parser.add_argument("--target", type=str, default="synthetic",
                        choices=["synthetic", "market", "both"],
                        help="Target dataset to run on")
    parser.add_argument("--smoke", action="store_true", help="Run only 1 scenario for smoke test")
    args = parser.parse_args()

    if args.model == "all_tier1":
        models_to_run = ["chronos-tiny", "moirai-small", "random_walk", "garch_t"]
    elif args.model == "all_tier2":
        models_to_run = ["chronos-base", "moirai-base", "random_walk", "garch_t"]
    elif args.model == "moirai_all":
        models_to_run = ["moirai-small", "moirai-base"]
    elif args.model == "all_models":
        models_to_run = ["chronos-base", "chronos-tiny", "moirai-base", "moirai-small", "random_walk", "garch_t"]
    else:
        models_to_run = [args.model]


    # --- 1. 합성 데이터 로드 ---
    if args.target in ["synthetic", "both"]:
        synth_files = sorted(list(DATA_SYNTHETIC.glob("*_L*.parquet")))
        if not synth_files:
            print("[오류] 합성 데이터가 없습니다. 01_generate_finstress_3axis.py를 먼저 실행하세요.")
            sys.exit(1)

        if args.smoke:
            synth_files = synth_files[:1]  # 스모크 테스트: 1개 시나리오만

        for f in synth_files:
            scenario_id = f.stem
            df = pd.read_parquet(f)
            series_ids = df["series_id"].unique()
            if args.smoke:
                series_ids = series_ids[:1]  # 스모크 테스트: 시계열 1개만

            series_dict = {}
            for sid in series_ids:
                sdf = df[df["series_id"] == sid].sort_values("step")
                ctx = sdf[sdf["is_context"]]["price"].values
                tgt = sdf[~sdf["is_context"]]["price"].values
                series_dict[sid] = {"context": ctx, "target": tgt}

            for m in models_to_run:
                run_inference_on_series_dict(series_dict, m, f"synth_{scenario_id}")

    # --- 2. 실측 시장 데이터 로드 ---
    if args.target in ["market", "both"]:
        raw_files = sorted(list(DATA_RAW.glob("us_yf_*.parquet"))) + sorted(list(DATA_RAW.glob("kr_yf_*.parquet")))
        if not raw_files:
            print("[주의] 실측 시장 데이터가 없습니다. 00_data_check.py를 먼저 실행하세요.")
        else:
            if args.smoke:
                raw_files = raw_files[:1]

            market_dict = {}
            for rf in raw_files:
                ticker = rf.stem.split("_")[-1]
                mdf = pd.read_parquet(rf)
                close_col = "close" if "close" in mdf.columns else "adj close"
                prices = mdf[close_col].dropna().values
                if len(prices) >= 532:
                    # 5개 롤링 윈도우 생성 (20일 간격)
                    n_windows = 1 if args.smoke else min(5, (len(prices) - 512) // 20)
                    for w in range(n_windows):
                        end_idx = len(prices) - w * 20
                        start_idx = end_idx - 532
                        if start_idx >= 0:
                            ctx = prices[start_idx:end_idx - 20]
                            tgt = prices[end_idx - 20:end_idx]
                            market_dict[f"market_{ticker}_w{w}"] = {"context": ctx, "target": tgt}

            for m in models_to_run:
                run_inference_on_series_dict(market_dict, m, "market_rolling")



if __name__ == "__main__":
    main()
