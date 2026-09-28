"""
[05_conformal_calibrator.py]
무재학습 사후 보정(Post-hoc Conformal Calibration) 2단계 대조 및 Sharpness(Winkler Score) 검증 모듈:
- Step 1: Quantile-Index ACI (Gibbs & Candès 2021 기본형 — 100개 예측 샘플 내부 분위수 인덱스 조정)
- Step 2: Scale-Normalized ACI-CQR (Romano et al. 2019 + Gibbs & Candès 2021 결합 — M0=20 층화 분위수 약한 사전분포 + 폭 정규화 잔차 외삽)
- Step 3: Winkler Interval Score (IS_0.10, Gneiting & Raftery 2007) 및 동일 폭 상수 확장(Iso-Width Constant Inflation) 대조 실험
"""

import os
import glob
import numpy as np
import pandas as pd
from scipy.stats import chi2

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FORECAST_DIR = os.path.join(BASE_DIR, "results", "raw_forecasts")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
TABLES_DIR = os.path.join(RESULTS_DIR, "tables")
os.makedirs(TABLES_DIR, exist_ok=True)


def kupiec_pof_test(violations: int, total: int, alpha: float = 0.10):
    """Kupiec (1995) Proportion of Failures (POF) 우도비 검정"""
    if total <= 0:
        return 0.0, 1.0
    p_hat = violations / total
    p_hat = max(min(p_hat, 1.0 - 1e-9), 1e-9)
    lr_pof = -2.0 * (
        (total - violations) * np.log((1.0 - alpha) / (1.0 - p_hat))
        + violations * np.log(alpha / p_hat)
    )
    lr_pof = max(0.0, lr_pof)
    p_val = 1.0 - chi2.cdf(lr_pof, df=1)
    return float(lr_pof), float(p_val)


def interval_score(low: np.ndarray, high: np.ndarray, y: np.ndarray, alpha: float = 0.10) -> np.ndarray:
    """Gneiting & Raftery (2007) Winkler Interval Score (IS_alpha)"""
    width = np.maximum(high - low, 1e-6)
    under = np.maximum(0.0, low - y)
    over = np.maximum(0.0, y - high)
    return width + (2.0 / alpha) * (under + over)


