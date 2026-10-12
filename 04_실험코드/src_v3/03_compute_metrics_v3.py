# -*- coding: utf-8 -*-
"""
03_compute_metrics_v3.py — 스텝 단위 지표 산출 (v3)
====================================================
지표 정의는 v2와 동일(불편 CRPS, nCRPS=CRPS/|y|x100, 90%/50% 구간 포함 여부, PIT).
v2 대비 변경: 벡터화, 클러스터 식별자 컬럼 추가(axis, level, s_idx / ticker, k, origin),
             요약 집계는 하지 않음(집계·검정은 07에서 클러스터 단위로).
출력: results_v3/metrics_long.parquet
"""
import argparse
import numpy as np
import pandas as pd

import config_v3 as C


def crps_unbiased(S, y):
    """S: (n, m) 표본, y: (n,) 관측. Zamo & Naveau(2018) 불편추정."""
    n, m = S.shape
    t1 = np.mean(np.abs(S - y[:, None]), axis=1)
    Ss = np.sort(S, axis=1)
    w = 2.0 * np.arange(1, m + 1) - m - 1
    sum_pairs = 2.0 * (Ss * w[None, :]).sum(axis=1)          # sum_{i,j}|x_i - x_j|
    t2 = sum_pairs / (2.0 * m * (m - 1))
    return t1 - t2


def ids(df, scenario):
    sid = df["series_id"].astype(str)
    if scenario.startswith("synth_"):
        p = sid.str.split("_", expand=True)
        df["axis"], df["level"] = p[0], p[1]
        df["s_idx"] = p[2].str[1:].astype(int)
        df["ticker"], df["k"] = "SYNTH", -1
    else:
        p = sid.str.split("_", expand=True)
        df["axis"], df["level"], df["s_idx"] = "MARKET", "NA", -1
        df["ticker"] = p[1]
        df["k"] = p[2].str[1:].astype(int)
    return df


def main(res_dir):
    raw = res_dir / "raw_forecasts"
    win = pd.read_csv(res_dir / "market_windows.csv", dtype={"ticker": str}) if (res_dir / "market_windows.csv").exists() else None
    out = []
    for f in sorted(raw.glob("*.parquet")):
        df = pd.read_parquet(f)
        cols = [c for c in df.columns if c.startswith("s_")]
        S = df[cols].to_numpy(float)
        y = df["y_true"].to_numpy(float)
        den = np.maximum(np.abs(y), 1e-8)
        q = np.percentile(S, [5, 25, 75, 95], axis=1)
        crps = crps_unbiased(S, y)
        o = pd.DataFrame({
            "model": df["model"], "scenario": df["scenario"], "series_id": df["series_id"],
            "step_h": df["step_h"], "y_true": y,
            "crps": crps, "rel_crps": crps / den * 100.0,
            "q05": q[0], "q95": q[3],
            "cov90": ((q[0] <= y) & (y <= q[3])).astype(int),
            "cov50": ((q[1] <= y) & (y <= q[2])).astype(int),
            "width90": q[3] - q[0], "rel_width90": (q[3] - q[0]) / den * 100.0,
            "pit": (S <= y[:, None]).mean(axis=1),
        })
        o = ids(o, str(df["scenario"].iloc[0]))
        out.append(o)
        print(f"  {f.name}: {len(o)}행")
    long = pd.concat(out, ignore_index=True)
    if win is not None:
        w = win[win["used"]].copy()
        w["scenario"] = np.where(w["set"] == "panel", "market_panel", "market_stream")
        w = w[["scenario", "ticker", "k", "origin"]].astype({"ticker": str})
        long = long.merge(w, on=["scenario", "ticker", "k"], how="left")
    long.to_parquet(res_dir / "metrics_long.parquet", index=False)
    print(f"[저장] metrics_long.parquet {len(long)}행")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    main(C.ROOT / ("results_v3_smoke" if a.smoke else "results_v3"))
