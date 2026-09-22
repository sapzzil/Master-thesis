# -*- coding: utf-8 -*-
"""
01_generate_finstress_3axis.py
==============================
학위논문 제5단계: FinStressTS 기반 핵심 3대 통제축 가상 합성 데이터 생성기

[3대 통제축 및 Ceteris Paribus(분산 일정 통제) 원칙]
1. 축 1: GARCH(1,1) 변동성 군집 (alpha + beta in [0.30, 0.60, 0.85, 0.95, 0.98])
   - 무조건부 분산 sigma_0^2 = 0.0001(일별 1%) 고정: omega = sigma_0^2 * (1 - alpha - beta)
   - alpha : beta = 1 : 9 비율 고정
2. 축 2: Student-t 두꺼운 꼬리 (nu in [30.0, 10.0, 5.0, 3.5, 2.5])
   - 표준화 스케일링 계수 sqrt((nu - 2) / nu) 적용하여 분산을 sigma_0^2로 엄격히 고정
3. 축 3: 마르코프 체제전환 (대칭 전이확률 p in [0.02, 0.05, 0.10, 0.20, 0.35])
   - 상태 1(저변동/상승): mu_1 = +0.0005, sigma_1 = 0.008
   - 상태 2(고변동/위기): mu_2 = -0.0020, sigma_2 = 0.030

출력: 04_실험코드/data/synthetic/{axis}_{level}.parquet
      각 시나리오당 n_series개 독립 시계열 (기본 100개, 스모크 2개)
"""

import argparse
import sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]  # 04_실험코드/
OUT_DIR = ROOT / "data" / "synthetic"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------------------
# 파라미터 그리드 정의 (FinStressTS 및 계량경제학 문헌 기반)
# -------------------------------------------------------------------------
SIGMA_0 = 0.01  # 일별 기본 변동성 1% (무조건부 표준편차)
SIGMA_0_SQ = SIGMA_0 ** 2  # 0.0001

GARCH_LEVELS = {
    "L1": 0.30,  # 군집 거의 없음 (비금융/거시 시계열)
    "L2": 0.60,  # 약한 군집
    "L3": 0.85,  # 정상 주식 시장 표준 (Bollerslev 1986)
    "L4": 0.95,  # 강한 위기 국면
    "L5": 0.98,  # 금융위기급 극단적 지속성
}

TAIL_LEVELS = {
    "L1": 30.0,  # 정규분포에 수렴
    "L2": 10.0,  # 완만한 꼬리
    "L3": 5.0,   # 일반 일별 주식 수익률 표준
    "L4": 3.5,   # 극단치 빈발 구역
    "L5": 2.5,   # 4차 모멘트(첨도) 발산 임계치
}

REGIME_LEVELS = {
    "L1": 0.02,  # 평균 지속 기간 50영업일 (분기별 안정)
    "L2": 0.05,  # 평균 지속 기간 20영업일 (월별 경기 사이클)
    "L3": 0.10,  # 평균 지속 기간 10영업일 (격주 변동)
    "L4": 0.20,  # 평균 지속 기간 5영업일 (주간 잦은 반전)
    "L5": 0.35,  # 평균 지속 기간 2.8영업일 (초단기 휩소/극심한 혼란)
}


# -------------------------------------------------------------------------
# 1. GARCH(1,1) 변동성 군집 생성기
# -------------------------------------------------------------------------
def generate_garch_series(persistence, total_len, seed, burn_in=200):
    """
    무조건부 분산 sigma_0^2를 고정한 상태에서 GARCH(1,1) 시뮬레이션
    sigma_t^2 = omega + alpha * r_{t-1}^2 + beta * sigma_{t-1}^2
    omega = sigma_0^2 * (1 - persistence)
    """
    rng = np.random.default_rng(seed)
    sim_len = total_len + burn_in

    alpha = 0.10 * persistence
    beta = 0.90 * persistence
    omega = SIGMA_0_SQ * (1.0 - persistence)

    r = np.zeros(sim_len)
    sigma2 = np.zeros(sim_len)
    sigma2[0] = SIGMA_0_SQ
    z = rng.standard_normal(sim_len)
    r[0] = np.sqrt(sigma2[0]) * z[0]

    for t in range(1, sim_len):
        sigma2[t] = omega + alpha * (r[t - 1] ** 2) + beta * sigma2[t - 1]
        r[t] = np.sqrt(sigma2[t]) * z[t]

    r_final = r[burn_in:]
    # 누적 가격 레벨 (P_0 = 100.0)
    price = 100.0 * np.exp(np.cumsum(r_final))
    return r_final, price


