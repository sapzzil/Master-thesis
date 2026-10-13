# -*- coding: utf-8 -*-
"""
k04_estimate_levels.py — v4 준비: 실제 10종목 특성 추정 → 합성 단계값 산출 (계획서 v4 §2-2 규칙)
====================================================================================================
데이터: 미국 5종목 data/raw/us_yf_*.parquet 의 close(분할 반영·배당 미반영),
        한국 5종목 data/raw_v4/kr_fdr_*.parquet 의 close. 기간 2015-01-02 ~ 2026-09-22.
종목별 추정 (일별 로그수익률 ×100):
  - GARCH(1,1)-t, 상수 평균 → α+β (군집 지속성), ν (꼬리)
  - 2국면 마르코프 전환(평균·분산 모두 전환), statsmodels MarkovRegression, 시작값 여러 번
    → 평온(분산 작은 국면)·격변 지속일 = 1/(1-p_ii), 변동비 = σ_격변/σ_평온 (표준편차 비)
  - 일 변동 = 로그수익률 표준편차
단계 규칙 (§2-2):
  L1 = 특성 없음(4축 공통).  L3 = 10종목 중 가장 약한 값, L4 = 중앙값, L5 = 가장 센 값.
  ① 군집: L2 = L3 α+β의 절반.  ② 꼬리: L2 = L3 초과첨도(6/(ν-4))의 절반에 해당하는 ν.
  ③ 빈도: 척도 = 평온 이탈확률 p = 1/평온지속일. L3 = min p, L4 = median p, L5 = 2 × max p, L2 = L3/2.
         격변 지속일 = 평온 지속일 / R (R = 평온/격변 지속일 비의 10종목 중앙값), 변동비 = 중앙값 k.
  ④ 크기: 변동비 L3 = min, L4 = median, L5 = max, L2 = (1 + L3)/2. 지속일 = ③의 L4와 동일(두 축 L4가 같은 설정).
  일 변동 = 10종목 중앙값.
주의: 모델을 돌리지 않는다. 데이터의 성질만 잰다.
출력: data/raw_v4/stylized_facts_10.csv, synthetic_levels_v4.json
"""
import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = DATA / "raw_v4"
START, END = "2015-01-02", "2026-09-22"
US = ["AAPL", "AMZN", "GOOG", "JPM", "META"]
KR = {"005930": "삼성전자", "000660": "SK하이닉스", "005380": "현대차", "015760": "한국전력", "012330": "현대모비스"}


def load():
    out = {}
    for t in US:
        d = pd.read_parquet(DATA / "raw" / f"us_yf_{t}.parquet")
        d = d[d["volume"] > 0]
        out[t] = d["close"]
    for c, n in KR.items():
        d = pd.read_parquet(DATA / "raw_v4" / f"kr_fdr_{c}.parquet")
        d = d[d["volume"] > 0]            # 거래정지일(거래량 0) 제외: 삼성전자 2018-04-30~05-03 액면분할 정지 3일
        out[f"{c} {n}"] = d["close"]
    rets = {}
    for k, p in out.items():
        p = p.astype(float).loc[START:END]
        p = p[p > 0].dropna()
        rets[k] = np.log(p).diff().dropna()
    return rets


def fit_garch(r):
    from arch import arch_model
    res = arch_model(r * 100, mean="Constant", vol="GARCH", p=1, q=1, dist="t", rescale=False).fit(disp="off")
    a, b, nu = res.params["alpha[1]"], res.params["beta[1]"], res.params["nu"]
    return {"alpha": a, "beta": b, "ab": a + b, "nu": nu, "garch_conv": int(res.convergence_flag)}


MIN_SIG_FRAC = 0.25   # 국면 표준편차가 표본 표준편차의 25% 미만이면 퇴화해(가격 단위 탓의 0 수익률 몰림)로 보고 버림