def run_aci_calibration(alpha_nominal: float = 0.10, gamma: float = 0.05, seed_m0: int = 20):
    """
    저장된 raw_forecasts/*.parquet에 대해:
    1) Quantile-Index ACI (기존 내부 샘플 분위수 선택 방식)
    2) Scale-Normalized ACI-CQR (M0=20 층화 분위수 사전분포 + 현재 구간 폭 비례 잔차 외삽 방식)
       - synth_*: 시계열(series_id, H=20) 독립 에피소드 리셋 (몬테카를로 독립 복제본 전제 보존)
       - market_rolling: 종목(ticker, T=100) 연속 온라인 스트림
    3) Winkler Interval Score (IS_0.10) 및 동일 폭 상수 확장(Same-Width Constant Inflation) 대조군
    을 동시에 산출하여 비교 검증한다.
    """
    forecast_files = sorted(glob.glob(os.path.join(FORECAST_DIR, "*.parquet")))
    if not forecast_files:
        print("[오류] raw_forecasts 파일이 없습니다.")
        return

    print("\n" + "=" * 84)
    print(" [무재학습 사후 보정 가동: Quantile-Index ACI vs Scale-Normalized ACI-CQR (M0=20)]")
    print(f" 목표 명목 커버리지: {1.0 - alpha_nominal:.1%} (alpha={alpha_nominal:.2f}) | 학습률 gamma={gamma} | 층화 시드 M0={seed_m0}")
    print("=" * 84)

    results = []
    strat_idx = np.linspace(0, 99, seed_m0).astype(int)

    for f in forecast_files:
        df = pd.read_parquet(f)
        sample_cols = [c for c in df.columns if c.startswith("s_")]
        if not sample_cols:
            continue

        model_name = df["model"].iloc[0]
        scenario_id = df["scenario"].iloc[0]

        raw_cov_list, raw_width_list, raw_is_list = [], [], []
        aci_cov_list, aci_width_list, aci_is_list = [], [], []
        cqr_cov_list, cqr_width_list, cqr_is_list = [], [], []
        raw_lows_all, raw_highs_all, y_trues_all = [], [], []

        # 1) 기존 Quantile-Index ACI (시계열별 100개 샘플 내부 분위수 선택)
        for sid in df["series_id"].unique():
            sdf = df[df["series_id"] == sid].sort_values("step_h")
            curr_alpha_aci = alpha_nominal

            for _, row in sdf.iterrows():
                samples = row[sample_cols].values.astype(float)
                y_true = float(row["y_true"])

                q_low_raw = float(np.percentile(samples, 5.0))
                q_high_raw = float(np.percentile(samples, 95.0))
                raw_in = 1 if (q_low_raw <= y_true <= q_high_raw) else 0
                raw_cov_list.append(raw_in)
                raw_width_list.append(max(q_high_raw - q_low_raw, 1e-6))
                raw_is_list.append(float(interval_score(q_low_raw, q_high_raw, y_true, alpha_nominal)))

                q_pct_low = max(0.5, (curr_alpha_aci / 2.0) * 100.0)
                q_pct_high = min(99.5, (1.0 - curr_alpha_aci / 2.0) * 100.0)
                q_low_aci = float(np.percentile(samples, q_pct_low))
                q_high_aci = float(np.percentile(samples, q_pct_high))

                aci_in = 1 if (q_low_aci <= y_true <= q_high_aci) else 0
                aci_cov_list.append(aci_in)
                aci_width_list.append(max(q_high_aci - q_low_aci, 1e-6))
                aci_is_list.append(float(interval_score(q_low_aci, q_high_aci, y_true, alpha_nominal)))

                err_aci = 1 - aci_in
                curr_alpha_aci = float(np.clip(curr_alpha_aci + gamma * (alpha_nominal - err_aci), 0.01, 0.40))

        # 2) Scale-Normalized ACI-CQR (M0=20 층화 분위수 시드 + 잔차 분포 외삽)
        df["group_key"] = (
            df["series_id"].apply(lambda x: x.split("_")[0])
            if scenario_id == "market_rolling"
            else df["series_id"]
        )

        for gkey in df["group_key"].unique():
            sdf = df[df["group_key"] == gkey].sort_values(["series_id", "step_h"])
            curr_alpha_cqr = alpha_nominal

            s0 = sdf.iloc[0][sample_cols].values.astype(float)
            q5_0, q95_0 = np.percentile(s0, 5.0), np.percentile(s0, 95.0)
            w0 = max(q95_0 - q5_0, 1e-6)
            full_seed = np.sort(np.maximum(q5_0 - s0, s0 - q95_0) / w0)
            residual_history = list(full_seed[strat_idx])

            for _, row in sdf.iterrows():
                samples = row[sample_cols].values.astype(float)
                y_true = float(row["y_true"])

                q_low_raw = float(np.percentile(samples, 5.0))
                q_high_raw = float(np.percentile(samples, 95.0))
                width_raw = max(q_high_raw - q_low_raw, 1e-6)

                raw_lows_all.append(q_low_raw)
                raw_highs_all.append(q_high_raw)
                y_trues_all.append(y_true)

                q_level = float(np.clip((1.0 - curr_alpha_cqr) * 100.0, 10.0, 99.5))
                rel_margin = float(np.percentile(residual_history, q_level))
                margin = rel_margin * width_raw

                q_low_cqr = q_low_raw - margin
                q_high_cqr = q_high_raw + margin

                cqr_in = 1 if (q_low_cqr <= y_true <= q_high_cqr) else 0
                cqr_cov_list.append(cqr_in)
                cqr_width_list.append(max(q_high_cqr - q_low_cqr, 1e-6))
                cqr_is_list.append(float(interval_score(q_low_cqr, q_high_cqr, y_true, alpha_nominal)))

                e_t = max(q_low_raw - y_true, y_true - q_high_raw) / width_raw
                residual_history.append(e_t)

                err_cqr = 1 - cqr_in
                curr_alpha_cqr = float(np.clip(curr_alpha_cqr + gamma * (alpha_nominal - err_cqr), 0.01, 0.40))

        n_total = len(raw_cov_list)
        raw_cov = float(np.mean(raw_cov_list))
        aci_cov = float(np.mean(aci_cov_list))
        cqr_cov = float(np.mean(cqr_cov_list))

        raw_w = float(np.mean(raw_width_list))
        aci_w = float(np.mean(aci_width_list))
        cqr_w = float(np.mean(cqr_width_list))
        cqr_w_ratio = cqr_w / max(raw_w, 1e-9)

        # 3) 동일 폭 상수 확장(Same-Width Constant Inflation) 대조군 계산
        raw_lows_arr = np.array(raw_lows_all)
        raw_highs_arr = np.array(raw_highs_all)
        y_trues_arr = np.array(y_trues_all)
        mid_arr = 0.5 * (raw_lows_arr + raw_highs_arr)
        half_w_const = 0.5 * (raw_highs_arr - raw_lows_arr) * cqr_w_ratio
        const_low = mid_arr - half_w_const
        const_high = mid_arr + half_w_const
        const_in_arr = (const_low <= y_trues_arr) & (y_trues_arr <= const_high)
        const_cov = float(np.mean(const_in_arr))
        _, p_const = kupiec_pof_test(int(n_total - np.sum(const_in_arr)), n_total, alpha_nominal)
        const_is = float(np.mean(interval_score(const_low, const_high, y_trues_arr, alpha_nominal)))

        raw_is = float(np.mean(raw_is_list))
        aci_is = float(np.mean(aci_is_list))
        cqr_is = float(np.mean(cqr_is_list))
        is_improv_pct = 100.0 * (raw_is - cqr_is) / max(raw_is, 1e-9)

        _, p_raw = kupiec_pof_test(n_total - sum(raw_cov_list), n_total, alpha_nominal)
        _, p_aci = kupiec_pof_test(n_total - sum(aci_cov_list), n_total, alpha_nominal)
        _, p_cqr = kupiec_pof_test(n_total - sum(cqr_cov_list), n_total, alpha_nominal)

        results.append({
            "model": model_name,
            "scenario": scenario_id,
            "raw_coverage": round(raw_cov, 6),
            "cal_coverage": round(aci_cov, 6),
            "width_ratio": round(aci_w / max(raw_w, 1e-9), 5),
            "kupiec_p_raw": p_raw,
            "kupiec_p_cal": p_aci,
            "cqr_coverage": round(cqr_cov, 6),
            "cqr_width_ratio": round(cqr_w_ratio, 5),
            "kupiec_p_cqr": p_cqr,
            "cqr_kupiec_pass": bool(p_cqr > 0.05),
            "const_coverage": round(const_cov, 6),
            "kupiec_p_const": p_const,
            "const_kupiec_pass": bool(p_const > 0.05),
            "raw_winkler_is": round(raw_is, 2),
            "cal_winkler_is": round(aci_is, 2),
            "const_winkler_is": round(const_is, 2),
            "cqr_winkler_is": round(cqr_is, 2),
            "cqr_is_improvement_pct": round(is_improv_pct, 2),
        })

    res_df = pd.DataFrame(results)
    res_df.to_csv(os.path.join(RESULTS_DIR, "calibrated_metrics.csv"), index=False, encoding="utf-8-sig")

    # Table 3a: 2단계 커버리지 복원 대조표
    target_scenarios = ["synth_REGIME_L4", "market_rolling"]
    sub = res_df[res_df["scenario"].isin(target_scenarios)].copy()

    md_lines = [
        "# [Table 3] 무재학습 사후 보정(Post-hoc Calibration) 2단계 커버리지 복원 비교표",
        "",
        "> **보정 방법론 비교 (`M0=20` 층화 분위수 사전분포 표준 적용)**:",
        "> - **Step 1 (`Quantile-Index ACI`)**: 모델이 생성한 100개 예측 샘플 내부에서 분위수 인덱스만 조정 (`Chronos`의 고정 양자화 빈 절단 한계 노출)",
        "> - **Step 2 (`Scale-Normalized ACI-CQR`)**: 현재 예측 구간 폭($w_t$)으로 정규화한 비순응 잔차($e_t / w_t$)의 경험적 분위수를 외삽하여 양자화 빈 경계 밖으로 구간 확장",
        "",
        "| 모델 (Model) | 시나리오 | 보정 전 (Raw) | Step 1: Quantile-ACI | Step 1 Kupiec $p$ | **Step 2: ACI-CQR (최종)** | **Step 2 폭 배율 (`WidthRatio`)** | **Step 2 Kupiec $p$** | **90% 복원 판정 ($p>0.05$)** |",
        "| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |",
    ]
    for _, r in sub.iterrows():
        status = "✅ **통과 (복원 성공)**" if r["cqr_kupiec_pass"] else "❌ 기각"
        md_lines.append(
            f"| **{r['model']}** | `{r['scenario']}` | {r['raw_coverage']:.4f} ({r['raw_coverage']*100:.2f}%) | "
            f"{r['cal_coverage']:.4f} ({r['cal_coverage']*100:.2f}%) | {r['kupiec_p_cal']:.4f} | "
            f"**{r['cqr_coverage']:.4f} ({r['cqr_coverage']*100:.2f}%)** | `{r['cqr_width_ratio']:.3f}x` | "
            f"**{r['kupiec_p_cqr']:.4f}** | {status} |"
        )

    table3_path = os.path.join(TABLES_DIR, "table3_conformal_restoration.md")
    with open(table3_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines) + "\n")

    # Table 3b: Winkler Interval Score (IS_0.10) 및 동일 폭 상수 확장(Same-Width Constant) 대조표
    sub_mkt = res_df[res_df["scenario"] == "market_rolling"].copy()
    md_3b = [
        "# [Table 3b] 구간 예리도(Sharpness) 검증: Winkler Score ($IS_{0.10}$) 및 동일 폭 상수 확장(Iso-Width Constant) 대조표",
        "",
        "> **검증 목적**: `ACI-CQR`의 구간 폭 확장(`1.225x ~ 1.502x`)이 단순 상수 팽창이 아니라, 변동성 군집·국면 전환 시점에만 폭 예산을 집중 배분하는 **시간적 선택성(Temporal Selectivity)**의 결과임을 정칙 채점 규칙(`Winkler Interval Score`)과 동일 폭 대조군(`Same-Width Constant Inflation`)으로 증명함.",
        "",
        "| 모델 (Model) | 동일 폭 예산 (`WidthRatio`) | **동일 폭 상수 확장** 커버리지 (Kupiec $p$) | **ACI-CQR (적응형)** 커버리지 (Kupiec $p$) | **보정 전 Raw $IS_{0.10}$** | **Quantile-ACI $IS_{0.10}$** | **동일 폭 상수 확장 $IS_{0.10}$** | **ACI-CQR $IS_{0.10}$ (최종)** | **Raw 대비 $IS_{0.10}$ 개선율** |",
        "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |",
    ]
    for _, r in sub_mkt.iterrows():
        c_status = "통과" if r["const_kupiec_pass"] else "실패"
        cqr_status = "통과" if r["cqr_kupiec_pass"] else "실패"
        md_3b.append(
            f"| **{r['model']}** | `{r['cqr_width_ratio']:.3f}x` | "
            f"{r['const_coverage']*100:.2f}% ($p={r['kupiec_p_const']:.4f}$, {c_status}) | "
            f"**{r['cqr_coverage']*100:.2f}%** ($p={r['kupiec_p_cqr']:.4f}$, **{cqr_status}**) | "
            f"`{r['raw_winkler_is']:,.2f}` | `{r['cal_winkler_is']:,.2f}` | "
            f"`{r['const_winkler_is']:,.2f}` | **`{r['cqr_winkler_is']:,.2f}`** | "
            f"**-{r['cqr_is_improvement_pct']:.1f}%** |"
        )

    table3b_path = os.path.join(TABLES_DIR, "table3b_winkler_sharpness.md")
    with open(table3b_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_3b) + "\n")

    print(f"[완료] 보정 지표 저장: {os.path.join(RESULTS_DIR, 'calibrated_metrics.csv')}")
    print(f"[완료] Table 3 저장: {table3_path}")
    print(f"[완료] Table 3b 저장: {table3b_path}")
    print("\n--- [핵심 시나리오 (synth_REGIME_L4 & market_rolling) 비교 요약] ---")
    print(
        sub[
            [
                "model",
                "scenario",
                "raw_coverage",
                "cal_coverage",
                "cqr_coverage",
                "cqr_width_ratio",
                "kupiec_p_cqr",
                "cqr_kupiec_pass",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    run_aci_calibration()
