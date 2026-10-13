# -*- coding: utf-8 -*-
"""
02_run_inference_v4.py — 모델 예측 (계획서 v4 §1·§4)
=====================================================
모델 하나씩 따로 실행한다:  python 02_run_inference_v4.py --model moirai2 [--smoke]
  모델: chronos_t5_base, chronos2, timesfm25, moirai2 (GPU) / rw, garch_t (CPU)
출력: results_v4/raw/{model}__L{L}_{input}__{dataset}.parquet  (조건·데이터셋마다 파일 1개)
  - 이미 있는 파일은 건너뛴다(중간에 끊겨도 다시 실행하면 이어서 함).
  - 열: dataset, scenario, unit, episode, day, date, in_main, y, q1~q9(수익률 단위, 오름차순 정렬 후),
        crossed(정렬 전 분위수 교차 여부), nonfinite(유한값 아님), fallback(GARCH 대체 사용)
어댑터는 준비작업 k03에서 PC로 확인된 호출 방식을 그대로 쓴다.
"""
import argparse
import gc
import json
import os
import platform
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

import config_v4 as C
import tasks_v4 as T
from baselines_v4 import garch_quantiles, rw_quantiles

QL = C.QLEVELS
Z_Q = stats.norm.ppf(QL)


# ------------------------------------------------------------------ 어댑터: (n, L) 배열 → (n, 9) 분위수 (입력과 같은 단위)
def _torch():
    import torch
    return torch


class ChronosT5:
    def __init__(self, batch):
        torch = _torch()
        from chronos import ChronosPipeline
        self.pipe = ChronosPipeline.from_pretrained(C.MODEL_IDS["chronos_t5_base"], device_map="cuda",
                                                    torch_dtype=torch.bfloat16)

    def __call__(self, x):
        torch = _torch()
        s = self.pipe.predict(torch.tensor(x, dtype=torch.float32), prediction_length=1,
                              num_samples=C.CHRONOS_SAMPLES)               # (n, S, 1)
        s = s.float().cpu().numpy()[:, :, 0]
        return np.quantile(s, QL, axis=1).T


class Chronos2:
    def __init__(self, batch):
        from chronos import Chronos2Pipeline
        self.pipe = Chronos2Pipeline.from_pretrained(C.MODEL_IDS["chronos2"], device_map="cuda")

    def __call__(self, x):
        torch = _torch()
        q, _ = self.pipe.predict_quantiles([torch.tensor(v, device="cpu") for v in x], prediction_length=1,
                                           quantile_levels=QL)
        arr = np.stack([np.asarray(t.float().cpu() if hasattr(t, "cpu") else t) for t in q]) \
            if isinstance(q, (list, tuple)) else np.asarray(q.float().cpu() if hasattr(q, "cpu") else q)
        return arr.reshape(len(x), -1)[:, -len(QL):]


class TimesFM25:
    def __init__(self, batch):
        import timesfm
        from timesfm import TimesFM_2p5_200M_torch
        self.m = TimesFM_2p5_200M_torch.from_pretrained(C.MODEL_IDS["timesfm25"], torch_compile=False)
        self.m.compile(timesfm.ForecastConfig(max_context=256, max_horizon=128, normalize_inputs=True,
                                              use_continuous_quantile_head=True, per_core_batch_size=batch))

    def __call__(self, x):
        _, q = self.m.forecast(horizon=1, inputs=list(x))                   # (n, 1, 10): 평균, 0.1~0.9
        return np.asarray(q)[:, 0, 1:10]


class Moirai2:
    def __init__(self, batch):
        from uni2ts.model.moirai2 import Moirai2Module
        self.module = Moirai2Module.from_pretrained(C.MODEL_IDS["moirai2"]).to("cuda")
        ql = getattr(self.module, "quantile_levels", None)
        if ql is not None and [round(float(v), 2) for v in ql] != QL:
            raise RuntimeError(f"Moirai 분위수 수준이 다름: {ql}")
        self.cache = {}

    def __call__(self, x):
        torch = _torch()
        from uni2ts.model.moirai2 import Moirai2Forecast
        n, L = x.shape
        if L not in self.cache:
            m = Moirai2Forecast(prediction_length=1, target_dim=1, feat_dynamic_real_dim=0,
                                past_feat_dynamic_real_dim=0, context_length=L, module=self.module).to("cuda")
            m.eval()
            self.cache[L] = m
        pt = torch.tensor(x, dtype=torch.float32, device="cuda").unsqueeze(-1)
        with torch.no_grad():
            out = self.cache[L](past_target=pt, past_observed_target=torch.ones_like(pt, dtype=torch.bool),
                                past_is_pad=torch.zeros((n, L), dtype=torch.bool, device="cuda"))
        a = out.float().cpu().numpy()                                       # k03 확인: (n, 9, 1)
        if a.shape != (n, len(QL), 1):
            raise RuntimeError(f"Moirai 출력 형태가 준비작업과 다름: {a.shape}")
        return a[:, :, 0]


GPU_ADAPTERS = {"chronos_t5_base": ChronosT5, "chronos2": Chronos2, "timesfm25": TimesFM25, "moirai2": Moirai2}


def progress(done, total, t0, every=0.05):
    step = max(1, int(total * every))
    if done % step == 0 or done == total:
        el = time.time() - t0
        eta = el / done * (total - done)
        print(f"    {done}/{total} ({done/total*100:.0f}%) 경과 {el/60:.1f}분, 남은 예상 {eta/60:.1f}분", flush=True)


