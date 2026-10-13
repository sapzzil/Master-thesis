# -*- coding: utf-8 -*-
"""
tasks_v4.py — 예측 과제(과거 L일 → 내일) 만들기. 합성·실제 주식이 같은 규칙을 쓴다.
====================================================================================
과제 1개 = (과거 L일 수익률, 과거 L일 가격, 기준가격 Pₜ, 정답 rₜ₊₁, 메타정보)
  - 수익률 입력: r[i−L : i]        (예측 대상 r[i]는 포함하지 않음)
  - 가격 입력  : P[i−L : i]        (P[i−1]이 기준가격, r[i] = ln(P[i]/P[i−1]))
  - 합성: 에피소드 1개(80일), 대상 위치 i = 452 … 531
  - 실제: 2017-01-02 이후 모든 거래일을 예측. 80일씩 잘라 에피소드 번호를 붙이고,
          마지막에 80일이 안 되는 자투리는 in_main=False (주분석 제외, 연속 보정 보조분석에만 사용)
"""
import hashlib

import numpy as np
import pandas as pd

import config_v4 as C


def sha256(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def verify_inputs():
    bad = []
    for rel, h in C.EXPECTED_SHA256.items():
        p = C.ROOT / rel
        if not p.exists():
            bad.append(f"없음: {rel}")
        elif sha256(p) != h:
            bad.append(f"지문 불일치: {rel}")
    if bad:
        raise SystemExit("입력 데이터 점검 실패 → 중단\n" + "\n".join(bad))


def load_real():
    """종목 → DataFrame(date, close, r). 거래량 0인 날 제외, 2015-01-02~2026-09-22."""
    out = {}
    for t, f in C.REAL_FILES.items():
        d = pd.read_parquet(f)
        d.columns = [str(c).lower() for c in d.columns]
        d = d[d["volume"] > 0].loc[C.REAL_START:C.REAL_END]
        p = d["close"].astype(float)
        p = p[p > 0].dropna()
        df = pd.DataFrame({"date": p.index, "close": p.values})
        df["r"] = np.log(df["close"]).diff()
        out[t] = df.reset_index(drop=True)
    return out


def market_of(unit):
    return "US" if unit in C.US else "KR"


def synth_tasks(L, smoke=False):
    syn = pd.read_parquet(C.DATA_SYN / "synthetic_v4.parquet")
    if smoke:
        syn = syn[syn["s"] < 3]
    R, P, A, Y, meta = [], [], [], [], []
    days = np.arange(C.EP_LEN)
    tgt = C.FIRST_TARGET + days                                   # 452 … 531
    idx = tgt[:, None] + np.arange(-L, 0)[None, :]                # (80, L): i−L … i−1
    assert (idx < tgt[:, None]).all() and idx.min() >= 0
    for (sc, s), g in syn.groupby(["scenario", "s"], sort=True):
        r = g.sort_values("t")["r"].to_numpy()
        assert len(r) == C.SIM_LEN
        price = C.P0 * np.exp(np.cumsum(r))                       # P[t] = 가격(그 날 수익률 반영 후)
        R.append(r[idx])
        P.append(price[idx])
        A.append(price[tgt - 1])
        Y.append(r[tgt])
        meta.append(pd.DataFrame({"dataset": "synth", "scenario": sc, "unit": str(s), "episode": 1,
                                  "day": days + 1, "date": pd.NaT, "in_main": True}))
    return np.concatenate(R), np.concatenate(P), np.concatenate(A), np.concatenate(Y), pd.concat(meta, ignore_index=True)


def real_tasks(L, smoke=False):
    R, P, A, Y, meta = [], [], [], [], []
    for t, df in load_real().items():
        if smoke and t not in ("AAPL", "005930"):
            continue
        r, price = df["r"].to_numpy(), df["close"].to_numpy()
        ii = np.where(df["date"] >= pd.Timestamp(C.EVAL_START))[0]
        assert ii[0] - L >= 1, f"{t}: 과거 {L}일 부족"
        if smoke:
            ii = ii[: 2 * C.EP_LEN]
        k = np.arange(len(ii))
        n_ep = len(ii) // C.EP_LEN
        idx = ii[:, None] + np.arange(-L, 0)[None, :]
        R.append(r[idx])
        P.append(price[idx])
        A.append(price[ii - 1])
        Y.append(r[ii])
        meta.append(pd.DataFrame({"dataset": "real", "scenario": market_of(t), "unit": t,
                                  "episode": k // C.EP_LEN + 1, "day": k % C.EP_LEN + 1,
                                  "date": df["date"].to_numpy()[ii], "in_main": (k // C.EP_LEN) < n_ep}))
    return np.concatenate(R), np.concatenate(P), np.concatenate(A), np.concatenate(Y), pd.concat(meta, ignore_index=True)


def tasks(dataset, L, smoke=False):
    R, P, A, Y, M = (synth_tasks if dataset == "synth" else real_tasks)(L, smoke)
    assert np.isfinite(R).all() and np.isfinite(P).all() and (P > 0).all() and np.isfinite(Y).all()
    return R.astype(np.float32), P.astype(np.float32), A.astype(np.float64), Y.astype(np.float64), M.reset_index(drop=True)


SYN_FINGERPRINT_COLS = ["scenario", "s"]


def synth_fingerprint():
    """합성 데이터 값 지문(시나리오별 Σr, Σr²). PC에서 다시 생성해도 같은지 확인용."""
    syn = pd.read_parquet(C.DATA_SYN / "synthetic_v4.parquet")
    g = syn.groupby("scenario")["r"]
    return pd.DataFrame({"sum": g.sum(), "sumsq": g.apply(lambda x: (x ** 2).sum()), "n": g.size()})
