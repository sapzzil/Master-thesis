# -*- coding: utf-8 -*-
"""
post_b4_garch_v4.py — 추가 점검 b4 (CPU, 새 예측 없음): 실제 주식에서 TSFM과 RW의 분위수 손실을 GARCH-t(1년)와 비교.
본문 H5(T7: TSFM 대 같은 과거 길이 RW)와 같은 방법 — 같은 종목·날짜로 짝지은 손실 차이의 달력 월 평균에 t검정(양측),
TSFM 1년 4개 조건 × 입력 2개 = 8개를 Holm 보정. 같은 정보(과거 252일)를 쓰는 비교만 한다.
입력: results_v4_t5fix/scored_v4.parquet (git 제외) / 출력: results_v4_post/b4_vs_garch.csv
"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
S = ROOT / "results_v4_t5fix" / "scored_v4.parquet"
OUT = ROOT / "results_v4_post" / "b4_vs_garch.csv"


def holm(p):
    p = np.asarray(p, float)
    o, adj, cur = np.argsort(p), np.empty(len(p)), 0.0
    for r, i in enumerate(o):
        cur = max(cur, (len(p) - r) * p[i])
        adj[i] = min(1.0, cur)
    return adj


def main():
    cols = ["dataset", "model", "L", "input", "unit", "date", "ql", "scored"]
    d = pd.read_parquet(S, columns=cols)
    s = d[(d["dataset"] == "real") & d["scored"] & (d["L"] == 252)].copy()
    s["month"] = pd.to_datetime(s["date"]).dt.to_period("M").astype(str)
    key = ["unit", "date"]
    g = s[s["model"] == "garch_t"].set_index(key)[["ql"]]
    rows = []
    for (m, k), a in s[s["model"] != "garch_t"].groupby(["model", "input"]):
        a = a.set_index(key)
        j = a[["ql", "month"]].join(g, rsuffix="_g", how="inner").dropna()
        D = (j["ql"] - j["ql_g"]).groupby(j["month"]).mean()
        rows.append({"model": m, "L": 252, "input": k, "n": len(j), "months": len(D),
                     "impr_vs_garch": 1 - j["ql"].sum() / j["ql_g"].sum(),
                     "p": float(stats.ttest_1samp(D.values, 0.0).pvalue)})
    t = pd.DataFrame(rows)
    m = t["model"] != "rw"
    t["p_holm"] = np.nan
    t.loc[m, "p_holm"] = holm(t.loc[m, "p"].values)
    t.to_csv(OUT, index=False, encoding="utf-8-sig")
    pd.set_option("display.width", 200)
    print(t.round(4).to_string(index=False))


if __name__ == "__main__":
    main()