def run_gpu(adapter, X, batch):
    """배치 예측. 메모리 부족 오류 또는 9,500MB 초과 시 배치를 절반으로 줄여 계속."""
    torch = _torch()
    out, i, t0, nb = [], 0, time.time(), 0
    total_b = int(np.ceil(len(X) / batch))
    while i < len(X):
        torch.cuda.reset_peak_memory_stats()
        try:
            q = adapter(X[i:i + batch])
        except Exception as e:  # noqa: BLE001
            if ("out of memory" in str(e).lower() or isinstance(e, getattr(torch, "OutOfMemoryError", ()))) and batch > 1:
                torch.cuda.empty_cache()
                batch = max(1, batch // 2)
                print(f"    메모리 부족 → 배치 {batch}로 줄여 계속", flush=True)
                continue
            raise
        q = np.asarray(q, dtype=np.float64)
        if q.shape != (len(X[i:i + batch]), len(QL)):
            raise RuntimeError(f"출력 형태 이상: {q.shape}")
        out.append(q)
        i += len(q)
        nb += 1
        peak = torch.cuda.max_memory_allocated() / 2 ** 20
        if peak > C.VRAM_LIMIT_MB and batch > 1:
            batch = max(1, batch // 2)
            print(f"    GPU 메모리 {peak:.0f}MB > {C.VRAM_LIMIT_MB}MB → 이후 배치 {batch}", flush=True)
        if nb % max(1, total_b // 20) == 0:
            el = time.time() - t0
            print(f"    {i}/{len(X)} ({i/len(X)*100:.0f}%) 경과 {el/60:.1f}분, 남은 예상 {el/i*(len(X)-i)/60:.1f}분",
                  flush=True)
    return np.concatenate(out), batch


def to_return_space(q, anchor, kind):
    if kind == "return":
        return q
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.log(q / anchor[:, None])


def finalize(q, Y, M, fallback):
    nonfinite = ~np.isfinite(q).all(1)
    crossed = (np.diff(q, axis=1) < 0).any(1) & ~nonfinite
    qs = np.sort(q, axis=1)                         # 사전 고정: 교차 시 오름차순 재정렬
    df = M.copy()
    df["y"] = Y
    for k in range(len(QL)):
        df[f"q{k+1}"] = qs[:, k]
    df["crossed"], df["nonfinite"], df["fallback"] = crossed, nonfinite, fallback
    return df


def main(model, smoke, workers, datasets):
    T.verify_inputs()
    fp = T.synth_fingerprint()
    exp = json.loads((Path(__file__).parent / "synth_fingerprint_expected.json").read_text(encoding="utf-8"))
    for sc, v in exp.items():
        got = fp.loc[sc]
        if not (np.isclose(got["sum"], v["sum"], rtol=0, atol=1e-9) and np.isclose(got["sumsq"], v["sumsq"], rtol=1e-9)
                and int(got["n"]) == v["n"]):
            raise SystemExit(f"합성 데이터 지문 불일치({sc}) → 중단. 01을 다시 실행했는지 확인")
    out_dir = C.res_dir(smoke) / "raw"
    out_dir.mkdir(parents=True, exist_ok=True)
    log = C.res_dir(smoke) / "run_log.jsonl"
    adapter = None
    for L, kind in C.conditions(model):
        for ds in datasets:
            f = out_dir / f"{model}__L{L}_{kind}__{ds}.parquet"
            if f.exists():
                print(f"[건너뜀] {f.name} 이미 있음", flush=True)
                continue
            R, P, A, Y, M = T.tasks(ds, L, smoke)
            X = R if kind == "return" else P
            print(f"\n=== {model} L={L} {kind} {ds}: 예측 {len(X)}회 시작 {time.strftime('%H:%M:%S')} ===", flush=True)
            t0 = time.time()
            batch_used = None
            if model == "rw":
                q, fb = rw_quantiles(R)
            elif model == "garch_t":
                q, fb = garch_quantiles(R, workers, progress)
            else:
                torch = _torch()
                if adapter is None:
                    adapter = GPU_ADAPTERS[model](C.BATCH[(model, 252)])
                torch.manual_seed(C.SEED_BASE + L + (kind == "price"))    # Chronos 샘플 재현용
                q, batch_used = run_gpu(adapter, X, C.BATCH[(model, L)])
                fb = np.zeros(len(X), bool)
            q = to_return_space(q, A, kind)
            df = finalize(q, Y, M, fb)
            df.to_parquet(f, index=False)
            rec = {"model": model, "L": L, "input": kind, "dataset": ds, "n": len(df), "sec": round(time.time() - t0, 1),
                   "batch_start": C.BATCH.get((model, L)), "batch_end": batch_used,
                   "crossed_rate": float(df["crossed"].mean()), "nonfinite": int(df["nonfinite"].sum()),
                   "fallback": int(df["fallback"].sum()), "finished": time.strftime("%Y-%m-%d %H:%M:%S")}
            with open(log, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            print(f"[저장] {f.name}  {rec}", flush=True)
            del R, P, A, Y, M, X, q, df
            gc.collect()
            if model in GPU_ADAPTERS:
                _torch().cuda.empty_cache()
    print(f"\n[완료] {model} {time.strftime('%H:%M:%S')}", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=C.TSFM + C.BASELINES)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 2), help="GARCH 병렬 프로세스 수")
    ap.add_argument("--datasets", default="synth,real")
    a = ap.parse_args()
    print(f"python {platform.python_version()}, model={a.model}, smoke={a.smoke}", flush=True)
    main(a.model, a.smoke, a.workers, a.datasets.split(","))