def fit_ms(r, seeds=30):
    """2국면 마르코프 전환. 여러 시작값 중 퇴화하지 않은 해 가운데 로그우도 최대를 고른다."""
    from statsmodels.tsa.regime_switching.markov_regression import MarkovRegression
    y = (r * 100).values
    v = y.var()
    mod = MarkovRegression(y, k_regimes=2, trend="c", switching_variance=True)
    names = mod.param_names          # p[0->0], p[1->0], const[0], const[1], sigma2[0], sigma2[1]
    rng = np.random.default_rng(0)
    fits, n_degenerate = [], 0
    for i in range(seeds):
        p00 = rng.uniform(0.90, 0.995)
        p10 = rng.uniform(0.02, 0.20)
        lo, hi = rng.uniform(0.3, 0.8), rng.uniform(2.0, 6.0)
        sp = np.array([p00, p10, 0.05, -0.05, v * lo, v * hi])
        try:
            res = mod.fit(start_params=sp, disp=False, maxiter=1000)
        except Exception:  # noqa: BLE001
            continue
        g = dict(zip(names, res.params))
        s2 = np.array([g["sigma2[0]"], g["sigma2[1]"]])
        if not np.isfinite(res.llf) or np.sqrt(s2.min()) < MIN_SIG_FRAC * np.sqrt(v):
            n_degenerate += 1
            continue
        fits.append((res.llf, res, s2))
    if not fits:
        raise RuntimeError("퇴화하지 않은 해 없음")
    llf, best, s2 = max(fits, key=lambda t: t[0])
    P = best.regime_transition[:, :, 0]   # P[i, j] = Pr(S_t = i | S_{t-1} = j)
    stay = np.array([P[0, 0], P[1, 1]])
    calm, turb = (0, 1) if s2[0] < s2[1] else (1, 0)
    d_calm, d_turb = 1 / (1 - stay[calm]), 1 / (1 - stay[turb])
    return {"ms_llf": llf, "ms_ok_fits": len(fits), "ms_degenerate_fits": n_degenerate,
            "dur_calm": d_calm, "dur_turb": d_turb,
            "p_exit_calm": 1 - stay[calm], "vol_ratio": float(np.sqrt(s2[turb] / s2[calm])),
            "sigma_calm_pct": float(np.sqrt(s2[calm])), "sigma_turb_pct": float(np.sqrt(s2[turb]))}


def main():
    rets = load()
    rows = []
    for k, r in rets.items():
        row = {"asset": k, "n": len(r), "first": str(r.index.min().date()), "last": str(r.index.max().date()),
               "daily_vol": r.std(), "zero_ret_days": int((r == 0).sum()), "exkurt_sample": r.kurt()}
        row.update(fit_garch(r))
        row.update(fit_ms(r))
        rows.append(row)
        print({kk: (round(v, 4) if isinstance(v, float) else v) for kk, v in row.items()}, flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "stylized_facts_10.csv", index=False, encoding="utf-8-sig")

    med = df.median(numeric_only=True)
    # ① 군집
    ab3, ab4, ab5 = df["ab"].min(), med["ab"], df["ab"].max()
    # ② 꼬리
    nu3, nu4, nu5 = df["nu"].max(), med["nu"], df["nu"].min()
    k3 = 6 / (nu3 - 4)
    nu2 = 4 + 6 / (k3 / 2)
    # ③ 빈도
    R = float((df["dur_calm"] / df["dur_turb"]).median())
    kmed = float(med["vol_ratio"])
    p3, p4, p5max = df["p_exit_calm"].min(), med["p_exit_calm"], df["p_exit_calm"].max()
    freq = {"L2": p3 / 2, "L3": p3, "L4": p4, "L5": 2 * p5max}
    freq_levels = {L: {"dur_calm": 1 / p, "dur_turb": (1 / p) / R, "vol_ratio": kmed} for L, p in freq.items()}
    # ④ 크기
    v3, v4, v5 = df["vol_ratio"].min(), kmed, df["vol_ratio"].max()
    dc4, dt4 = freq_levels["L4"]["dur_calm"], freq_levels["L4"]["dur_turb"]
    size_levels = {L: {"dur_calm": dc4, "dur_turb": dt4, "vol_ratio": v}
                   for L, v in {"L2": (1 + v3) / 2, "L3": v3, "L4": v4, "L5": v5}.items()}
    levels = {
        "daily_vol": float(med["daily_vol"]),
        "duration_ratio_R": R,
        "L1": {"ab": 0.0, "nu": "inf", "regime": "none", "vol_ratio": 1.0},
        "cluster_ab": {"L2": ab3 / 2, "L3": ab3, "L4": ab4, "L5": ab5, "alpha_beta_split": "1:9"},
        "tail_nu": {"L2": nu2, "L3": nu3, "L4": nu4, "L5": nu5},
        "regime_freq": freq_levels,
        "regime_size": size_levels,
    }
    levels = json.loads(json.dumps(levels, default=float))
    (OUT / "synthetic_levels_v4.json").write_text(json.dumps(levels, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(levels, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
