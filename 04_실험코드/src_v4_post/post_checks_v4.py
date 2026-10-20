# -*- coding: utf-8 -*-
"""
post_checks_v4.py — 본 실행 이후의 사후 점검 3종 (미리 고정한 분석 계획 밖, 결과와 무관하게 모두 보고)
==========================================================================================
  e1  Chronos-T5 수익률 입력 붕괴 원인: 샘플링 top_k(기본 50) 제한과 값 크기의 영향
  e2  Chronos-2에 거래량(로그)을 과거 공변량으로 넣었을 때의 변화 (실제 10종목)
  e3  TimesFM-2.5 1년·가격 구간 과대의 원인: 연속 분위수 헤드·입력 정규화·로그 가격
실행:  python post_checks_v4.py --exp e1 [--smoke]      (04_실험코드/src_v4_post 에서)
출력:  results_v4_post/raw/{exp}__{variant}.parquet, results_v4_post/summary_{exp}.csv, run_log.jsonl
src_v4의 config·tasks·어댑터 호출 방식을 그대로 가져다 쓰며, src_v4 파일은 고치지 않는다.
"""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src_v4"))
import config_v4 as C  # noqa: E402
import tasks_v4 as T  # noqa: E402
from baselines_v4 import rw_quantiles  # noqa: E402

QL = np.array(C.QLEVELS)
OUT = C.ROOT / "results_v4_post"
RAW = OUT / "raw"
SEED = C.SEED_BASE + 900


# ------------------------------------------------------------------ 공통
def torch_():
    import torch
    return torch


def score(q, y):
    q = np.sort(np.asarray(q, float), axis=1)
    y = np.asarray(y, float)
    cover = (y >= q[:, 0]) & (y <= q[:, -1])
    d = y[:, None] - q
    pin = np.maximum(QL * d, (QL - 1) * d).mean(1)
    return cover, q[:, -1] - q[:, 0], pin


def save(exp, variant, M, y, q, extra=None):
    cover, width, pin = score(q, y)
    df = M.copy().reset_index(drop=True)
    df["y"] = y
    for k in range(9):
        df[f"q{k+1}"] = np.sort(q, axis=1)[:, k]
    df["cover"], df["width"], df["ql"] = cover, width, pin
    RAW.mkdir(parents=True, exist_ok=True)
    df.to_parquet(RAW / f"{exp}__{variant}.parquet", index=False)
    rec = {"exp": exp, "variant": variant, "n": len(df), "coverage": float(cover.mean()),
           "mean_width_pct": float(width.mean() * 100), "ql": float(pin.mean()),
           "finished": time.strftime("%Y-%m-%d %H:%M:%S")}
    if extra:
        rec.update(extra)
    with open(OUT / "run_log.jsonl", "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"[저장] {exp}__{variant}: 커버리지 {rec['coverage']*100:.1f}%, 평균 폭 {rec['mean_width_pct']:.2f}%p, "
          f"분위수 손실 {rec['ql']:.5f}  (n={len(df)})", flush=True)
    return rec


def batched(fn, X, batch, **kw):
    out, i = [], 0
    t0 = time.time()
    while i < len(X):
        try:
            q = fn(X[i:i + batch], **kw)
        except Exception as e:  # noqa: BLE001
            if "out of memory" in str(e).lower() and batch > 1:
                torch_().cuda.empty_cache()
                batch //= 2
                print(f"    메모리 부족 → 배치 {batch}", flush=True)
                continue
            raise
        out.append(np.asarray(q, float))
        i += batch
        if len(out) % 50 == 0:
            el = time.time() - t0
            print(f"    {min(i, len(X))}/{len(X)} 경과 {el/60:.1f}분, 남은 예상 {el/i*(len(X)-i)/60:.1f}분", flush=True)
    return np.concatenate(out)


def to_ret(q, anchor, kind):
    if kind == "return":
        return q
    if kind == "logprice":
        return q - np.log(anchor)[:, None]
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.log(q / anchor[:, None])


def synth_L1(L, smoke):
    R, P, A, Y, M = T.tasks("synth", L, smoke)
    k = (M["scenario"] == "L1").to_numpy()
    return R[k], P[k], A[k], Y[k], M[k].reset_index(drop=True)


def gauss01(L, smoke):
    """Chronos 원 논문 그림 12a 조건: 독립 N(0,1) 계열. 계열 100개 × 예측 80일."""
    rng = np.random.default_rng(SEED)
    n = 3 if smoke else 100
    x = rng.standard_normal((n, L + C.EP_LEN)).astype(np.float32)
    days = np.arange(C.EP_LEN)
    idx = (L + days)[:, None] + np.arange(-L, 0)[None, :]
    X = np.concatenate([s[idx] for s in x])
    Y = np.concatenate([s[L + days] for s in x]).astype(float)
    M = pd.DataFrame({"dataset": "gauss01", "unit": np.repeat(np.arange(n), C.EP_LEN).astype(str),
                      "day": np.tile(days + 1, n)})
    return X, Y, M