# -------------------------------------------------------------------------
# 2. Student-t 두꺼운 꼬리 생성기 (표준화 스케일링)
# -------------------------------------------------------------------------
def generate_tail_series(nu, total_len, seed, burn_in=200):
    """
    표준화 스케일링 sqrt((nu-2)/nu)을 적용하여 분산을 SIGMA_0_SQ로 고정한 Student-t 시뮬레이션
    """
    rng = np.random.default_rng(seed)
    sim_len = total_len + burn_in

    # 표준화 계수: Var(t_nu) = nu / (nu - 2) 이므로 곱해주면 Var = 1.0
    scale_factor = np.sqrt((nu - 2.0) / nu)
    t_samples = rng.standard_t(df=nu, size=sim_len)
    r = SIGMA_0 * scale_factor * t_samples

    r_final = r[burn_in:]
    price = 100.0 * np.exp(np.cumsum(r_final))
    return r_final, price


# -------------------------------------------------------------------------
# 3. 마르코프 체제전환 생성기 (2-State Markov Switching)
# -------------------------------------------------------------------------
def generate_regime_series(p_trans, total_len, seed, burn_in=200):
    """
    2상태 마르코프 체제전환 시뮬레이션
    상태 1: mu=0.0005, sigma=0.008 (저변동 상승)
    상태 2: mu=-0.0020, sigma=0.030 (고변동 폭락)
    """
    rng = np.random.default_rng(seed)
    sim_len = total_len + burn_in

    mu = [0.0005, -0.0020]
    sigma = [0.008, 0.030]

    states = np.zeros(sim_len, dtype=int)
    states[0] = 0 if rng.random() < 0.5 else 1

    for t in range(1, sim_len):
        curr_state = states[t - 1]
        # p_trans 확률로 반대 상태로 전이
        if rng.random() < p_trans:
            states[t] = 1 - curr_state
        else:
            states[t] = curr_state

    z = rng.standard_normal(sim_len)
    r = np.array([mu[states[t]] + sigma[states[t]] * z[t] for t in range(sim_len)])

    r_final = r[burn_in:]
    price = 100.0 * np.exp(np.cumsum(r_final))
    return r_final, price


# -------------------------------------------------------------------------
# 전체 시나리오 생성 및 Parquet 저장
# -------------------------------------------------------------------------
def generate_all_scenarios(n_series=100, context_len=512, horizon=20, seed_base=42):
    total_len = context_len + horizon
    print(f"[FinStressTS 합성 데이터 생성 시작]")
    print(f"  시계열 길이: {total_len} (컨텍스트 {context_len} + 예측지평 {horizon})")
    print(f"  시나리오당 시계열 수: {n_series}개 (총 3축 x 5레벨 = 15개 시나리오, 총 {15 * n_series}개)")
    print(f"  저장 경로: {OUT_DIR}\n")

    summary_records = []

    axes = [
        ("GARCH", GARCH_LEVELS, generate_garch_series),
        ("TAIL", TAIL_LEVELS, generate_tail_series),
        ("REGIME", REGIME_LEVELS, generate_regime_series),
    ]

    for axis_name, level_dict, gen_func in axes:
        for level_name, param_val in level_dict.items():
            scenario_id = f"{axis_name}_{level_name}"
            rows = []

            for s_idx in range(n_series):
                seed = seed_base + s_idx * 100 + int(param_val * 1000)
                r_series, price_series = gen_func(param_val, total_len, seed)

                series_id = f"{scenario_id}_s{s_idx:03d}"
                for t in range(total_len):
                    rows.append({
                        "series_id": series_id,
                        "axis": axis_name,
                        "level": level_name,
                        "param_value": param_val,
                        "step": t,
                        "is_context": t < context_len,
                        "return": r_series[t],
                        "price": price_series[t],
                    })

            df = pd.DataFrame(rows)
            out_path = OUT_DIR / f"{scenario_id}.parquet"
            df.to_parquet(out_path, index=False)
            print(f"  [OK] {scenario_id:<12} (파라미터={param_val:<6}) -> {out_path.name} ({len(df)}행)")

            summary_records.append({
                "axis": axis_name,
                "level": level_name,
                "param_value": param_val,
                "n_series": n_series,
                "total_rows": len(df),
                "file": out_path.name
            })

    summary_df = pd.DataFrame(summary_records)
    summary_df.to_csv(OUT_DIR / "_manifest.csv", index=False)
    print(f"\n[합성 데이터 생성 완료] 15개 시나리오 manifest 저장 완료: {OUT_DIR / '_manifest.csv'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FinStressTS 3-Axis Synthetic Data Generator")
    parser.add_argument("--n_series", type=int, default=100, help="Number of series per scenario (default: 100)")
    parser.add_argument("--smoke", action="store_true", help="Run in smoke test mode (2 series per scenario)")
    args = parser.parse_args()

    n_series = 2 if args.smoke else args.n_series
    generate_all_scenarios(n_series=n_series)
