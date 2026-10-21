# -*- coding: utf-8 -*-
"""
post_g1_axis_v4.py — g1(Chronos-2 극단 분위수) 결과 분석 (CPU). post_checks3_v4.py run 이후 실행.
합성 데이터에서 각 축의 L5−L1 커버리지 변화를 80%·90%·98% 구간별로 계산한다.
계열(100개) 단위 커버리지의 대응 차이에 Wilcoxon 부호순위 검정(양측), 같은 구간·축 안에서 4개 조건 Holm 보정.
비교용으로 분산이 같은 정규분포 기반 구간을 표준화 t분포 자료에 적용했을 때의 이론 커버리지도 출력한다.
출력: results_v4_post/g1_axis.csv, g1_real.csv
"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "results_v4_post" / "raw"
OUT = ROOT / "results_v4_post"
IV = {"80": ("p10", "p90"), "90": ("p05", "p95"), "98": ("p01", "p99")}
NU = {"L2": 11.28, "L3": 7.64, "L4": 4.39, "L5": 3.56}


def holm(p):
    p = np.asarray(p, float)
    o = np.argsort(p)
    adj, cur = np.empty(len(p)), 0.0
    for r, i in enumerate(o):
        cur = max(cur, (len(p) - r) * p[i])
        adj[i] = min(1.0, cur)
    return adj


def main():
    rows, real = [], []
    for L in (21, 252):
        for k in ("return", "price"):
            d = pd.read_parquet(RAW / f"g1__chronos2__L{L}_{k}__synth.parquet")
            d = d[d["in_main"] & (d["day"] > 20)].copy()
            r = pd.read_parquet(RAW / f"g1__chronos2__L{L}_{k}__real.parquet")
            r = r[r["in_main"] & (r["day"] > 20)]
            for lv, (a, b) in IV.items():
                d["c"] = ((d["y"] >= d[a]) & (d["y"] <= d[b])).astype(float)
                s = d.groupby(["scenario", "unit"])["c"].mean().unstack("scenario")
                for ax in ["CL", "TL", "RF", "RS"]:
                    x = s[f"{ax}_L5"] - s["L1"]
                    p = stats.wilcoxon(x).pvalue if (x != 0).any() else 1.0
                    rows.append({"L": L, "input": k, "level": lv, "axis": ax, "cov_L1": s["L1"].mean() * 100,
                                 "cov_L5": s[f"{ax}_L5"].mean() * 100, "diff": x.mean() * 100, "p": p})
                real.append({"L": L, "input": k, "level": lv,
                             "cov_real": ((r["y"] >= r[a]) & (r["y"] <= r[b])).mean() * 100, "n": len(r)})
    t = pd.DataFrame(rows)
    t["p_holm"] = t.groupby(["level", "axis"])["p"].transform(holm)
    t.to_csv(OUT / "g1_axis.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(real).to_csv(OUT / "g1_real.csv", index=False, encoding="utf-8-sig")
    pd.set_option("display.width", 200)
    print(t.round(3).to_string(index=False))
    print(pd.DataFrame(real).round(2).to_string(index=False))
    print("[이론] 분산이 같은 정규 구간을 t 자료에 적용 (80/90/98%)")
    for lv, nu in NU.items():
        sc = np.sqrt((nu - 2) / nu)
        cov = [(2 * stats.t.cdf(stats.norm.ppf(0.5 + c / 2) / sc, nu) - 1) * 100 for c in (0.8, 0.9, 0.98)]
        print(lv, nu, [round(v, 1) for v in cov])


if __name__ == "__main__":
    main()