# ------------------------------------------------------------------ e1: Chronos-T5
def e1(smoke):
    torch = torch_()
    from chronos import ChronosPipeline
    pipe = ChronosPipeline.from_pretrained(C.MODEL_IDS["chronos_t5_base"], device_map="cuda", torch_dtype=torch.bfloat16)
    cfg = pipe.model.config
    info = {k: getattr(cfg, k, None) for k in ["n_tokens", "tokenizer_kwargs", "temperature", "top_k", "top_p",
                                                "num_samples", "context_length"]}
    print("[설정] Chronos-T5 base:", json.dumps(info, ensure_ascii=False, default=str), flush=True)
    (OUT / "e1_model_config.json").write_text(json.dumps(info, ensure_ascii=False, default=str, indent=1), encoding="utf-8")

    def fc(x, top_k=None):
        kw = {} if top_k is None else {"top_k": top_k}
        try:
            s = pipe.predict(torch.tensor(x, dtype=torch.float32), prediction_length=1, num_samples=C.CHRONOS_SAMPLES, **kw)
        except TypeError:                       # predict()가 top_k 인자를 받지 않는 버전이면 설정값을 잠시 바꿔 실행
            old = cfg.top_k
            cfg.top_k = top_k if top_k is not None else old
            try:
                s = pipe.predict(torch.tensor(x, dtype=torch.float32), prediction_length=1, num_samples=C.CHRONOS_SAMPLES)
            finally:
                cfg.top_k = old
        return np.quantile(s.float().cpu().numpy()[:, :, 0], QL, axis=1).T

    full = int(info["n_tokens"] or 4096)
    recs = []

    def run(variant, X, Y, M, L, top_k, scale=1.0, kind="return", A=None):
        if (RAW / f"e1__{variant}.parquet").exists():
            print(f"[건너뜀] e1__{variant}", flush=True)
            return
        torch.manual_seed(SEED)
        print(f"\n=== e1 {variant}: {len(X)}회, top_k={top_k or '기본'}, 배율 {scale} ===", flush=True)
        q = batched(fc, X * scale, C.BATCH[("chronos_t5_base", L)], top_k=top_k) / scale
        q = to_ret(q, A, kind) if kind != "return" else q
        recs.append(save("e1", variant, M, Y, q, {"L": L, "top_k": top_k or info["top_k"], "scale": scale, "input": kind}))

    for L in ([252] if not smoke else [21]):
        R, P, A, Y, M = synth_L1(L, smoke)
        run(f"L1_return_L{L}_default", R, Y, M, L, None)
        run(f"L1_return_L{L}_topkall", R, Y, M, L, full)
        run(f"L1_return_L{L}_default_x100", R, Y, M, L, None, scale=100.0)
        run(f"L1_price_L{L}_default", P, Y, M, L, None, kind="price", A=A)
        run(f"L1_price_L{L}_topkall", P, Y, M, L, full, kind="price", A=A)
        X, Yg, Mg = gauss01(L, smoke)
        run(f"gauss01_L{L}_default", X, Yg, Mg, L, None)
        run(f"gauss01_L{L}_topkall", X, Yg, Mg, L, full)
    for L in ([21, 252] if not smoke else [21]):
        R, P, A, Y, M = T.tasks("real", L, smoke)
        run(f"real_return_L{L}_topkall", R, Y, M, L, full)


# ------------------------------------------------------------------ e2: Chronos-2 + 거래량
def real_with_volume(L, smoke):
    """tasks_v4.real_tasks와 같은 규칙으로 과제를 만들고, 같은 날들의 로그 거래량을 붙인다."""
    R0, P0, A0, Y0, M0 = T.tasks("real", L, smoke)
    V = []
    for t, f in C.REAL_FILES.items():
        if smoke and t not in ("AAPL", "005930"):
            continue
        d = pd.read_parquet(f)
        d.columns = [str(c).lower() for c in d.columns]
        d = d[d["volume"] > 0].loc[C.REAL_START:C.REAL_END]
        d = d[(d["close"].astype(float) > 0) & d["close"].notna()]
        ref = T.load_real()[t]
        assert np.allclose(d["close"].to_numpy(float), ref["close"].to_numpy()), f"{t}: 종가 정렬 불일치"
        lv = np.log(d["volume"].to_numpy(float))
        ii = np.where(ref["date"] >= pd.Timestamp(C.EVAL_START))[0]
        if smoke:
            ii = ii[: 2 * C.EP_LEN]
        V.append(lv[ii[:, None] + np.arange(-L, 0)[None, :]])
    V = np.concatenate(V).astype(np.float32)
    assert len(V) == len(R0)
    return R0, P0, A0, Y0, M0, V


