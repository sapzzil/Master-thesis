# -*- coding: utf-8 -*-
"""
05_calibrate_v3.py — 무재학습 사후보정 (v3, 설정 동결판)
=========================================================
알고리즘과 하이퍼파라미터는 v2(05_conformal_calibrator.py)와 동일하며 config_v3에 동결:
  Step1 Quantile-Index ACI, Step2 Scale-Normalized ACI-CQR (M0=20, gamma=0.05, alpha=0.10)
v2 대비 변경(구현 버그 수정, 설계 변경 아님)
  1) v2는 market 시계열의 그룹키가 'market' 하나로 잡혀 6개 자산이 단일 스트림으로 처리됐고,
     자산 내 윈도우가 최신→과거 순서로 처리됐다. v3는 자산별·시간순으로 처리한다.
  2) 동일폭 대조군의 폭 배율을 상대폭(폭/|y|) 기준으로 계산 (통화 혼합 시 KRW 지배 방지)
  3) 집계·검정은 하지 않고 스텝 단위 구간을 저장 → 07에서 클러스터 단위 검정
에피소드(보정 상태 리셋 단위)
  synth_*       : 시계열마다
  market_panel  : 윈도우마다 (주분석)
  market_stream : 자산마다, 윈도우 w0→w4(과거→최근) 연속 (보조분석)
출력: results_v3/calibrated_long.parquet
"""
import argparse
import numpy as np
import pandas as pd

import config_v3 as C


def episodes(df, scenario):
    if scenario == "market_stream":
        df = df.assign(_ep=df["series_id"].str.split("_").str[1],
                       _w=df["series_id"].str.split("_").str[2].str[1:].astype(int))
        df = df.sort_values(["_ep", "_w", "step_h"])
    else:
        df = df.assign(_ep=df["series_id"]).sort_values(["series_id", "step_h"])
    return df


def calibrate_file(f):
    df = pd.read_parquet(f)
    scen = str(df["scenario"].iloc[0])
    cols = [c for c in df.columns if c.startswith("s_")]
    df = episodes(df, scen)
    a_nom, g = C.ACI_ALPHA, C.ACI_GAMMA
    lo_c, hi_c = C.ACI_CLIP
    strat = np.linspace(0, C.NUM_SAMPLES - 1, C.CQR_M0).astype(int)
    out = []
    for ep, e in df.groupby("_ep", sort=False):
        S = e[cols].to_numpy(float)
        y = e["y_true"].to_numpy(float)
        sid = e["series_id"].to_numpy()
        a_q = a_nom                      # Step1 상태 (v2와 동일하게 윈도우=series_id 단위로 리셋)
        a_c = a_nom                      # Step2 상태 (에피소드 단위)
        q5_0, q95_0 = np.percentile(S[0], 5), np.percentile(S[0], 95)
        w0 = max(q95_0 - q5_0, 1e-6)
        hist = list(np.sort(np.maximum(q5_0 - S[0], S[0] - q95_0) / w0)[strat])
        prev_sid = None
        for t in range(len(y)):
            if sid[t] != prev_sid:        # Step1은 v2와 같이 series_id마다 리셋
                a_q = a_nom
                prev_sid = sid[t]
            s = S[t]
            ql, qh = np.percentile(s, 5), np.percentile(s, 95)
            w = max(qh - ql, 1e-6)
            # Step1
            pl = max(C.QACI_PCT_CLIP[0], a_q / 2 * 100)
            ph = min(C.QACI_PCT_CLIP[1], (1 - a_q / 2) * 100)
            al, ah = np.percentile(s, pl), np.percentile(s, ph)
            in_a = al <= y[t] <= ah
            a_q = float(np.clip(a_q + g * (a_nom - (0 if in_a else 1)), lo_c, hi_c))
            # Step2
            lev = float(np.clip((1 - a_c) * 100, *C.CQR_QLEVEL_CLIP))
            m = float(np.percentile(hist, lev)) * w
            cl, ch = ql - m, qh + m
            in_c = cl <= y[t] <= ch
            hist.append(max(ql - y[t], y[t] - qh) / w)
            a_c = float(np.clip(a_c + g * (a_nom - (0 if in_c else 1)), lo_c, hi_c))
            out.append((sid[t], int(e["step_h"].iloc[t]), y[t], ql, qh, al, ah, cl, ch))
    o = pd.DataFrame(out, columns=["series_id", "step_h", "y_true", "raw_lo", "raw_hi",
                                   "qaci_lo", "qaci_hi", "cqr_lo", "cqr_hi"])
    o["model"], o["scenario"] = df["model"].iloc[0], scen
    den = np.maximum(np.abs(o["y_true"]), 1e-8)
    ratio = ((o["cqr_hi"] - o["cqr_lo"]) / den).mean() / ((o["raw_hi"] - o["raw_lo"]) / den).mean()
    mid, half = (o["raw_lo"] + o["raw_hi"]) / 2, (o["raw_hi"] - o["raw_lo"]) / 2 * ratio
    o["const_lo"], o["const_hi"] = mid - half, mid + half
    o["const_ratio"] = ratio
    return o


def main(res_dir):
    parts = []
    for f in sorted((res_dir / "raw_forecasts").glob("*.parquet")):
        parts.append(calibrate_file(f))
        print(f"  {f.name}")
    out = pd.concat(parts, ignore_index=True)
    out.to_parquet(res_dir / "calibrated_long.parquet", index=False)
    print(f"[저장] calibrated_long.parquet {len(out)}행")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    main(C.ROOT / ("results_v3_smoke" if a.smoke else "results_v3"))
