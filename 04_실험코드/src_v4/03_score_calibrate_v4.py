# -*- coding: utf-8 -*-
"""
03_score_calibrate_v4.py — 지표 계산 + 사후보정 (계획서 v4 §5·§6)
=================================================================
입력: results_v4/raw/*.parquet (02 출력), data/synthetic_v4/oracle_v4.parquet
지표(예측 1건마다): cover(정답이 [q0.1, q0.9] 안), ql(9개 분위 평균 pinball 손실), width, wis(Winkler IS₀.₂)
사후보정 ACI-CQR (에피소드마다 새로 시작):
  - 점수 sₜ = max(lₜ − yₜ, yₜ − uₜ) / wₜ  (wₜ = uₜ − lₜ, 폭으로 나눈 이탈 정도)
  - 1~20일(준비): 점수만 기록. 21~80일(채점): 기록 n개 중 k = ⌈(n+1)(1−αₜ)⌉번째 작은 점수 × wₜ 만큼
    양쪽을 넓힌(음수면 좁힌) 구간을 내고, 실제값을 본 뒤 αₜ₊₁ = clip(αₜ + γ(α − 빗나감), 0.02, 0.50),
    그날 점수를 기록에 추가. k > n 이면 기록의 최댓값을 쓴다. α = 0.20, γ = 0.05.
  - 대조군: 같은 묶음(모델·조건·시나리오, 실제는 10종목 전체)의 채점일 평균 폭이 보정 구간과 같아지도록
    원래 구간을 중심 기준으로 일괄 확대. 실제값을 쓰지 않음(배율만 사후에 맞춤).
  - 보조(실제 주식만): 종목별로 끊지 않는 연속 보정. 처음 20일 준비 후 모든 날 채점.
  - 유한값이 아닌 예측: cover=False, 손실 계산 제외, 보정 기록에 넣지 않음(빗나감으로 α 갱신).
채점 대상: 주분석은 in_main=True 이고 day > 20 인 날.
출력: results_v4/scored_v4.parquet
"""
import argparse
import bisect
import math

import numpy as np
import pandas as pd

import config_v4 as C

QCOLS = [f"q{i+1}" for i in range(len(C.QLEVELS))]
TAU = np.array(C.QLEVELS)


def metrics(df):
    Q = df[QCOLS].to_numpy(float)
    y = df["y"].to_numpy(float)
    lo, hi = Q[:, C.LO_IDX], Q[:, C.HI_IDX]
    fin = np.isfinite(Q).all(1)
    df["lo"], df["hi"] = lo, hi
    df["cover"] = fin & (y >= lo) & (y <= hi)
    with np.errstate(invalid="ignore"):
        pin = (TAU[None, :] - (y[:, None] < Q)) * (y[:, None] - Q)
        df["ql"] = np.where(fin, pin.mean(1), np.nan)
        df["width"] = np.where(fin, hi - lo, np.nan)
        a = 1 - C.NOMINAL
        df["wis"] = np.where(fin, (hi - lo) + (2 / a) * np.maximum(lo - y, 0) + (2 / a) * np.maximum(y - hi, 0), np.nan)
    return df


def aci_cqr(lo, hi, y, warm):
    """한 에피소드(또는 연속 구간)의 보정 구간. 반환: cal_lo, cal_hi, alpha_used (warm 이전은 NaN)."""
    n = len(y)
    cl, ch, al = np.full(n, np.nan), np.full(n, np.nan), np.full(n, np.nan)
    a = C.ACI_ALPHA
    hist = []                                       # 정렬 유지
    for t in range(n):
        ok = np.isfinite(lo[t]) and np.isfinite(hi[t])
        w = max(hi[t] - lo[t], 1e-12) if ok else np.nan
        if t >= warm:
            al[t] = a
            if ok and hist:
                k = math.ceil((len(hist) + 1) * (1 - a))
                m = (hist[-1] if k > len(hist) else hist[k - 1]) * w
                cl[t], ch[t] = lo[t] - m, hi[t] + m
                err = 0.0 if cl[t] <= y[t] <= ch[t] else 1.0
            else:
                err = 1.0
            a = min(max(a + C.ACI_GAMMA * (C.ACI_ALPHA - err), C.ACI_CLIP[0]), C.ACI_CLIP[1])
        if ok:
            bisect.insort(hist, max(lo[t] - y[t], y[t] - hi[t]) / w)
    return cl, ch, al


