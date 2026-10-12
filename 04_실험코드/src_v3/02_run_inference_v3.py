# -*- coding: utf-8 -*-
"""
02_run_inference_v3.py — 제로샷 추론 (v3, 사전등록판)
======================================================
v2 대비 변경
  1) 실측 시장: '마지막 100일' 대신
       - market_panel : 2017~ 전 기간, AAPL 거래일 기준 60거래일 간격 20일 윈도우 (사전 규칙)
       - market_stream: 자산별 마지막 100거래일(20일 x 5 연속 윈도우), H5 보조분석 전용
     패널 윈도우는 스트림 구간 시작 전에 끝나도록 잘라 서로 겹치지 않게 한다.
  2) KODEX 200은 FDR 데이터 사용 (config_v3.MARKET_FILES)
  3) 모든 모델의 표본추출 시드 고정: 합성은 SEED_BASE + s_idx (축·레벨 공통, CRN),
     시장은 SEED_BASE + 100000 + 윈도우번호
  4) torch는 TSFM을 돌릴 때만 import (베이스라인만 돌릴 때 GPU 불필요)
  5) 이미 존재하는 출력 파일은 건너뜀(--overwrite로 강제 재실행)

출력: results_v3/raw_forecasts/{model}_{scenario}.parquet
      results_v3/market_windows.csv (윈도우-날짜 대응표)
"""
import argparse
import time
import numpy as np
import pandas as pd

import config_v3 as C

_TORCH = None
DEVICE = "cpu"


def torch_mod():
    global _TORCH, DEVICE
    if _TORCH is None:
        import torch
        _TORCH = torch
        DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    return _TORCH


def set_seed(seed):
    torch = torch_mod()
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


# ---------------------------------------------------------------- 베이스라인 (v2와 동일)
def predict_random_walk(context, horizon, num_samples, seed):
    rng = np.random.default_rng(seed)
    diffs = np.diff(context)
    mu = np.mean(diffs)
    sd = np.std(diffs, ddof=1) if len(diffs) > 1 else 0.01
    if sd < 1e-6:
        sd = 0.01
    h = np.arange(1, horizon + 1)
    z = rng.standard_normal((num_samples, horizon))
    return context[-1] + h[None, :] * mu + np.sqrt(h)[None, :] * sd * z


def predict_garch_t(context, horizon, num_samples, seed):
    from arch import arch_model
    rng = np.random.default_rng(seed)
    lr = np.diff(np.log(np.maximum(context, 1e-6))) * 100.0
    try:
        res = arch_model(lr, vol="Garch", p=1, q=1, dist="StudentsT", rescale=False).fit(disp="off", show_warning=False)
        omega = res.params.get("omega", 0.01)
        alpha = res.params.get("alpha[1]", 0.05)
        beta = res.params.get("beta[1]", 0.90)
        nu = res.params.get("nu", 5.0)
        mu = res.params.get("Const", 0.0)
        last_s2 = res.conditional_volatility[-1] ** 2
        last_eps = lr[-1] - mu
        out = np.zeros((num_samples, horizon))
        sc = np.sqrt((nu - 2.0) / nu) if nu > 2.0 else 1.0
        for s in range(num_samples):
            s2, eps, p = last_s2, last_eps, context[-1]
            for h in range(horizon):
                s2 = omega + alpha * eps ** 2 + beta * s2
                zt = rng.standard_t(df=max(nu, 2.1)) * sc
                ret = (mu + np.sqrt(max(s2, 1e-6)) * zt) / 100.0
                p = p * np.exp(ret)
                out[s, h] = p
                eps = ret * 100.0 - mu
        return out
    except Exception:
        return predict_random_walk(context, horizon, num_samples, seed)


# ---------------------------------------------------------------- TSFM (v2와 동일 설정)
_CH, _MO = {}, {}


def predict_chronos(context, model_id, horizon, num_samples, seed):
    torch = torch_mod()
    if model_id not in _CH:
        from chronos import ChronosPipeline
        _CH[model_id] = ChronosPipeline.from_pretrained(
            model_id, device_map=DEVICE,
            torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32)
    set_seed(seed)
    fc = _CH[model_id].predict(torch.tensor(context, dtype=torch.float32),
                               prediction_length=horizon, num_samples=num_samples)
    return fc[0].cpu().numpy()


def predict_moirai(context, model_id, horizon, num_samples, seed):
    torch = torch_mod()
    L = len(context)
    key = (model_id, L)
    if key not in _MO:
        from uni2ts.model.moirai import MoiraiForecast, MoiraiModule
        m = MoiraiForecast(module=MoiraiModule.from_pretrained(model_id), prediction_length=horizon,
                           context_length=L, patch_size=C.MOIRAI_PATCH, num_samples=num_samples,
                           target_dim=1, feat_dynamic_real_dim=0, past_feat_dynamic_real_dim=0).to(DEVICE)
        m.eval()
        _MO[key] = m
    set_seed(seed)
    pt = torch.tensor(context, dtype=torch.float32, device=DEVICE).view(1, L, 1)
    with torch.no_grad():
        pr = _MO[key](past_target=pt,
                      past_observed_target=torch.ones(1, L, 1, dtype=torch.bool, device=DEVICE),
                      past_is_pad=torch.zeros(1, L, dtype=torch.bool, device=DEVICE),
                      num_samples=num_samples)
    return pr[0].cpu().numpy()


