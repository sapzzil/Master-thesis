# -*- coding: utf-8 -*-
"""
05_conformal_calibrator.py
==========================
학위논문 제5단계: 무재학습 적응형 콘포멀 사후 보정기 (ACI, Gibbs & Candes 2021)

[이론 및 알고리즘]
- 모델 가중치는 100% 동결(Frozen, 재학습 0원)
- 예측 분위수 q_{alpha_t/2}, q_{1 - alpha_t/2}의 명목 알파를 시계열 오차에 따라 동적 적응:
  alpha_{t+1} = alpha_t + gamma * (alpha_nominal - err_t)
  err_t = 1 if y_t not in interval else 0
- Kupiec POF (Proportion of Failures) 우도비 검정으로 VaR/신뢰구간 적합성 판정

출력:
- results/calibrated_metrics.csv
- results/tables/table3_conformal_restoration.csv & .md
"""

from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]  # 04_실험코드/
IN_DIR = ROOT / "results" / "raw_forecasts"
OUT_DIR = ROOT / "results"
TABLES_DIR = OUT_DIR / "tables"
TABLES_DIR.mkdir(parents=True, exist_ok=True)


def kupiec_pof_test(failures, total_trials, p_nominal=0.10):
    """
    Kupiec POF (Proportion of Failures) Likelihood Ratio Test
    H0: 실제 실패율 == p_nominal (0.10)
    LR = -2 * ln( L(p_nominal) / L(p_hat) ) ~ Chi2(1)
    """
    if failures == 0 or failures == total_trials:
        return 0.0, 1.0

    p_hat = failures / total_trials
    num = ((1.0 - p_nominal) ** (total_trials - failures)) * (p_nominal ** failures)
    den = ((1.0 - p_hat) ** (total_trials - failures)) * (p_hat ** failures)

    lr_stat = -2.0 * np.log(max(num / den, 1e-12))
    p_value = 1.0 - stats.chi2.cdf(lr_stat, df=1)
    return float(lr_stat), float(p_value)


def run_conformal_calibration(gamma=0.05, alpha_nominal=0.10):
    forecast_files = sorted(list(IN_DIR.glob("*.parquet")))
    if not forecast_files:
        print("[오류] raw_forecasts 파일이 없습니다.")
        return

    print("\n" + "=" * 68)
    print(" [적응형 콘포멀 사후 보정(ACI) 가동]")
    print(f" 목표 명목 커버리지: {1.0 - alpha_nominal:.1%} (alpha={alpha_nominal:.2f}) | 학습률 gamma={gamma}")
    print("=" * 68)

    results = []

    for f in forecast_files:
        df = pd.read_parquet(f)
        sample_cols = [c for c in df.columns if c.startswith("s_")]
        if not sample_cols:
            continue

        model_name = df["model"].iloc[0]
        scenario_id = df["scenario"].iloc[0]

        # 보정 전 실측치
        raw_cov_list = []
        raw_width_list = []

        # ACI 보정용 시뮬레이션
        cal_cov_list = []
        cal_width_list = []

        # 시계열별로 ACI 추적
        for sid in df["series_id"].unique():
            sdf = df[df["series_id"] == sid].sort_values("step_h")
            curr_alpha = alpha_nominal

            for _, row in sdf.iterrows():
                samples = row[sample_cols].values.astype(float)
                y_true = float(row["y_true"])

                # 1) 보정 전 (명목 90% 고정: 5% ~ 95%)
                q_low_raw = np.percentile(samples, 5.0)
                q_high_raw = np.percentile(samples, 95.0)
                raw_in = 1 if (q_low_raw <= y_true <= q_high_raw) else 0
                raw_cov_list.append(raw_in)
                raw_width_list.append(q_high_raw - q_low_raw)

                # 2) ACI 적응형 보정 분위수
                q_pct_low = max(0.5, (curr_alpha / 2.0) * 100.0)
                q_pct_high = min(99.5, (1.0 - curr_alpha / 2.0) * 100.0)
                q_low_cal = np.percentile(samples, q_pct_low)
                q_high_cal = np.percentile(samples, q_pct_high)

                cal_in = 1 if (q_low_cal <= y_true <= q_high_cal) else 0
                cal_cov_list.append(cal_in)
                cal_width_list.append(q_high_cal - q_low_cal)

                # ACI 상태 갱신: 벗어났으면(err=1) 다음 알파 축소(구간 넓힘), 들어왔으면(err=0) 알파 확대(구간 좁힘)
                err_t = 1 - cal_in
                curr_alpha = np.clip(curr_alpha + gamma * (alpha_nominal - err_t), 0.01, 0.40)

        n_total = len(raw_cov_list)
        raw_cov = np.mean(raw_cov_list)
        cal_cov = np.mean(cal_cov_list)
        raw_w = np.mean(raw_width_list)
        cal_w = np.mean(cal_width_list)

        # Kupiec 검정
        lr_raw, p_raw = kupiec_pof_test(n_total - sum(raw_cov_list), n_total, alpha_nominal)
        lr_cal, p_cal = kupiec_pof_test(n_total - sum(cal_cov_list), n_total, alpha_nominal)

        results.append({
            "model": model_name,
            "scenario": scenario_id,
            "n_obs": n_total,
            "raw_coverage": raw_cov,
            "cal_coverage": cal_cov,
            "cov_improvement": abs(raw_cov - 0.90) - abs(cal_cov - 0.90),
            "raw_mean_width": raw_w,
            "cal_mean_width": cal_w,
            "width_ratio": cal_w / max(raw_w, 1e-6),
            "kupiec_p_raw": p_raw,
            "kupiec_p_cal": p_cal,
            "is_h5_success": abs(cal_cov - 0.90) <= 0.02,
        })

    res_df = pd.DataFrame(results)
    out_csv = OUT_DIR / "calibrated_metrics.csv"
    res_df.to_csv(out_csv, index=False)
    print(f"  [저장 완료] 보정 메트릭 -> {out_csv.name}")

    # Table 3 생성 (논문 실물 표)
    table3 = res_df[["model", "scenario", "raw_coverage", "cal_coverage", "width_ratio", "kupiec_p_raw", "kupiec_p_cal", "is_h5_success"]]
    t3_csv = TABLES_DIR / "table3_conformal_restoration.csv"
    table3.to_csv(t3_csv, index=False)

    t3_md = TABLES_DIR / "table3_conformal_restoration.md"
    md_content = [
        "# [Table 3] 무재학습 적응형 콘포멀 사후 보정(ACI) 전/후 90% 신뢰구간 복원율 비교표",
        "",
        table3.to_markdown(index=False),
        "",
        "- `raw_coverage`: 동결 TSFM의 원시 90% 명목 커버리지 실측치",
        "- `cal_coverage`: ACI 사후 보정 후 실측 커버리지 (목표: 90% +- 2%)",
        "- `width_ratio`: 보정 후 신뢰구간 너비 비율 (너비 폭증 통제 여부)",
        "- `kupiec_p_cal`: Kupiec POF 검정 p-value (p > 0.05 이면 통계적으로 90% 구간 적합)",
        "- `is_h5_success`: 가설 H5 성공 여부 (|Coverage - 0.90| <= 0.02)",
    ]
    t3_md.write_text("\n".join(md_content), encoding="utf-8")
    print(f"  [Table 3 생성 완료] -> {t3_csv.name} & {t3_md.name}")

    print("\n[Table 3 미리보기]")
    print(table3.to_string())


if __name__ == "__main__":
    run_conformal_calibration()