def calibrate(df):
    df = df.sort_values(["scenario", "unit", "episode", "day"]).reset_index(drop=True)
    cl = np.full(len(df), np.nan)
    ch, al = cl.copy(), cl.copy()
    for _, idx in df.groupby(["scenario", "unit", "episode"], sort=False).indices.items():
        g = df.iloc[idx]
        a, b, c = aci_cqr(g["lo"].to_numpy(), g["hi"].to_numpy(), g["y"].to_numpy(), C.EP_WARM)
        cl[idx], ch[idx], al[idx] = a, b, c
    df["cal_lo"], df["cal_hi"], df["alpha_t"] = cl, ch, al
    df["cal_cover"] = (df["y"] >= df["cal_lo"]) & (df["y"] <= df["cal_hi"])
    df["scored"] = df["in_main"] & (df["day"] > C.EP_WARM)
    # 대조군: 묶음별 평균 폭 맞춤 (합성=시나리오별, 실제=전체)
    key = "scenario" if df["dataset"].iloc[0] == "synth" else "dataset"
    df["ctl_lo"], df["ctl_hi"], df["ctl_ratio"] = np.nan, np.nan, np.nan
    for _, idx in df.groupby(key).indices.items():
        g = df.iloc[idx]
        s = g["scored"] & np.isfinite(g["cal_lo"]) & np.isfinite(g["width"])
        ratio = (g.loc[s, "cal_hi"] - g.loc[s, "cal_lo"]).mean() / g.loc[s, "width"].mean()
        mid, half = (g["lo"] + g["hi"]) / 2, (g["hi"] - g["lo"]) / 2 * ratio
        df.loc[g.index, "ctl_lo"], df.loc[g.index, "ctl_hi"], df.loc[g.index, "ctl_ratio"] = mid - half, mid + half, ratio
    df["ctl_cover"] = (df["y"] >= df["ctl_lo"]) & (df["y"] <= df["ctl_hi"])
    # 보조: 실제 주식 연속 보정
    df["cont_lo"], df["cont_hi"], df["cont_scored"] = np.nan, np.nan, False
    if df["dataset"].iloc[0] == "real":
        for _, idx in df.groupby("unit").indices.items():
            g = df.iloc[idx].sort_values("date")
            a, b, _ = aci_cqr(g["lo"].to_numpy(), g["hi"].to_numpy(), g["y"].to_numpy(), C.EP_WARM)
            df.loc[g.index, "cont_lo"], df.loc[g.index, "cont_hi"] = a, b
            df.loc[g.index[C.EP_WARM:], "cont_scored"] = True
    df["cont_cover"] = (df["y"] >= df["cont_lo"]) & (df["y"] <= df["cont_hi"])
    return df


def oracle_rows(smoke):
    o = pd.read_parquet(C.DATA_SYN / "oracle_v4.parquet")
    syn = pd.read_parquet(C.DATA_SYN / "synthetic_v4.parquet")
    syn = syn[syn["t"] >= C.FIRST_TARGET].assign(day=lambda d: d["t"] - C.FIRST_TARGET + 1)
    o = o.merge(syn[["scenario", "s", "day", "r"]], on=["scenario", "s", "day"], how="inner", validate="1:1")
    if smoke:
        o = o[o["s"] < 3]
    df = pd.DataFrame({"dataset": "synth", "scenario": o["scenario"], "unit": o["s"].astype(str), "episode": 1,
                       "day": o["day"], "date": pd.NaT, "in_main": True, "y": o["r"]})
    for c in QCOLS:
        df[c] = o[c].to_numpy()
    df["crossed"], df["nonfinite"], df["fallback"] = False, False, False
    df["model"], df["L"], df["input"] = "oracle", 0, "-"
    return df


def main(smoke):
    rd = C.res_dir(smoke)
    files = sorted((rd / "raw").glob("*.parquet"))
    parts = []
    for f in files:
        model, cond, ds = f.stem.split("__")
        L, kind = cond[1:].split("_")
        df = pd.read_parquet(f)
        df["model"], df["L"], df["input"] = model, int(L), kind
        df = calibrate(metrics(df))
        parts.append(df)
        s = df[df["scored"]]
        print(f"  {f.name}: n={len(df)} 채점 {len(s)}  원래 {s['cover'].mean():.3f}  보정 {s['cal_cover'].mean():.3f}"
              f"  대조 {s['ctl_cover'].mean():.3f}", flush=True)
    orc = calibrate(metrics(oracle_rows(smoke)))
    s = orc[orc["scored"]]
    print(f"  oracle(정답 기준선): 채점 {len(s)}  원래 {s['cover'].mean():.3f}  보정 {s['cal_cover'].mean():.3f}")
    out = pd.concat(parts + [orc], ignore_index=True)
    # 정답 정렬 점검: 같은 합성 과제의 정답 y는 모든 모델에서 같아야 함
    sy = out[out["dataset"] == "synth"]
    chk = sy.groupby(["scenario", "unit", "day"])["y"].agg(["min", "max"])
    if not np.allclose(chk["min"], chk["max"], rtol=0, atol=1e-12):
        raise AssertionError("합성 정답값이 모델마다 다름 → 정렬 오류")
    rl = out[out["dataset"] == "real"]
    chk = rl.groupby(["unit", "date"])["y"].agg(["min", "max"])
    if not np.allclose(chk["min"], chk["max"], rtol=0, atol=1e-12):
        raise AssertionError("실제 정답값이 모델마다 다름 → 정렬 오류")
    out.to_parquet(rd / "scored_v4.parquet", index=False)
    print(f"[저장] scored_v4.parquet {len(out)}행, 정답 정렬 점검 통과")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    main(ap.parse_args().smoke)