def predict(model, context, seed):
    H, S = C.HORIZON, C.NUM_SAMPLES
    if model.startswith("chronos"):
        return predict_chronos(context, C.MODEL_IDS[model], H, S, seed)
    if model.startswith("moirai"):
        return predict_moirai(context, C.MODEL_IDS[model], H, S, seed)
    if model == "random_walk":
        return predict_random_walk(context, H, S, seed)
    if model == "garch_t":
        return predict_garch_t(context, H, S, seed)
    raise ValueError(model)


def run(series, model, scenario, overwrite):
    out = C.RAW_FC / f"{model}_{scenario}.parquet"
    if out.exists() and not overwrite:
        print(f"  [skip] {out.name} 존재")
        return
    t0 = time.time()
    rows = []
    for sid, info in series.items():
        smp = predict(model, info["context"], info["seed"])
        for h in range(C.HORIZON):
            row = {"series_id": sid, "model": model, "scenario": scenario, "step_h": h + 1,
                   "y_true": float(info["target"][h])}
            row.update({f"s_{k:03d}": float(smp[k, h]) for k in range(C.NUM_SAMPLES)})
            rows.append(row)
    pd.DataFrame(rows).to_parquet(out, index=False)
    print(f"  [done] {out.name} {len(series)}계열 {time.time() - t0:.1f}s")


# ---------------------------------------------------------------- 데이터 구성
def synthetic_sets(limit=None):
    for f in sorted(C.DATA_SYN.glob("*_L*.parquet")):
        df = pd.read_parquet(f)
        series = {}
        for sid, g in df.groupby("series_id", sort=True):
            g = g.sort_values("step")
            s_idx = int(g["s_idx"].iloc[0])
            if limit is not None and s_idx >= limit:
                continue
            series[sid] = {"context": g.loc[g["is_context"], "price"].values,
                           "target": g.loc[~g["is_context"], "price"].values,
                           "seed": C.SEED_BASE + s_idx}
        yield f"synth_{f.stem}", series


def load_close(ticker):
    d = pd.read_parquet(C.MARKET_FILES[ticker])
    d.columns = [str(c).lower() for c in d.columns]
    s = d["close"].astype(float).dropna()
    s.index = pd.to_datetime(s.index)
    return s.sort_index()


def market_sets():
    L, H = C.CONTEXT_LEN, C.HORIZON
    closes = {t: load_close(t) for t in C.US_TICKERS + C.KR_TICKERS}
    master = closes[C.MASTER_CALENDAR].index
    # 스트림 구간: 자산별 마지막 100거래일. 패널은 가장 이른 스트림 시작일 전에 끝나야 함
    stream_start = min(s.index[-C.STREAM_LEN] for s in closes.values())
    panel, stream, recs = {}, {}, []
    k, i = 0, L
    while True:
        if i + H > len(master):
            break
        origin = master[i]                     # 첫 예측 대상일
        if master[i + H - 1] >= stream_start:
            break
        for t, s in closes.items():
            j = s.index.searchsorted(origin)   # 해당 자산 달력에서 origin 이상 첫 거래일
            if j < L or j + H > len(s) or s.index[j + H - 1] >= stream_start:
                recs.append({"set": "panel", "ticker": t, "k": k, "origin": origin.date(), "used": False})
                continue
            sid = f"mktp_{t}_k{k:03d}"
            panel[sid] = {"context": s.values[j - L:j], "target": s.values[j:j + H],
                          "seed": C.SEED_BASE + 100000 + k}
            recs.append({"set": "panel", "ticker": t, "k": k, "origin": s.index[j].date(),
                         "context_start": s.index[j - L].date(), "target_end": s.index[j + H - 1].date(),
                         "used": True})
        k += 1
        i += C.PANEL_STEP
    for t, s in closes.items():
        n = len(s)
        for w in range(C.STREAM_LEN // H):          # w=0 이 가장 과거
            j = n - C.STREAM_LEN + w * H
            sid = f"mkts_{t}_w{w}"
            stream[sid] = {"context": s.values[j - L:j], "target": s.values[j:j + H],
                           "seed": C.SEED_BASE + 200000 + w}
            recs.append({"set": "stream", "ticker": t, "k": w, "origin": s.index[j].date(),
                         "context_start": s.index[j - L].date(), "target_end": s.index[j + H - 1].date(),
                         "used": True})
    C.RES.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(recs).to_csv(C.RES / "market_windows.csv", index=False)
    return panel, stream


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="all", help="모델명 또는 all / baselines / tsfm")
    ap.add_argument("--target", default="all", choices=["synthetic", "market", "all"])
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--smoke", action="store_true", help="시나리오당 2계열만 (출력 디렉터리 results_v3_smoke)")
    a = ap.parse_args()
    if a.smoke:
        C.RES = C.ROOT / "results_v3_smoke"
        C.RAW_FC = C.RES / "raw_forecasts"
    C.RAW_FC.mkdir(parents=True, exist_ok=True)

    models = {"all": C.MODELS, "baselines": ["garch_t", "random_walk"], "tsfm": C.TSFM}.get(a.model, [a.model])
    if a.target in ("synthetic", "all"):
        for scen, series in synthetic_sets(limit=2 if a.smoke else None):
            for m in models:
                run(series, m, scen, a.overwrite)
    if a.target in ("market", "all"):
        panel, stream = market_sets()
        if a.smoke:
            panel = dict(list(panel.items())[:6])
            stream = dict(list(stream.items())[:5])
        print(f"[market] panel 윈도우 {len(panel)}개, stream 윈도우 {len(stream)}개")
        for m in models:
            run(panel, m, "market_panel", a.overwrite)
            run(stream, m, "market_stream", a.overwrite)


if __name__ == "__main__":
    main()
