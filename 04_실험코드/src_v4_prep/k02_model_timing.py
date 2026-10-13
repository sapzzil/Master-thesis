# -*- coding: utf-8 -*-
"""
k02_model_timing.py — v4 준비: 새 모델 4종 실행 시간 및 GPU 메모리 측정
=============================================================================
조건 (지시서 §B):
  - 입력: numpy.random.default_rng(0)으로 생성한 가짜 가격 시계열
    P0 = 100, r ~ N(0, 0.018^2)
  - 조건: 과거 길이 3종 (21, 252, 512) × 예측 길이 5일 × 배치 크기 64
  - 각 조건 1회 워밍업 + 3회 반복 평균 (시계열 1개당 초 = 배치시간 / 64)
  - GPU 최대 메모리 사용량: torch.cuda.max_memory_allocated()
  - 출력: data/raw_v4/model_timing.csv
"""
from pathlib import Path
import time
import gc
import numpy as np
import pandas as pd
import torch

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "raw_v4"
OUT.mkdir(parents=True, exist_ok=True)

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


def generate_fake_prices(batch_size: int, context_len: int, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    r = rng.normal(0.0, 0.018, size=(batch_size, context_len))
    log_p = np.cumsum(r, axis=1) + np.log(100.0)
    return np.exp(log_p)


def run_benchmark():
    records = []
    contexts = [21, 252, 512]
    pred_len = 5
    batch_size = 64

    print(f"=== GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'} ===")

    # ---------------------------------------------------------
    # 1. Chronos-T5 large (amazon/chronos-t5-large)
    # ---------------------------------------------------------
    print("\n--- 1. Chronos-T5 large (amazon/chronos-t5-large) ---")
    from chronos import ChronosPipeline
    pipe_t5 = ChronosPipeline.from_pretrained(
        "amazon/chronos-t5-large",
        device_map=DEVICE,
        torch_dtype=torch.bfloat16,
    )

    for ctx in contexts:
        prices = generate_fake_prices(batch_size, ctx)
        t_input = torch.tensor(prices, dtype=torch.float32)

        # Batch 64 test
        torch.cuda.empty_cache()
        gc.collect()
        torch.cuda.reset_peak_memory_stats()
        try:
            # Warmup
            _ = pipe_t5.predict(t_input, prediction_length=pred_len, num_samples=200)
            times = []
            for _ in range(3):
                t0 = time.perf_counter()
                _ = pipe_t5.predict(t_input, prediction_length=pred_len, num_samples=200)
                times.append(time.perf_counter() - t0)
            avg_time = float(np.mean(times))
            sec_per_series = avg_time / batch_size
            peak_vram = torch.cuda.max_memory_allocated() / (1024 ** 2)
            status = "OK"
        except torch.OutOfMemoryError:
            print(f"  ctx={ctx}, batch={batch_size}: CUDA OOM")
            torch.cuda.empty_cache()
            avg_time = np.nan
            sec_per_series = np.nan
            peak_vram = torch.cuda.max_memory_allocated() / (1024 ** 2)
            status = "CUDA OOM"

        records.append({
            "model": "Chronos-T5-large",
            "model_id": "amazon/chronos-t5-large",
            "context_length": ctx,
            "prediction_length": pred_len,
            "batch_size": batch_size,
            "sec_per_series": round(sec_per_series, 6) if not np.isnan(sec_per_series) else "OOM",
            "avg_batch_sec": round(avg_time, 4) if not np.isnan(avg_time) else "OOM",
            "peak_vram_mb": round(peak_vram, 1),
            "status": status,
        })

        # Also measure batch=1 as reference since batch=64 is OOM
        prices_1 = generate_fake_prices(1, ctx)
        t_input_1 = torch.tensor(prices_1, dtype=torch.float32)
        torch.cuda.empty_cache()
        gc.collect()
        torch.cuda.reset_peak_memory_stats()
        try:
            _ = pipe_t5.predict(t_input_1, prediction_length=pred_len, num_samples=200)
            times_1 = []
            for _ in range(3):
                t0 = time.perf_counter()
                _ = pipe_t5.predict(t_input_1, prediction_length=pred_len, num_samples=200)
                times_1.append(time.perf_counter() - t0)
            avg_time_1 = float(np.mean(times_1))
            peak_vram_1 = torch.cuda.max_memory_allocated() / (1024 ** 2)
            records.append({
                "model": "Chronos-T5-large (ref: b=1)",
                "model_id": "amazon/chronos-t5-large",
                "context_length": ctx,
                "prediction_length": pred_len,
                "batch_size": 1,
                "sec_per_series": round(avg_time_1, 6),
                "avg_batch_sec": round(avg_time_1, 4),
                "peak_vram_mb": round(peak_vram_1, 1),
                "status": "OK (ref b=1)",
            })
        except Exception as e:
            pass

    del pipe_t5
    torch.cuda.empty_cache()
    gc.collect()

    # ---------------------------------------------------------
    # 2. Chronos-2 (amazon/chronos-2)
    # ---------------------------------------------------------
    print("\n--- 2. Chronos-2 (amazon/chronos-2) ---")
    from chronos import Chronos2Pipeline
    pipe_c2 = Chronos2Pipeline.from_pretrained(
        "amazon/chronos-2",
        device_map=DEVICE,
        torch_dtype=torch.bfloat16,
    )
    quantiles_c2 = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

    for ctx in contexts:
        prices = generate_fake_prices(batch_size, ctx)
        t_input = torch.tensor(prices, dtype=torch.float32).unsqueeze(1)

        torch.cuda.empty_cache()
        gc.collect()
        torch.cuda.reset_peak_memory_stats()
        try:
            _ = pipe_c2.predict_quantiles(t_input, prediction_length=pred_len, quantile_levels=quantiles_c2)
            times = []
            for _ in range(3):
                t0 = time.perf_counter()
                _ = pipe_c2.predict_quantiles(t_input, prediction_length=pred_len, quantile_levels=quantiles_c2)
                times.append(time.perf_counter() - t0)
            avg_time = float(np.mean(times))
            sec_per_series = avg_time / batch_size
            peak_vram = torch.cuda.max_memory_allocated() / (1024 ** 2)
            status = "OK"
        except Exception as e:
            print(f"  Chronos-2 error: {e}")
            avg_time = np.nan
            sec_per_series = np.nan
            peak_vram = torch.cuda.max_memory_allocated() / (1024 ** 2)
            status = str(e)

        records.append({
            "model": "Chronos-2",
            "model_id": "amazon/chronos-2",
            "context_length": ctx,
            "prediction_length": pred_len,
            "batch_size": batch_size,
            "sec_per_series": round(sec_per_series, 6) if not np.isnan(sec_per_series) else "ERR",
            "avg_batch_sec": round(avg_time, 4) if not np.isnan(avg_time) else "ERR",
            "peak_vram_mb": round(peak_vram, 1),
            "status": status,
        })
        print(f"  ctx={ctx}: {sec_per_series:.6f} s/series, peak VRAM: {peak_vram:.1f} MB")

    del pipe_c2
    torch.cuda.empty_cache()
    gc.collect()

    # ---------------------------------------------------------
    # 3. TimesFM-2.5 (google/timesfm-2.5-200m-pytorch)
    # ---------------------------------------------------------
    print("\n--- 3. TimesFM-2.5 (google/timesfm-2.5-200m-pytorch) ---")
    import timesfm
    from timesfm import TimesFM_2p5_200M_torch

    tfm = TimesFM_2p5_200M_torch.from_pretrained(
        "google/timesfm-2.5-200m-pytorch",
        torch_compile=False,
    )
    tfm.compile(timesfm.ForecastConfig(
        max_context=512,
        max_horizon=pred_len,
        per_core_batch_size=batch_size,
    ))

    for ctx in contexts:
        prices = generate_fake_prices(batch_size, ctx)
        input_list = list(prices)

        torch.cuda.empty_cache()
        gc.collect()
        torch.cuda.reset_peak_memory_stats()
        try:
            _ = tfm.forecast(horizon=pred_len, inputs=input_list)
            times = []
            for _ in range(3):
                t0 = time.perf_counter()
                _ = tfm.forecast(horizon=pred_len, inputs=input_list)
                times.append(time.perf_counter() - t0)
            avg_time = float(np.mean(times))
            sec_per_series = avg_time / batch_size
            peak_vram = torch.cuda.max_memory_allocated() / (1024 ** 2)
            status = "OK"
        except Exception as e:
            print(f"  TimesFM error: {e}")
            avg_time = np.nan
            sec_per_series = np.nan
            peak_vram = torch.cuda.max_memory_allocated() / (1024 ** 2)
            status = str(e)

        records.append({
            "model": "TimesFM-2.5",
            "model_id": "google/timesfm-2.5-200m-pytorch",
            "context_length": ctx,
            "prediction_length": pred_len,
            "batch_size": batch_size,
            "sec_per_series": round(sec_per_series, 6) if not np.isnan(sec_per_series) else "ERR",
            "avg_batch_sec": round(avg_time, 4) if not np.isnan(avg_time) else "ERR",
            "peak_vram_mb": round(peak_vram, 1),
            "status": status,
        })
        print(f"  ctx={ctx}: {sec_per_series:.6f} s/series, peak VRAM: {peak_vram:.1f} MB")

    del tfm
    torch.cuda.empty_cache()
    gc.collect()

    # ---------------------------------------------------------
    # 4. Moirai-2.0 (Salesforce/moirai-2.0-R-small)
    # ---------------------------------------------------------
    print("\n--- 4. Moirai-2.0 (Salesforce/moirai-2.0-R-small) ---")
    from uni2ts.model.moirai2 import Moirai2Forecast, Moirai2Module

    m_module = Moirai2Module.from_pretrained("Salesforce/moirai-2.0-R-small").to(DEVICE)

    for ctx in contexts:
        model_m2 = Moirai2Forecast(
            prediction_length=pred_len,
            target_dim=1,
            feat_dynamic_real_dim=0,
            past_feat_dynamic_real_dim=0,
            context_length=ctx,
            module=m_module,
        ).to(DEVICE)
        model_m2.eval()

        prices = generate_fake_prices(batch_size, ctx)
        past_target = torch.tensor(prices, dtype=torch.float32, device=DEVICE).unsqueeze(-1)
        past_observed = torch.ones_like(past_target, dtype=torch.bool)
        past_is_pad = torch.zeros((batch_size, ctx), dtype=torch.bool, device=DEVICE)

        torch.cuda.empty_cache()
        gc.collect()
        torch.cuda.reset_peak_memory_stats()
        try:
            with torch.no_grad():
                _ = model_m2(past_target=past_target, past_observed_target=past_observed, past_is_pad=past_is_pad)
                times = []
                for _ in range(3):
                    t0 = time.perf_counter()
                    _ = model_m2(past_target=past_target, past_observed_target=past_observed, past_is_pad=past_is_pad)
                    times.append(time.perf_counter() - t0)
            avg_time = float(np.mean(times))
            sec_per_series = avg_time / batch_size
            peak_vram = torch.cuda.max_memory_allocated() / (1024 ** 2)
            status = "OK"
        except Exception as e:
            print(f"  Moirai-2.0 error: {e}")
            avg_time = np.nan
            sec_per_series = np.nan
            peak_vram = torch.cuda.max_memory_allocated() / (1024 ** 2)
            status = str(e)

        records.append({
            "model": "Moirai-2.0-R-small",
            "model_id": "Salesforce/moirai-2.0-R-small",
            "context_length": ctx,
            "prediction_length": pred_len,
            "batch_size": batch_size,
            "sec_per_series": round(sec_per_series, 6) if not np.isnan(sec_per_series) else "ERR",
            "avg_batch_sec": round(avg_time, 4) if not np.isnan(avg_time) else "ERR",
            "peak_vram_mb": round(peak_vram, 1),
            "status": status,
        })
        print(f"  ctx={ctx}: {sec_per_series:.6f} s/series, peak VRAM: {peak_vram:.1f} MB")
        del model_m2

    del m_module
    torch.cuda.empty_cache()
    gc.collect()

    # Save to CSV
    df = pd.DataFrame(records)
    out_csv = OUT / "model_timing.csv"
    df.to_csv(out_csv, index=False, encoding="utf-8-sig")
    print("\n[model_timing.csv 완료]\n", df.to_string(index=False))


if __name__ == "__main__":
    run_benchmark()
