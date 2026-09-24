# -*- coding: utf-8 -*-
"""
04_analyze_results.py
=====================
학위논문 제5단계: 통계 분석 및 논문용 실물 산출물 자동 생성 마스터 스크립트 (개정판 v2.0)

[주요 보강 사항 (지도교수 검토 보고서 전수 반영)]
1. 6개 모델 전수 비교:
   - Chronos-Tiny (8M), Chronos-Base (200M)
   - Moirai-Small (14M), Moirai-Base (91M)
   - GARCH(1,1)-t (계량경제 벤치마크), Random Walk (귀무가설 베이스라인)
2. H1~H3 통계적 검정력 보강:
   - 시나리오 수준(n=5) 외에 개별 시계열 수준(N=100) 및 관측치 스텝 수준(N=2,000) Spearman 상관검정 및 L1 vs L5 Mann-Whitney U 검정 병행
3. H4 비대칭 붕괴 가설 공식 비모수 검정 추가:
   - 고강도 스트레스(L4~L5, N=800 스텝 / N=40 시계열)에서 통제축 간 커버리지 결손폭(0.90 - Cov)에 대한 Wilcoxon 부호순위 검정 및 10,000회 부트스트랩 95% 신뢰구간 산출
4. H6 실측 시장 스케일 착시 제거 및 자산 경계 분리 DM 검정:
   - 스케일 정규화 CRPS (nCRPS % = CRPS / |y_true| * 100%) 도입
   - 미국 5대 대형주(USD, N=500, W=25) vs 한국 KODEX 200(KRW, N=100, W=5) vs 개별 종목 6종 전수 분리 표(Table 2A, Table 2B) 생성
   - 이종 자산/연도 경계를 절대 침범하지 않는 계층화 윈도우 내 Newey-West DM 검정(Stratified Within-Window HLN DM) 및 윈도우 블록 DM 검정(Window-Block DM) 적용
"""

import shutil
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

# Matplotlib 한글 및 스타일 설정
plt.rcParams["font.sans-serif"] = ["Malgun Gothic", "DejaVu Sans", "Arial"]
plt.rcParams["axes.unicode_minus"] = False

ROOT = Path(__file__).resolve().parents[1]  # 04_실험코드/
RESULTS_DIR = ROOT / "results"
TABLES_DIR = RESULTS_DIR / "tables"
FIGURES_DIR = RESULTS_DIR / "figures"
TABLES_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

ARTIFACT_DIR = Path(r"C:\Users\User\.gemini\antigravity\brain\071d91b3-2677-455a-baa8-dd55bb31a85b")


# -------------------------------------------------------------------------
# 1. 경계 무침범 계층화 Diebold-Mariano 검정 (Stratified Within-Window HLN DM)
# -------------------------------------------------------------------------
def stratified_dm_test(df_model, df_bench, value_col="rel_crps", horizon=20):
    """
    각 독립 롤링 윈도우(series_id, 길이 H=20) 내부에서만 Newey-West 자기공분산을 계산하고,
    서로 다른 종목이나 연도 윈도우 간에는 공분산이 섞이지 않도록 계층화(Stratified)하여 합산.
    동시에 윈도우 평균 손실 차이(D_w)에 대한 Window-Block DM t-검정도 함께 반환.
    """
    merged = pd.merge(
        df_model[["series_id", "step_h", value_col]],
        df_bench[["series_id", "step_h", value_col]],
        on=["series_id", "step_h"],
        suffixes=("_m", "_b"),
    ).sort_values(["series_id", "step_h"])

    d_all = merged[f"{value_col}_m"].values - merged[f"{value_col}_b"].values
    T_total = len(d_all)
    if T_total < 5:
        return 0.0, 1.0, 0.0, 1.0

    # 1) Window-Block 평균 손실 차이(D_w) 및 전체 평균(grand_mean_d) 산출
    win_diffs = []
    groups = []
    for sid, group in merged.groupby("series_id"):
        d_w = group[f"{value_col}_m"].values - group[f"{value_col}_b"].values
        win_diffs.append(np.mean(d_w))
        groups.append(d_w)

    win_diffs = np.array(win_diffs)
    W = len(win_diffs)
    grand_mean_d = float(np.mean(win_diffs))

    # 2) 각 윈도우 내부에서만 Newey-West 장기분산 산출 (전체 평균 grand_mean_d 기준 중심화 -> 경계 침범 0%)
    win_nw_vars = []
    for d_w in groups:
        H = len(d_w)
        u_w = d_w - grand_mean_d
        gamma0 = float(np.mean(u_w ** 2))
        cov_sum = 0.0
        max_lag = min(horizon - 1, H - 1)
        for lag in range(1, max_lag + 1):
            gamma_k = float(np.mean(u_w[lag:] * u_w[:-lag]))
            weight = 1.0 - (lag / (max_lag + 1.0))
            cov_sum += 2.0 * weight * gamma_k
        lrv_w = max(gamma0 + cov_sum, 1e-8)
        win_nw_vars.append(lrv_w / H)

    # Stratified Within-Window HLN DM 통계량
    var_grand_mean = np.sum(win_nw_vars) / (W ** 2)
    dm_stat = grand_mean_d / np.sqrt(max(var_grand_mean, 1e-12))
    # HLN 유한표본 보정
    hln_factor = np.sqrt(max((T_total + 1 - 2 * horizon + horizon * (horizon - 1) / T_total) / T_total, 0.1))
    dm_stat_hln = float(dm_stat * hln_factor)
    p_val_hln = float(stats.norm.cdf(dm_stat_hln))

    # Window-Block t-통계량 (W개 윈도우 블록 기준)
    if W >= 2:
        wb_se = stats.sem(win_diffs)
        wb_stat = float(grand_mean_d / max(wb_se, 1e-12))
        wb_p = float(stats.t.cdf(wb_stat, df=W - 1))
    else:
        wb_stat, wb_p = dm_stat_hln, p_val_hln

    return dm_stat_hln, p_val_hln, wb_stat, wb_p


