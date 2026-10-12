# -*- coding: utf-8 -*-
"""
01_generate_synthetic_v3.py — 3축 합성 데이터 생성 (v3, 사전등록판)
=====================================================================
v2 대비 변경
  1) 공통 난수(CRN): 시계열 번호 s마다 기본 난수(z, u, v, s0)를 한 번 뽑고
     모든 축·모든 레벨이 같은 기본 난수를 쓴다. → 축 간·레벨 간 '시계열 단위 대응 검정'이 정당해짐.
     (v2는 seed = 42 + 100*s + int(1000*param) 이라 레벨 간 시드가 우연히 겹쳤음)
  2) REGIME 축도 무조건부 평균 0, 분산 1e-4로 고정 (v2는 약 4.7e-4)
  3) 시나리오당 시계열 100개 (v2: 20개)
  4) Student-t는 z / sqrt(chi2_nu(v)/nu) 로 생성 → 자유도가 달라도 같은 z, v 사용

출력: data/synthetic_v3/{AXIS}_{Lk}.parquet, _manifest.csv, _realized_moments.csv
"""
import argparse
import numpy as np
import pandas as pd
from scipy import stats

import config_v3 as C


def base_draws(s_idx, sim_len):
    """시계열 번호 s의 기본 난수. 모든 축·레벨이 공유한다."""
    rng = np.random.default_rng(np.random.SeedSequence([C.SEED_BASE, s_idx]))
    z = rng.standard_normal(sim_len)          # 공통 정규 충격
    u = rng.random(sim_len)                   # 체제 전이용 균등난수
    v = rng.random(sim_len)                   # Student-t 카이제곱 성분용 균등난수
    s0 = rng.random()                         # 체제 초기상태
    v = np.clip(v, 1e-12, 1.0 - 1e-12)
    return z, u, v, s0


def gen_garch(persistence, d):
    z = d["z"]
    n = len(z)
    a = C.GARCH_ALPHA_SHARE * persistence
    b = (1.0 - C.GARCH_ALPHA_SHARE) * persistence
    omega = C.SIGMA_UNC_SQ * (1.0 - persistence)
    r = np.empty(n)
    s2 = C.SIGMA_UNC_SQ
    r[0] = np.sqrt(s2) * z[0]
    for t in range(1, n):
        s2 = omega + a * r[t - 1] ** 2 + b * s2
        r[t] = np.sqrt(s2) * z[t]
    return r


def gen_tail(nu, d):
    chi = stats.chi2.ppf(d["v"], df=nu)
    t = d["z"] / np.sqrt(chi / nu)                 # 정확한 t_nu
    return C.SIGMA_UNC * np.sqrt((nu - 2.0) / nu) * t


def gen_regime(p, d):
    z, u = d["z"], d["u"]
    n = len(z)
    st = np.empty(n, dtype=int)
    st[0] = 0 if d["s0"] < 0.5 else 1
    for t in range(1, n):
        st[t] = 1 - st[t - 1] if u[t] < p else st[t - 1]
    mu = np.array(C.REGIME_MU)[st]
    sg = np.array(C.REGIME_SIGMA)[st]
    return mu + sg * z


GEN = {"GARCH": gen_garch, "TAIL": gen_tail, "REGIME": gen_regime}


def main(n_series):
    C.DATA_SYN.mkdir(parents=True, exist_ok=True)
    total = C.CONTEXT_LEN + C.HORIZON
    sim_len = total + C.BURN_IN
    draws = {}
    for s in range(n_series):
        z, u, v, s0 = base_draws(s, sim_len)
        draws[s] = {"z": z, "u": u, "v": v, "s0": s0}

    man, mom = [], []
    for axis, levels in C.AXES.items():
        for lvl, param in levels.items():
            sid_list, rows_r = [], []
            frames = []
            for s in range(n_series):
                r = GEN[axis](param, draws[s])[C.BURN_IN:]
                price = C.P0 * np.exp(np.cumsum(r))
                frames.append(pd.DataFrame({
                    "series_id": f"{axis}_{lvl}_s{s:03d}",
                    "s_idx": s,
                    "axis": axis, "level": lvl, "param_value": param,
                    "step": np.arange(total),
                    "is_context": np.arange(total) < C.CONTEXT_LEN,
                    "return": r, "price": price,
                }))
                rows_r.append(r)
            df = pd.concat(frames, ignore_index=True)
            out = C.DATA_SYN / f"{axis}_{lvl}.parquet"
            df.to_parquet(out, index=False)
            allr = np.concatenate(rows_r)
            man.append({"axis": axis, "level": lvl, "param_value": param,
                        "n_series": n_series, "total_rows": len(df), "file": out.name})
            mom.append({"axis": axis, "level": lvl, "param_value": param,
                        "realized_mean": allr.mean(), "realized_var": allr.var(),
                        "target_var": C.SIGMA_UNC_SQ})
            print(f"[OK] {axis}_{lvl} param={param} var={allr.var():.3e}")
    pd.DataFrame(man).to_csv(C.DATA_SYN / "_manifest.csv", index=False)
    pd.DataFrame(mom).to_csv(C.DATA_SYN / "_realized_moments.csv", index=False)
    print(f"REGIME scale c={C.REGIME_SCALE:.5f}, sigma={C.REGIME_SIGMA}, mu={C.REGIME_MU}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n_series", type=int, default=C.N_SERIES)
    a = ap.parse_args()
    main(a.n_series)
