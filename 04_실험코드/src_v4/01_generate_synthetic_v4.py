# -*- coding: utf-8 -*-
"""
01_generate_synthetic_v4.py — 합성 데이터 17 시나리오 × 100 계열 + 정답 기준선 (계획서 v4 §2)
==========================================================================================
- 공통 난수(CRN): 계열 번호 s마다 기본 난수(z, u, v, s0)를 한 번 뽑아 모든 축·단계가 공유
- 모든 시나리오: 무조건부 평균 0, 무조건부 표준편차 SIGMA(2.11%)
  CL (군집)  : GARCH(1,1), α = 0.1·(α+β), β = 0.9·(α+β), ω = σ²(1−α−β), 정규 충격
  TL (꼬리)  : σ·√((ν−2)/ν)·t_ν,  t_ν = z / √(χ²_ν(v)/ν)
  RF·RS(국면): 2국면(평온·격변), 평균 0, 격변 σ = 변동비 × 평온 σ, 정상분포 기준 분산 = σ²
              평온 이탈확률 1/평온지속일, 격변 이탈확률 1/격변지속일, 첫 상태는 정상분포에서
  L1         : σ·z (네 축의 L1 모수로 만들어도 같은 데이터가 됨을 시작 시 점검)
- 정답 기준선(oracle): 생성 과정을 아는 상태에서 내일 수익률의 참 조건부 0.1~0.9 분위
  CL: σₜ·Φ⁻¹(τ) / TL: σ√((ν−2)/ν)·t⁻¹_ν(τ) / RF·RS: 어제 국면을 알 때 오늘 국면 혼합정규의 분위 / L1: σΦ⁻¹(τ)
출력: data/synthetic_v4/synthetic_v4.parquet (scenario, s, t, r)
      data/synthetic_v4/oracle_v4.parquet   (scenario, s, day 1~80, q1~q9)
      data/synthetic_v4/_manifest.csv        (시나리오 모수, 실현 표준편차·첨도·자기상관)
"""
import argparse

import numpy as np
import pandas as pd
from scipy import optimize, stats

import config_v4 as C

Z_Q = stats.norm.ppf(C.QLEVELS)


def base_draws(s):
    rng = np.random.default_rng(np.random.SeedSequence([C.SEED_BASE, 4, s]))
    z = rng.standard_normal(C.SIM_LEN)
    u = rng.random(C.SIM_LEN)
    v = np.clip(rng.random(C.SIM_LEN), 1e-12, 1 - 1e-12)
    s0 = rng.random()
    return {"z": z, "u": u, "v": v, "s0": s0}


def gen_cluster(ab, d):
    z = d["z"]
    a, b = C.GARCH_ALPHA_SHARE * ab, (1 - C.GARCH_ALPHA_SHARE) * ab
    om = C.SIGMA ** 2 * (1 - ab)
    n = len(z)
    r, s2 = np.empty(n), np.empty(n)
    s2[0] = C.SIGMA ** 2
    r[0] = np.sqrt(s2[0]) * z[0]
    for t in range(1, n):
        s2[t] = om + a * r[t - 1] ** 2 + b * s2[t - 1]
        r[t] = np.sqrt(s2[t]) * z[t]
    oracle = np.sqrt(s2)[:, None] * Z_Q[None, :]
    return r, oracle


def gen_tail(nu, d):
    if np.isinf(nu):
        return C.SIGMA * d["z"], np.tile(C.SIGMA * Z_Q, (len(d["z"]), 1))
    chi = stats.chi2.ppf(d["v"], df=nu)
    t = d["z"] / np.sqrt(chi / nu)
    sc = C.SIGMA * np.sqrt((nu - 2) / nu)
    return sc * t, np.tile(sc * stats.t.ppf(C.QLEVELS, nu), (len(t), 1))


def mix_quantiles(w_calm, s_c, s_t):
    """혼합정규 w·N(0,s_c²)+(1−w)·N(0,s_t²)의 분위수."""
    out = np.empty(len(C.QLEVELS))
    for i, q in enumerate(C.QLEVELS):
        f = lambda x: w_calm * stats.norm.cdf(x / s_c) + (1 - w_calm) * stats.norm.cdf(x / s_t) - q  # noqa: E731
        out[i] = optimize.brentq(f, -20 * s_t, 20 * s_t, xtol=1e-14)
    return out