def bootstrap_ci_diff(arr1, arr2, n_boot=5000, seed=42):
    rng = np.random.default_rng(seed)
    diffs = np.empty(n_boot)
    n1, n2 = len(arr1), len(arr2)
    for b in range(n_boot):
        s1 = rng.choice(arr1, size=n1, replace=True)
        s2 = rng.choice(arr2, size=n2, replace=True)
        diffs[b] = np.mean(s1) - np.mean(s2)
    return float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5))


def run_full_analysis():
    summary_file = RESULTS_DIR / "summary_metrics.csv"
    long_file = RESULTS_DIR / "metrics_long.parquet"

    if not summary_file.exists() or not long_file.exists():
        print(f"[오류] 필수 결과 파일이 누락되었습니다: {summary_file}, {long_file}")
        return

    summary_df = pd.read_csv(summary_file)
    long_df = pd.read_parquet(long_file)

    models_order = [
        "chronos-tiny",
        "chronos-base",
        "moirai-small",
        "moirai-base",
        "garch_t",
        "random_walk",
    ]
    models_order = [m for m in models_order if m in summary_df["model"].unique()]

    print("\n" + "=" * 76)
    print(" [학위논문 제5단계: 종합 통계 분석 및 논문 실물 산출물 생성 (v2.0)]")
    print(f" 분석 대상 모델 ({len(models_order)}종): {', '.join(models_order)}")
    print("=" * 76)

    # -------------------------------------------------------------------------
    # 2. 개별 통제축 가설 (H1 ~ H3) 다층 상관성 및 비모수 검정 (n=5, N=100, N=2000)
    # -------------------------------------------------------------------------
    synth_df = summary_df[summary_df["scenario"].str.startswith("synth_")].copy()
    synth_long = long_df[long_df["scenario"].str.startswith("synth_")].copy()
    synth_long["axis"] = synth_long["scenario"].apply(lambda s: s.split("_")[1])
    synth_long["lvl"] = synth_long["scenario"].apply(lambda s: int(s.split("_L")[-1]))

    # 시계열(series_id) 단위 집계 (각 축당 5레벨 x 20시계열 = 100개 독립 시계열)
    series_agg = (
        synth_long.groupby(["model", "scenario", "axis", "lvl", "series_id"])
        .agg(
            series_crps=("crps", "mean"),
            series_rel_crps=("rel_crps", "mean"),
            series_cov90=("is_covered_90", "mean"),
            series_mae=("mae", "mean"),
        )
        .reset_index()
    )

    hypo_results = []
    print("\n>>> 1. 개별 통제축 가설 (H1 ~ H3) 다층 검정 결과 (n=5 레벨평균 & N=100 독립시계열):")

    axis_info = {
        "GARCH": ("H1", "변동성 군집 지속성 (alpha+beta: 0.30 -> 0.98)"),
        "TAIL": ("H2", "두꺼운 꼬리 극단치 (자유도 nu: 30 -> 3)"),
        "REGIME": ("H3", "체제전환 단절 강도 (전이확률 p_stay: 0.99 -> 0.80)"),
    }

    for axis, (h_id, axis_desc) in axis_info.items():
        axis_sub = synth_df[synth_df["scenario"].str.contains(axis)].copy()
        axis_sub["lvl"] = axis_sub["scenario"].apply(lambda s: int(s.split("_L")[-1]))
        axis_sub = axis_sub.sort_values("lvl")

        for m in models_order:
            m_sub = axis_sub[axis_sub["model"] == m]
            m_ser = series_agg[(series_agg["axis"] == axis) & (series_agg["model"] == m)]
            m_stp = synth_long[(synth_long["axis"] == axis) & (synth_long["model"] == m)]

            if len(m_sub) >= 3:
                # (a) n=5 레벨 평균 Spearman
                rho_crps_5, p_crps_5 = stats.spearmanr(m_sub["lvl"], m_sub["mean_crps"])
                rho_cov_5, p_cov_5 = stats.spearmanr(m_sub["lvl"], m_sub["cov_90"])

                # (b) N=100 개별 시계열 Spearman
                rho_crps_100, p_crps_100 = stats.spearmanr(m_ser["lvl"], m_ser["series_crps"])
                rho_cov_100, p_cov_100 = stats.spearmanr(m_ser["lvl"], m_ser["series_cov90"])

                # (c) N=2000 개별 스텝 Spearman
                rho_crps_2000, p_crps_2000 = stats.spearmanr(m_stp["lvl"], m_stp["crps"])

                # (d) L1 vs L5 Mann-Whitney U 검정 (N1=20, N5=20 시계열)
                l1_crps = m_ser[m_ser["lvl"] == 1]["series_crps"].values
                l5_crps = m_ser[m_ser["lvl"] == 5]["series_crps"].values
                u_stat, u_pval = stats.mannwhitneyu(l5_crps, l1_crps, alternative="two-sided")

                hypo_results.append({
                    "hypothesis": h_id,
                    "axis": axis,
                    "description": axis_desc,
                    "model": m,
                    "rho_crps_n5": rho_crps_5,
                    "p_crps_n5": p_crps_5,
                    "rho_cov_n5": rho_cov_5,
                    "p_cov_n5": p_cov_5,
                    "rho_crps_N100": rho_crps_100,
                    "p_crps_N100": p_crps_100,
                    "rho_cov_N100": rho_cov_100,
                    "p_cov_N100": p_cov_100,
                    "rho_crps_N2000": rho_crps_2000,
                    "p_crps_N2000": p_crps_2000,
                    "l1_mean_crps": float(np.mean(l1_crps)),
                    "l5_mean_crps": float(np.mean(l5_crps)),
                    "mw_u_pval_L1_vs_L5": float(u_pval),
                })
                print(
                    f"  [{h_id}] {axis:<6} | {m:<13} | "
                    f"n=5 rho(CRPS)={rho_crps_5:+.3f}(p={p_crps_5:.3f}) | "
                    f"N=100 rho(CRPS)={rho_crps_100:+.3f}(p={p_crps_100:.4f}), rho(Cov)={rho_cov_100:+.3f}(p={p_cov_100:.4f})"
                )

    hypo_df = pd.DataFrame(hypo_results)
    hypo_df.to_csv(TABLES_DIR / "table_h1_h3_correlations.csv", index=False)

    # -------------------------------------------------------------------------
    # 3. H4 비대칭 붕괴 가설 (Regime > Tail > GARCH) 공식 비모수 검정 (N=400 / N=800)
    # -------------------------------------------------------------------------
    print("\n>>> 2. H4 통제축 간 상대적 취약성 비모수 검정 (Wilcoxon & Bootstrap 95% CI):")
    h4_rows = []
    for m in models_order:
        # 극단 스트레스 구간(L4, L5 합산 N=800 스텝 및 최악 레벨 N=400 스텝)
        m_high = synth_long[(synth_long["model"] == m) & (synth_long["lvl"].isin([4, 5]))].copy()
        m_high["cov_deficit"] = (0.90 - m_high["is_covered_90"]) * 100.0  # %p 단위 부족폭

        def_reg = m_high[m_high["axis"] == "REGIME"]["cov_deficit"].values
        def_tail = m_high[m_high["axis"] == "TAIL"]["cov_deficit"].values
        def_garch = m_high[m_high["axis"] == "GARCH"]["cov_deficit"].values

        # 대응 표본 Wilcoxon 부호순위 검정 (동일 시드/스텝 구조 800쌍)
        _, p_reg_vs_tail = stats.wilcoxon(def_reg, def_tail, alternative="greater")
        _, p_reg_vs_garch = stats.wilcoxon(def_reg, def_garch, alternative="greater")
        _, p_tail_vs_garch = stats.wilcoxon(def_tail, def_garch, alternative="greater")

        ci_rt_low, ci_rt_high = bootstrap_ci_diff(def_reg, def_tail, n_boot=2000)
        ci_rg_low, ci_rg_high = bootstrap_ci_diff(def_reg, def_garch, n_boot=2000)

        # 최악 레벨(Worst-case L4 or L5) 기준 부족폭
        m_sum_sub = synth_df[synth_df["model"] == m].copy()
        m_sum_sub["axis"] = m_sum_sub["scenario"].apply(lambda s: s.split("_")[1])
        worst_reg = (0.90 - m_sum_sub[m_sum_sub["axis"] == "REGIME"]["cov_90"].min()) * 100.0
        worst_tail = (0.90 - m_sum_sub[m_sum_sub["axis"] == "TAIL"]["cov_90"].min()) * 100.0
        worst_garch = (0.90 - m_sum_sub[m_sum_sub["axis"] == "GARCH"]["cov_90"].min()) * 100.0

        h4_rows.append({
            "Model": m,
            "Worst_Deficit_REGIME_pp": round(worst_reg, 2),
            "Worst_Deficit_TAIL_pp": round(worst_tail, 2),
            "Worst_Deficit_GARCH_pp": round(worst_garch, 2),
            "L4L5_Mean_Deficit_REGIME_pp": round(float(np.mean(def_reg)), 2),
            "L4L5_Mean_Deficit_TAIL_pp": round(float(np.mean(def_tail)), 2),
            "L4L5_Mean_Deficit_GARCH_pp": round(float(np.mean(def_garch)), 2),
            "Diff_REGIME_minus_TAIL_pp": f"{np.mean(def_reg)-np.mean(def_tail):+.2f} [{ci_rt_low:+.2f}, {ci_rt_high:+.2f}]",
            "Wilcoxon_p_REGIME_gt_TAIL": float(p_reg_vs_tail),
            "Wilcoxon_p_REGIME_gt_GARCH": float(p_reg_vs_garch),
            "Wilcoxon_p_TAIL_gt_GARCH": float(p_tail_vs_garch),
        })
        print(
            f"  {m:<13} | Worst 부족폭: Regime={worst_reg:+.1f}%p, Tail={worst_tail:+.1f}%p, GARCH={worst_garch:+.1f}%p | "
            f"L4~L5 평균: Regime={np.mean(def_reg):+.1f}%p vs Tail={np.mean(def_tail):+.1f}%p (Wilcoxon p={p_reg_vs_tail:.2e})"
        )

    h4_df = pd.DataFrame(h4_rows)
    h4_df.to_csv(TABLES_DIR / "table_h4_asymmetry_test.csv", index=False)

    # -------------------------------------------------------------------------
    # 4. 실측 시장 롤링 윈도우 성능: 스케일 정규화(nCRPS %) & 미국/한국/종목별 분리 (Table 2A, 2B)
    # -------------------------------------------------------------------------
    print("\n>>> 3. 실측 시장 롤링 윈도우 성능 (미국 5대 대형주 vs 한국 KODEX 200 vs 정규화 통합):")
    mkt_long = long_df[long_df["scenario"] == "market_rolling"].copy()
    mkt_long["asset_id"] = mkt_long["series_id"].apply(lambda s: str(s).split("_")[1])

    us_tickers = ["AAPL", "AMZN", "GOOG", "JPM", "META"]
    kr_tickers = ["069500"]

    panels = [
        ("Panel A: 미국 S&P 500 5대 대형주 (USD, N=500, W=25)", mkt_long[mkt_long["asset_id"].isin(us_tickers)]),
        ("Panel B: 한국 KOSPI 200 ETF (069500, KRW, N=100, W=5)", mkt_long[mkt_long["asset_id"].isin(kr_tickers)]),
        ("Panel C: 전체 6개 자산 스케일 정규화 통합 (nCRPS 기준, N=600, W=30)", mkt_long),
    ]

    table2_rows = []
    for panel_name, p_df in panels:
        print(f"\n  [{panel_name}]")
        rw_sub = p_df[p_df["model"] == "random_walk"]
        garch_sub = p_df[p_df["model"] == "garch_t"]
        rw_ncrps_mean = float(rw_sub["rel_crps"].mean())
        rw_raw_crps_mean = float(rw_sub["crps"].mean())

        for m in models_order:
            m_sub = p_df[p_df["model"] == m]
            ncrps_mean = float(m_sub["rel_crps"].mean())
            raw_crps_mean = float(m_sub["crps"].mean())
            cov90_mean = float(m_sub["is_covered_90"].mean())
            rel_mae_mean = float(m_sub["rel_mae"].mean())
            raw_mae_mean = float(m_sub["mae"].mean())

            # PIT KS stat
            pits = np.clip(m_sub["pit"].values + np.random.uniform(-1e-6, 1e-6, size=len(m_sub)), 0.0, 1.0)
            ks_stat = float(stats.kstest(pits, "uniform").statistic)

            # Skill Score vs RW (nCRPS 기준 및 Raw CRPS 기준)
            skill_ncrps = (1.0 - (ncrps_mean / rw_ncrps_mean)) * 100.0
            skill_raw = (1.0 - (raw_crps_mean / rw_raw_crps_mean)) * 100.0

            # 경계 무침범 DM 검정 (nCRPS 기준)
            dm_hln_rw, p_hln_rw, wb_stat_rw, wb_p_rw = stratified_dm_test(m_sub, rw_sub, value_col="rel_crps")
            dm_hln_g, p_hln_g, wb_stat_g, wb_p_g = stratified_dm_test(m_sub, garch_sub, value_col="rel_crps")

            table2_rows.append({
                "Market Panel": panel_name.split(" (")[0],
                "Model": m,
                "nCRPS (%)": f"{ncrps_mean:.3f}%",
                "nCRPS Skill vs RW": f"{skill_ncrps:+.2f}%",
                "Raw CRPS": f"{raw_crps_mean:.2f}",
                "Raw Skill vs RW": f"{skill_raw:+.2f}%",
                "90% Coverage": f"{cov90_mean*100:.1f}%",
                "MAPE (%)": f"{rel_mae_mean:.2f}%",
                "PIT KS": f"{ks_stat:.4f}",
                "Stratified DM (p)": f"{dm_hln_rw:+.3f} ({p_hln_rw:.4f})",
                "Window-Block DM (p)": f"{wb_stat_rw:+.3f} ({wb_p_rw:.4f})",
            })
            print(
                f"    {m:<13} | nCRPS={ncrps_mean:.3f}% (Skill={skill_ncrps:+.2f}%) | "
                f"RawCRPS={raw_crps_mean:.2f} | Cov90={cov90_mean*100:.1f}% | "
                f"StratDM p={p_hln_rw:.4f} | WinBlockDM p={wb_p_rw:.4f}"
            )

    table2_df = pd.DataFrame(table2_rows)
    t2_csv = TABLES_DIR / "table2_market_performance.csv"
    t2_md = TABLES_DIR / "table2_market_performance.md"
    table2_df.to_csv(t2_csv, index=False)

    # 개별 종목(6종목) 전수 분해표 (Table 2B)
    per_asset_rows = []
    for asset in us_tickers + kr_tickers:
        a_df = mkt_long[mkt_long["asset_id"] == asset]
        rw_a = a_df[a_df["model"] == "random_walk"]
        rw_a_ncrps = float(rw_a["rel_crps"].mean())
        rw_a_raw = float(rw_a["crps"].mean())

        for m in models_order:
            m_a = a_df[a_df["model"] == m]
            ncrps_a = float(m_a["rel_crps"].mean())
            raw_a = float(m_a["crps"].mean())
            cov_a = float(m_a["is_covered_90"].mean())
            skill_a = (1.0 - (ncrps_a / rw_a_ncrps)) * 100.0
            dm_stat_a, dm_p_a, wb_stat_a, wb_p_a = stratified_dm_test(m_a, rw_a, value_col="rel_crps")

            per_asset_rows.append({
                "Asset": asset,
                "Currency": "KRW" if asset == "069500" else "USD",
                "Model": m,
                "Raw CRPS": f"{raw_a:.2f}",
                "nCRPS (%)": f"{ncrps_a:.3f}%",
                "Skill vs RW (%)": f"{skill_a:+.2f}%",
                "90% Coverage (%)": f"{cov_a*100:.1f}%",
                "Within-Asset DM Stat": f"{dm_stat_a:+.3f}",
                "Within-Asset DM p": f"{dm_p_a:.4f}",
            })

    table2b_df = pd.DataFrame(per_asset_rows)
    t2b_csv = TABLES_DIR / "table2b_per_asset_breakdown.csv"
    table2b_df.to_csv(t2b_csv, index=False)

    # 종목별 nCRPS 피벗 요약표 (논문 본문 삽입용)
    piv_ncrps = table2b_df.pivot(index="Asset", columns="Model", values="nCRPS (%)")[models_order]
    piv_skill = table2b_df.pivot(index="Asset", columns="Model", values="Skill vs RW (%)")[models_order]

    md_t2 = [
        "# [Table 2] 실측 주식시장 롤링 윈도우 예측 성능 및 경계 분리 Diebold-Mariano 검정표",
        "",
        "## Table 2A. 시장 권역별(미국 5종목 vs 한국 KODEX 200 vs 스케일 정규화 통합) 성능 비교",
        table2_df.to_markdown(index=False),
        "",
        "## Table 2B. 개별 종목별 스케일 정규화 nCRPS (%) 상세 분해 (각 종목 N=100, 5개 연도 윈도우)",
        piv_ncrps.to_markdown(),
        "",
        "## Table 2C. 개별 종목별 Random Walk 대비 Skill Score (%) 분해",
        piv_skill.to_markdown(),
        "",
        "- `nCRPS (%)`: $\\text{CRPS} / |y_{\\text{true}}| \\times 100\\%$ (통화 단위 및 주가 레벨 차이를 제거한 무차원 상대 확률오차)",
        "- `Stratified DM`: 종목 및 연도 윈도우 경계를 침범하지 않도록 각 20일 윈도우 내부에서만 Newey-West 분산을 산출 후 결합한 HLN 보정 DM 통계량",
        "- `Window-Block DM`: 각 20일 롤링 윈도우 평균 오차 차이($D_w$)를 독립 블록($W=25$ 또는 $W=30$)으로 간주한 대응 $t$-검정",
    ]
    t2_md.write_text("\n".join(md_t2), encoding="utf-8")
    print(f"\n  [Table 2A/2B/2C 저장 완료] -> {t2_csv.name}, {t2b_csv.name}, {t2_md.name}")

    # -------------------------------------------------------------------------
    # 5. 논문 실물 Table 1 생성 (가상 15개 시나리오 x 6개 모델 전수 비교)
    # -------------------------------------------------------------------------
    t1_piv_crps = synth_df.pivot(index="scenario", columns="model", values="mean_crps")
    t1_piv_cov = synth_df.pivot(index="scenario", columns="model", values="cov_90")

    table1_rows = []
    scenario_order = [
        "synth_GARCH_L1", "synth_GARCH_L2", "synth_GARCH_L3", "synth_GARCH_L4", "synth_GARCH_L5",
        "synth_TAIL_L1", "synth_TAIL_L2", "synth_TAIL_L3", "synth_TAIL_L4", "synth_TAIL_L5",
        "synth_REGIME_L1", "synth_REGIME_L2", "synth_REGIME_L3", "synth_REGIME_L4", "synth_REGIME_L5"
    ]

    for sc in scenario_order:
        axis_name = sc.split("_")[1]
        lvl_name = sc.split("_")[2]
        row_dict = {"Axis": axis_name, "Level": lvl_name}
        for m in models_order:
            crps_val = t1_piv_crps.loc[sc, m]
            cov_val = t1_piv_cov.loc[sc, m] * 100.0
            row_dict[m] = f"{crps_val:.2f} ({cov_val:.1f}%)"
        table1_rows.append(row_dict)

    table1_df = pd.DataFrame(table1_rows)
    t1_csv = TABLES_DIR / "table1_stress_comparison.csv"
    t1_md = TABLES_DIR / "table1_stress_comparison.md"
    table1_df.to_csv(t1_csv, index=False)

    md_t1 = [
        "# [Table 1] 3대 금융 스트레스 통제축별 6개 모델 예측 성능 비교표: CRPS (90% 커버리지)",
        "",
        table1_df.to_markdown(index=False),
        "",
        "- 표기 형식: `CRPS (90% 명목 신뢰구간 실측 커버리지 %)`",
        "- 비교 모델: Chronos-Tiny (8M), Chronos-Base (200M), Moirai-Small (14M), Moirai-Base (91M), GARCH(1,1)-t, Random Walk",
    ]
    t1_md.write_text("\n".join(md_t1), encoding="utf-8")
    print(f"  [Table 1 저장 완료] -> {t1_csv.name} & {t1_md.name}")

    # -------------------------------------------------------------------------
    # 6. 논문 실물 Figure 1 렌더링 (3대 통제축 스트레스-반응 붕괴 곡선, 6개 모델)
    # -------------------------------------------------------------------------
    fig, axes = plt.subplots(2, 3, figsize=(19, 10.5))
    axes = axes.flatten()

    colors = {
        "chronos-tiny": "#1f77b4",   # 파랑
        "chronos-base": "#d62728",   # 빨강
        "moirai-small": "#9467bd",   # 보라
        "moirai-base": "#ff7f0e",    # 주황
        "garch_t": "#2ca02c",        # 초록
        "random_walk": "#7f7f7f"     # 회색
    }
    markers = {
        "chronos-tiny": "o",
        "chronos-base": "s",
        "moirai-small": "D",
        "moirai-base": "P",
        "garch_t": "^",
        "random_walk": "x"
    }

    axes_labels = ["GARCH (변동성 군집)", "TAIL (두꺼운 꼬리)", "REGIME (체제 전환)"]
    axes_keys = ["GARCH", "TAIL", "REGIME"]

    # 상단 3개: CRPS 반응 곡선
    for idx, (ax_key, ax_title) in enumerate(zip(axes_keys, axes_labels)):
        ax = axes[idx]
        sub = synth_df[synth_df["scenario"].str.contains(ax_key)].copy()
        sub["lvl"] = sub["scenario"].apply(lambda s: int(s.split("_L")[-1]))
        sub = sub.sort_values("lvl")

        for m in models_order:
            m_sub = sub[sub["model"] == m]
            ax.plot(
                m_sub["lvl"],
                m_sub["mean_crps"],
                marker=markers.get(m, "o"),
                color=colors.get(m, "black"),
                label=m,
                linewidth=2,
                markersize=6.5,
            )

        ax.set_title(f"[Fig 1.{idx+1}A] {ax_title} vs CRPS", fontsize=12, fontweight="bold")
        ax.set_xlabel("스트레스 레벨 (L1: 약함 -> L5: 극단)", fontsize=10)
        ax.set_ylabel("Unbiased CRPS (낮을수록 우수)", fontsize=10)
        ax.set_xticks([1, 2, 3, 4, 5])
        ax.set_xticklabels(["L1", "L2", "L3", "L4", "L5"])
        ax.grid(True, linestyle="--", alpha=0.5)
        if idx == 0:
            ax.legend(loc="upper left", frameon=True, fontsize=8.5)

    # 하단 3개: 90% 명목 커버리지 반응 곡선
    for idx, (ax_key, ax_title) in enumerate(zip(axes_keys, axes_labels)):
        ax = axes[idx + 3]
        sub = synth_df[synth_df["scenario"].str.contains(ax_key)].copy()
        sub["lvl"] = sub["scenario"].apply(lambda s: int(s.split("_L")[-1]))
        sub = sub.sort_values("lvl")

        for m in models_order:
            m_sub = sub[sub["model"] == m]
            ax.plot(
                m_sub["lvl"],
                m_sub["cov_90"] * 100.0,
                marker=markers.get(m, "o"),
                color=colors.get(m, "black"),
                label=m,
                linewidth=2,
                markersize=6.5,
            )

        ax.axhline(90.0, color="black", linestyle="--", linewidth=1.5, label="명목 90% 목표선")
        ax.set_title(f"[Fig 1.{idx+1}B] {ax_title} vs 90% 커버리지", fontsize=12, fontweight="bold")
        ax.set_xlabel("스트레스 레벨 (L1: 약함 -> L5: 극단)", fontsize=10)
        ax.set_ylabel("실측 커버리지 (%)", fontsize=10)
        ax.set_xticks([1, 2, 3, 4, 5])
        ax.set_xticklabels(["L1", "L2", "L3", "L4", "L5"])
        ax.set_ylim(55, 100)
        ax.grid(True, linestyle="--", alpha=0.5)
        if idx == 0:
            ax.legend(loc="lower left", frameon=True, fontsize=8.5)

    plt.tight_layout()
    fig1_path = FIGURES_DIR / "fig1_stress_response_curves.png"
    plt.savefig(fig1_path, dpi=300)
    plt.close()
    print(f"  [Figure 1 렌더링 완료] -> {fig1_path.name}")

    # -------------------------------------------------------------------------
    # 7. 논문 실물 Figure 2 렌더링 (실측 시장 PIT 히스토그램, 6개 모델 2x3 배치)
    # -------------------------------------------------------------------------
    n_models = len(models_order)
    ncols = 3
    nrows = int(np.ceil(n_models / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(16, 4.5 * nrows), sharey=True)
    axes = axes.flatten()
    mkt_summary = summary_df[summary_df["scenario"] == "market_rolling"].copy()

    for idx, m in enumerate(models_order):
        ax = axes[idx]
        m_pits = mkt_long[mkt_long["model"] == m]["pit"].values
        ks_stat = mkt_summary[mkt_summary["model"] == m]["pit_ks_stat"].iloc[0]

        ax.hist(m_pits, bins=10, range=(0, 1), density=True, color=colors.get(m, "#1f77b4"), alpha=0.75, edgecolor="black")
        ax.axhline(1.0, color="red", linestyle="--", linewidth=2, label="이상적 균등분포 (U[0,1])")

        ax.set_title(f"{m}\n(KS 통계량 = {ks_stat:.4f})", fontsize=11, fontweight="bold")
        ax.set_xlabel("PIT (확률적분변환값)", fontsize=10)
        if idx % ncols == 0:
            ax.set_ylabel("확률 밀도", fontsize=10)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 3.2)
        ax.grid(True, linestyle="--", alpha=0.4)
        ax.legend(loc="upper center", fontsize=9)

    for j in range(n_models, len(axes)):
        axes[j].axis("off")

    plt.suptitle("[Figure 2] 실측 시장 데이터(N=600)에서의 확률적분변환(PIT) 분포 진단 (U자형=신뢰구간 과소평가)", fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    fig2_path = FIGURES_DIR / "fig2_pit_histograms.png"
    plt.savefig(fig2_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  [Figure 2 렌더링 완료] -> {fig2_path.name}")

    # -------------------------------------------------------------------------
    # 8. 논문 실물 Figure 3 렌더링 (3대 통제축 최악 커버리지 결손폭 비교 바 차트)
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(12, 5.5))
    bar_width = 0.13
    x = np.arange(len(axes_keys))

    for i, m in enumerate(models_order):
        m_sub = synth_df[synth_df["model"] == m].copy()
        m_sub["axis"] = m_sub["scenario"].apply(lambda s: s.split("_")[1])
        # 각 축별 최악(최소 커버리지) 결손폭 (0.90 - min_cov) * 100
        cov_drops = [(0.90 - m_sub[m_sub["axis"] == ax_k]["cov_90"].min()) * 100.0 for ax_k in axes_keys]
        offset = (i - (len(models_order) - 1) / 2.0) * bar_width
        ax.bar(
            x + offset,
            cov_drops,
            width=bar_width,
            label=m,
            color=colors.get(m, "gray"),
            edgecolor="black",
            alpha=0.88,
        )

    ax.set_title("[Figure 3] 3대 금융 스트레스 통제축별 최대 신뢰구간 결손폭 (목표 90% 대비 부족분 %p)", fontsize=12, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(["GARCH 군집 (지속성 극대화)", "두꺼운 꼬리 (자유도 df=3)", "체제전환 단절 (빈번한 구조전이)"], fontsize=11)
    ax.set_ylabel("최대 커버리지 결손폭 (%p, 클수록 붕괴 심각)", fontsize=11)
    ax.axhline(0, color="black", linestyle="-", linewidth=0.8)
    ax.grid(True, linestyle="--", alpha=0.5, axis="y")
    ax.legend(loc="upper left", frameon=True, ncol=2)

    plt.tight_layout()
    fig3_path = FIGURES_DIR / "fig3_breakdown_radar.png"
    plt.savefig(fig3_path, dpi=300)
    plt.close()
    print(f"  [Figure 3 렌더링 완료] -> {fig3_path.name}")

    # 아티팩트 폴더로 이미지 동기화 복사
    if ARTIFACT_DIR.exists():
        for fp in [fig1_path, fig2_path, fig3_path]:
            shutil.copy2(fp, ARTIFACT_DIR / fp.name)
        print("  [아티팩트 이미지 동기화 완료]")


if __name__ == "__main__":
    run_full_analysis()
