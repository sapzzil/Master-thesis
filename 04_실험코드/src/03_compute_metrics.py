# -*- coding: utf-8 -*-
"""
03_compute_metrics.py
=====================
학위논문 제5단계: 확률적 신뢰도 평가 메트릭 산출기 (불편추정 CRPS, 커버리지, PIT, KS 검정)

[핵심 수식 및 계량 이론]
1. 불편 추정 CRPS (Gneiting & Raftery 2007, Zamo & Naveau 2018):
   CRPS_hat = (1/S) * sum(|x_i - y|) - (1 / (2*S*(S-1))) * sum sum(|x_i - x_j|)
2. 명목 90% 예측구간 커버리지 및 오차:
   is_covered_90 = 1 if (q_05 <= y <= q_95) else 0
3. PIT (Probability Integral Transform) 균등분포 검정:
   scipy.stats.kstest(pit_values, 'uniform')

출력:
- results/metrics_long.parquet (시계열-스텝 단위 로우 메트릭)
- results/summary_metrics.csv (시나리오-모델 단위 집계 요약표)
"""

import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]  # 04_실험코드/
IN_DIR = ROOT / "results" / "raw_forecasts"
OUT_DIR = ROOT / "results"
OUT_DIR.mkdir(parents=True, exist_ok=True)


# -------------------------------------------------------------------------
# 1. 불편 추정 CRPS 계산 함수
# -------------------------------------------------------------------------
def compute_crps_unbiased(samples, y_true):
    """
    samples: shape (S,) 1차원 배열 (S=100)
    y_true: float 실수 관측값
    """
    S = len(samples)
    term1 = np.mean(np.abs(samples - y_true))
    # E|X - X'| 불편 추정: 2*S*(S-1)로 나눔
    diff_matrix = np.abs(samples[:, None] - samples[None, :])
    term2 = np.sum(diff_matrix) / (2.0 * S * (S - 1))
    return float(term1 - term2)


# -------------------------------------------------------------------------
# 2. 메트릭 산출 메인 루프
# -------------------------------------------------------------------------
def compute_all_metrics():
    forecast_files = sorted(list(IN_DIR.glob("*.parquet")))
    if not forecast_files:
        print("[오류] raw_forecasts 파일이 없습니다. 02_run_zeroshot_inference.py를 먼저 실행하세요.")
        return

    print(f"[메트릭 계산 시작] 대상 파일: {len(forecast_files)}개")

    long_records = []
    summary_records = []

    for f in forecast_files:
        df = pd.read_parquet(f)
        # sample 컬럼 추출 (s_000 ~ s_099)
        sample_cols = [c for c in df.columns if c.startswith("s_")]
        if not sample_cols:
            continue

        model_name = df["model"].iloc[0]
        scenario_id = df["scenario"].iloc[0]

        crps_list = []
        rel_crps_list = []
        covered90_list = []
        covered50_list = []
        width90_list = []
        rel_width90_list = []
        pit_list = []
        mae_list = []
        rel_mae_list = []

        for idx, row in df.iterrows():
            samples = row[sample_cols].values.astype(float)
            y_true = float(row["y_true"])
            denom = max(abs(y_true), 1e-8)

            # 1) 불편 추정 CRPS 및 스케일 정규화 CRPS (nCRPS %)
            crps_val = compute_crps_unbiased(samples, y_true)
            rel_crps_val = (crps_val / denom) * 100.0
            crps_list.append(crps_val)
            rel_crps_list.append(rel_crps_val)

            # 2) 분위수 및 커버리지
            q05 = np.percentile(samples, 5.0)
            q25 = np.percentile(samples, 25.0)
            q50 = np.percentile(samples, 50.0)
            q75 = np.percentile(samples, 75.0)
            q95 = np.percentile(samples, 95.0)

            cov90 = 1 if (q05 <= y_true <= q95) else 0
            cov50 = 1 if (q25 <= y_true <= q75) else 0
            width90 = float(q95 - q05)
            rel_width90 = (width90 / denom) * 100.0

            covered90_list.append(cov90)
            covered50_list.append(cov50)
            width90_list.append(width90)
            rel_width90_list.append(rel_width90)

            # 3) PIT 및 MAE
            pit = float(np.mean(samples <= y_true))
            mae = float(np.abs(np.mean(samples) - y_true))
            rel_mae = (mae / denom) * 100.0

            pit_list.append(pit)
            mae_list.append(mae)
            rel_mae_list.append(rel_mae)

            sid = str(row["series_id"])
            asset_id = sid.split("_")[1] if scenario_id == "market_rolling" else "SYNTH"

            long_records.append({
                "model": model_name,
                "scenario": scenario_id,
                "series_id": sid,
                "asset_id": asset_id,
                "step_h": row["step_h"],
                "y_true": y_true,
                "crps": crps_val,
                "rel_crps": rel_crps_val,
                "is_covered_90": cov90,
                "is_covered_50": cov50,
                "width_90": width90,
                "rel_width_90": rel_width90,
                "pit": pit,
                "mae": mae,
                "rel_mae": rel_mae,
            })

        # 시나리오 단위 집계
        mean_crps = float(np.mean(crps_list))
        mean_rel_crps = float(np.mean(rel_crps_list))
        coverage_90 = float(np.mean(covered90_list))
        coverage_50 = float(np.mean(covered50_list))
        mean_width_90 = float(np.mean(width90_list))
        mean_rel_width_90 = float(np.mean(rel_width90_list))
        mean_mae = float(np.mean(mae_list))
        mean_rel_mae = float(np.mean(rel_mae_list))

        # PIT KS 검정 (U[0, 1] 균등성 검정)
        # tie-break를 위해 미세 노이즈 추가
        pit_clean = np.array(pit_list) + np.random.uniform(-1e-6, 1e-6, size=len(pit_list))
        pit_clean = np.clip(pit_clean, 0.0, 1.0)
        ks_res = stats.kstest(pit_clean, "uniform")

        summary_records.append({
            "model": model_name,
            "scenario": scenario_id,
            "n_steps": len(df),
            "mean_crps": mean_crps,
            "mean_rel_crps": mean_rel_crps,
            "cov_90": coverage_90,
            "cov_90_err": abs(coverage_90 - 0.90),
            "cov_50": coverage_50,
            "mean_width_90": mean_width_90,
            "mean_rel_width_90": mean_rel_width_90,
            "mean_mae": mean_mae,
            "mean_rel_mae": mean_rel_mae,
            "pit_ks_stat": float(ks_res.statistic),
            "pit_ks_pvalue": float(ks_res.pvalue),
        })

    long_df = pd.DataFrame(long_records)
    long_path = OUT_DIR / "metrics_long.parquet"
    long_df.to_parquet(long_path, index=False)
    print(f"  [저장 완료] 로우 메트릭 -> {long_path.name} ({len(long_df)}행)")

    summary_df = pd.DataFrame(summary_records)
    summary_path = OUT_DIR / "summary_metrics.csv"
    summary_df.to_csv(summary_path, index=False)
    print(f"  [저장 완료] 집계 요약표 -> {summary_path.name} ({len(summary_df)}행)")
    print("\n[요약 미리보기]")
    print(summary_df[["model", "scenario", "mean_crps", "mean_rel_crps", "cov_90", "cov_90_err", "mean_mae"]].to_string())


if __name__ == "__main__":
    compute_all_metrics()