def gen_regime(par, d):
    """par: {} 이면 전환 없음(σ·z). 아니면 dur_calm, dur_turb, vol_ratio."""
    z, u = d["z"], d["u"]
    n = len(z)
    if not par:
        return C.SIGMA * z, np.tile(C.SIGMA * Z_Q, (n, 1)), np.zeros(n, int)
    dc, dt, k = par["dur_calm"], par["dur_turb"], par["vol_ratio"]
    p_ct, p_tc = 1 / dc, 1 / dt               # 평온→격변, 격변→평온
    assert 0 < p_ct <= 1 and 0 < p_tc <= 1, (dc, dt)
    pi_t = dt / (dc + dt)                     # 정상분포에서 격변 비율
    s_c = C.SIGMA / np.sqrt((1 - pi_t) + pi_t * k ** 2)
    s_t = k * s_c
    st = np.empty(n, int)
    st[0] = 1 if d["s0"] < pi_t else 0
    for t in range(1, n):
        p = p_ct if st[t - 1] == 0 else p_tc
        st[t] = 1 - st[t - 1] if u[t] < p else st[t - 1]
    r = np.where(st == 1, s_t, s_c) * z
    q_after_calm = mix_quantiles(1 - p_ct, s_c, s_t)
    q_after_turb = mix_quantiles(p_tc, s_c, s_t)
    oracle = np.empty((n, len(C.QLEVELS)))
    oracle[0] = mix_quantiles(1 - pi_t, s_c, s_t)
    oracle[1:] = np.where(st[:-1, None] == 0, q_after_calm[None, :], q_after_turb[None, :])
    return r, oracle, st


def generate(name, axis, par, d):
    if axis == "NONE":
        return C.SIGMA * d["z"], np.tile(C.SIGMA * Z_Q, (C.SIM_LEN, 1))
    if axis == "CL":
        return gen_cluster(par["ab"], d)
    if axis == "TL":
        return gen_tail(par["nu"], d)
    r, o, _ = gen_regime(par, d)
    return r, o


def check_l1_identity(draws):
    """네 축의 L1 모수(α+β=0, ν=∞, 전환 없음, 변동비 1)로 만든 데이터가 L1과 같은지 점검."""
    L1p = C.LEVELS["regime_size"]["L4"]
    for s in list(draws)[:5]:
        d = draws[s]
        base = C.SIGMA * d["z"]
        a = gen_cluster(0.0, d)[0]
        b = gen_tail(np.inf, d)[0]
        c = gen_regime({}, d)[0]
        e = gen_regime({"dur_calm": L1p["dur_calm"], "dur_turb": L1p["dur_turb"], "vol_ratio": 1.0}, d)[0]
        for name, x in [("CL α+β=0", a), ("TL ν=∞", b), ("RF 전환 없음", c), ("RS 변동비 1", e)]:
            if not np.allclose(x, base, rtol=0, atol=1e-15):
                raise AssertionError(f"L1 동일성 실패: {name}, s={s}")
    print("[점검] 네 축의 L1 모수로 만든 데이터가 L1과 동일: 통과")


def main(n_series):
    C.DATA_SYN.mkdir(parents=True, exist_ok=True)
    draws = {s: base_draws(s) for s in range(n_series)}
    check_l1_identity(draws)
    rows, orc, man = [], [], []
    for name, axis, lv, par in C.scenarios():
        allr = []
        for s in range(n_series):
            r, o = generate(name, axis, par, draws[s])
            assert r.shape == (C.SIM_LEN,) and np.isfinite(r).all()
            rows.append(pd.DataFrame({"scenario": name, "s": s, "t": np.arange(C.SIM_LEN), "r": r}))
            od = pd.DataFrame(o[C.FIRST_TARGET:C.FIRST_TARGET + C.EP_LEN], columns=[f"q{i+1}" for i in range(9)])
            od.insert(0, "day", np.arange(1, C.EP_LEN + 1))
            od.insert(0, "s", s)
            od.insert(0, "scenario", name)
            orc.append(od)
            allr.append(r[C.WARMUP:])
        x = np.concatenate(allr)
        ac1 = np.mean([np.corrcoef(a[1:] ** 2, a[:-1] ** 2)[0, 1] for a in allr])
        man.append({"scenario": name, "axis": axis, "level": lv, **{f"par_{k}": v for k, v in par.items()},
                    "real_sd": x.std(), "target_sd": C.SIGMA, "real_exkurt": stats.kurtosis(x),
                    "acf1_sq_mean": ac1})
    pd.concat(rows, ignore_index=True).to_parquet(C.DATA_SYN / "synthetic_v4.parquet", index=False)
    pd.concat(orc, ignore_index=True).to_parquet(C.DATA_SYN / "oracle_v4.parquet", index=False)
    m = pd.DataFrame(man)
    m.to_csv(C.DATA_SYN / "_manifest.csv", index=False, encoding="utf-8-sig")
    print(m[["scenario", "real_sd", "real_exkurt", "acf1_sq_mean"]].round(4).to_string(index=False))
    print(f"[저장] {C.DATA_SYN}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n_series", type=int, default=C.N_SERIES)
    main(ap.parse_args().n_series)