def e2(smoke):
    torch = torch_()
    from chronos import Chronos2Pipeline
    pipe = Chronos2Pipeline.from_pretrained(C.MODEL_IDS["chronos2"], device_map="cuda")

    def fc(x, v=None):
        if v is None:
            inp = [torch.tensor(a) for a in x]
        else:
            inp = [{"target": a, "past_covariates": {"log_volume": b}} for a, b in zip(x, v)]
        q, _ = pipe.predict_quantiles(inp, prediction_length=1, quantile_levels=list(QL))
        arr = np.stack([np.asarray(t.float().cpu() if hasattr(t, "cpu") else t) for t in q]) \
            if isinstance(q, (list, tuple)) else np.asarray(q.float().cpu() if hasattr(q, "cpu") else q)
        return arr.reshape(len(x), -1)[:, -len(QL):]

    def fcv(xv):
        n = xv.shape[1] // 2
        return fc(xv[:, :n], xv[:, n:])

    for L in ([21, 252] if not smoke else [21]):
        R, P, A, Y, M, V = real_with_volume(L, smoke)
        for kind, X in [("return", R), ("price", P)]:
            for cov in ["none", "logvolume"]:
                variant = f"real_{kind}_L{L}_{cov}"
                if (RAW / f"e2__{variant}.parquet").exists():
                    print(f"[건너뜀] e2__{variant}", flush=True)
                    continue
                print(f"\n=== e2 {variant}: {len(X)}회 ===", flush=True)
                if cov == "none":
                    q = batched(fc, X, 256)
                else:
                    q = batched(fcv, np.concatenate([X, V], axis=1), 256)
                save("e2", variant, M, Y, to_ret(q, A, kind), {"L": L, "input": kind, "covariate": cov})
        # 같은 과제에 대한 RW (비교 기준)
        variant = f"real_rw_L{L}"
        if not (RAW / f"e2__{variant}.parquet").exists():
            q, _ = rw_quantiles(R)
            save("e2", variant, M, Y, q, {"L": L, "input": "return", "covariate": "rw"})


# ------------------------------------------------------------------ e3: TimesFM-2.5
def e3(smoke):
    import timesfm
    from timesfm import TimesFM_2p5_200M_torch
    models = {}

    def get(cq, norm):
        if (cq, norm) not in models:
            m = TimesFM_2p5_200M_torch.from_pretrained(C.MODEL_IDS["timesfm25"], torch_compile=False)
            m.compile(timesfm.ForecastConfig(max_context=256, max_horizon=128, normalize_inputs=norm,
                                             use_continuous_quantile_head=cq, per_core_batch_size=256))
            models[(cq, norm)] = m
        return models[(cq, norm)]

    def fc(x, cq=True, norm=True):
        _, q = get(cq, norm).forecast(horizon=1, inputs=list(x))
        return np.asarray(q)[:, 0, 1:10]

    def run(variant, X, Y, M, A, kind, cq=True, norm=True, L=252):
        if (RAW / f"e3__{variant}.parquet").exists():
            print(f"[건너뜀] e3__{variant}", flush=True)
            return
        print(f"\n=== e3 {variant}: {len(X)}회 (연속 분위수 헤드 {cq}, 입력 정규화 {norm}) ===", flush=True)
        q = batched(fc, X, 256, cq=cq, norm=norm)
        save("e3", variant, M, Y, to_ret(q, A, kind), {"L": L, "input": kind, "cq_head": cq, "normalize": norm})

    L = 21 if smoke else 252
    R, P, A, Y, M = synth_L1(L, smoke)
    run(f"L1_price_L{L}_default", P, Y, M, A, "price")
    run(f"L1_price_L{L}_noCQhead", P, Y, M, A, "price", cq=False)
    run(f"L1_price_L{L}_noNorm", P, Y, M, A, "price", norm=False)
    run(f"L1_logprice_L{L}_default", np.log(P), Y, M, A, "logprice")
    run(f"L1_price_L{L}_rebased", P / P[:, -1:] * 100.0, Y, M, A * 0 + 100.0, "price")
    run(f"L1_return_L{L}_default", R, Y, M, A, "return")
    run(f"L1_return_L{L}_noCQhead", R, Y, M, A, "return", cq=False)
    Rr, Pr, Ar, Yr, Mr = T.tasks("real", L, smoke)
    run(f"real_price_L{L}_default", Pr, Yr, Mr, Ar, "price")
    run(f"real_price_L{L}_noCQhead", Pr, Yr, Mr, Ar, "price", cq=False)
    run(f"real_logprice_L{L}_default", np.log(Pr), Yr, Mr, Ar, "logprice")


# ------------------------------------------------------------------ 요약
def month_test(a, b):
    """실제 주식 주분석 행(in_main)에서 월별 평균 손실 차(a − b)의 t검정. 개선율 = 1 − Σa/Σb."""
    k = a["in_main"].to_numpy() & b["in_main"].to_numpy()
    mo = pd.to_datetime(a.loc[k, "date"]).dt.to_period("M").astype(str).to_numpy()
    D = pd.Series(a.loc[k, "ql"].to_numpy() - b.loc[k, "ql"].to_numpy()).groupby(mo).mean()
    return 1 - a.loc[k, "ql"].sum() / b.loc[k, "ql"].sum(), float(stats.ttest_1samp(D.values, 0).pvalue), len(D)


def summarize(exp):
    rows = []
    for f in sorted(RAW.glob(f"{exp}__*.parquet")):
        d = pd.read_parquet(f)
        v = f.stem.split("__", 1)[1]
        main = d[d["in_main"]] if "in_main" in d else d
        r = {"variant": v, "n": len(main), "coverage": main["cover"].mean(), "mean_width_pct": main["width"].mean() * 100,
             "ql": main["ql"].mean()}
        if exp == "e2" and "_rw_" not in v:
            L = int(v.split("_L")[1].split("_")[0])
            b = pd.read_parquet(RAW / f"e2__real_rw_L{L}.parquet")
            r["impr_vs_rw"], r["p_vs_rw"], r["months"] = month_test(d, b)
            if v.endswith("logvolume"):
                u = pd.read_parquet(RAW / f"e2__{v.replace('logvolume', 'none')}.parquet")
                r["impr_vs_univariate"], r["p_vs_univariate"], _ = month_test(d, u)
                r["share_changed"] = float((np.abs(d["q5"].to_numpy() - u["q5"].to_numpy()) > 1e-9).mean())
        rows.append(r)
    s = pd.DataFrame(rows)
    s.to_csv(OUT / f"summary_{exp}.csv", index=False, encoding="utf-8-sig")
    print(f"\n[요약] summary_{exp}.csv\n" + s.to_string(index=False, float_format=lambda x: f"{x:.4f}"), flush=True)


def check_reproduction(exp):
    """사후 점검의 기본 설정이 본 실행 결과와 같은지 확인 (같은 과제·같은 설정이면 커버리지가 거의 같아야 함)."""
    pairs = {"e1": [("L1_return_L252_default", "chronos_t5_base__L252_return__synth", "L1")],
             "e2": [("real_return_L252_none", "chronos2__L252_return__real", None),
                    ("real_return_L21_none", "chronos2__L21_return__real", None)],
             "e3": [("L1_price_L252_default", "timesfm25__L252_price__synth", "L1"),
                    ("real_price_L252_default", "timesfm25__L252_price__real", None)]}[exp]
    for v, ref, sc in pairs:
        f = RAW / f"{exp}__{v}.parquet"
        g = C.res_dir(False) / "raw" / f"{ref}.parquet"
        if not (f.exists() and g.exists()):
            continue
        a = pd.read_parquet(f)
        b = pd.read_parquet(g)
        if sc:
            b = b[b["scenario"] == sc]
        cb = ((b["y"] >= b["q1"]) & (b["y"] <= b["q9"])).mean()
        print(f"[재현 확인] {exp}__{v}: {a['cover'].mean()*100:.2f}%  ↔  본 실행 {ref}: {cb*100:.2f}%  "
              f"(n {len(a)} ↔ {len(b)})", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--exp", required=True, choices=["e1", "e2", "e3"])
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        OUT = C.ROOT / "results_v4_post_smoke"
        RAW = OUT / "raw"
    OUT.mkdir(parents=True, exist_ok=True)
    T.verify_inputs()
    print(f"python {sys.version.split()[0]}, exp={a.exp}, smoke={a.smoke}, 시작 {time.strftime('%H:%M:%S')}", flush=True)
    {"e1": e1, "e2": e2, "e3": e3}[a.exp](a.smoke)
    summarize(a.exp)
    if not a.smoke:
        check_reproduction(a.exp)
    print(f"\n[완료] {a.exp} {time.strftime('%H:%M:%S')}", flush=True)
