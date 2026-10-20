# -*- coding: utf-8 -*-
"""
post_t5fix_v4.py — 사후 분석: Chronos-T5의 샘플링 제한(top_k)을 풀고 수익률 조건을 다시 예측한 뒤,
                   본 실행과 같은 채점·보정(03)과 분석(07)을 그대로 돌린다. (미리 고정한 계획 밖, 결과와 무관하게 보고)
================================================================================================
배경: 사후 점검 e1에서 Chronos-T5 수익률 입력의 구간 붕괴가 기본 샘플링 설정(top_k=50) 때문임을 확인.
      가격 입력은 top_k와 무관(합성 L1 75.34% ↔ 75.35%)하므로 수익률 조건 2개만 다시 예측한다.
바뀌는 것은 Chronos-T5의 top_k(50 → 어휘 전체 4,096) 하나뿐이다. 과제·난수 시드·배치·후처리는 02와 같다.

실행 (04_실험코드/src_v4_post 에서, 순서대로):
  python post_t5fix_v4.py infer   [--smoke]   GPU. 합성 17개 시나리오 + 실제 10종목, L=21·252, 수익률 입력
  python post_t5fix_v4.py assemble [--smoke]  나머지 모델·조건의 본 실행 예측 파일을 그대로 복사
  python post_t5fix_v4.py score    [--smoke]  src_v4/03_score_calibrate_v4.py 를 결과 폴더만 바꿔 실행
  python post_t5fix_v4.py analyze  [--smoke]  src_v4/07_analysis_v4.py 를 결과 폴더만 바꿔 실행
출력: results_v4_t5fix/ (스모크는 results_v4_t5fix_smoke/) — raw/, scored_v4.parquet, tables/
"""
import argparse
import importlib.util
import json
import shutil
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "src_v4"
sys.path.insert(0, str(SRC))
import config_v4 as C  # noqa: E402
import tasks_v4 as T  # noqa: E402

MODEL = "chronos_t5_base"
CONDS = [(21, "return"), (252, "return")]


def load(name):
    spec = importlib.util.spec_from_file_location(name.replace(".py", ""), SRC / name)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def out_dir(smoke):
    return C.ROOT / ("results_v4_t5fix_smoke" if smoke else "results_v4_t5fix")


def patch(smoke):
    """03·07이 쓰는 결과 폴더만 바꾼다(코드는 그대로)."""
    C.res_dir = lambda s=False: out_dir(smoke)


def infer(smoke):
    R02 = load("02_run_inference_v4.py")
    torch = R02._torch()
    full = None

    class ChronosT5All(R02.ChronosT5):
        def __call__(self, x):
            s = self.pipe.predict(torch.tensor(x, dtype=torch.float32), prediction_length=1,
                                  num_samples=C.CHRONOS_SAMPLES, top_k=full)
            s = s.float().cpu().numpy()[:, :, 0]
            return np.quantile(s, C.QLEVELS, axis=1).T

    raw = out_dir(smoke) / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    log = out_dir(smoke) / "run_log.jsonl"
    adapter = None
    for L, kind in CONDS:
        for ds in ["synth", "real"]:
            f = raw / f"{MODEL}__L{L}_{kind}__{ds}.parquet"
            if f.exists():
                print(f"[건너뜀] {f.name} 이미 있음", flush=True)
                continue
            R, P, A, Y, M = T.tasks(ds, L, smoke)
            X = R if kind == "return" else P
            if adapter is None:
                adapter = ChronosT5All(C.BATCH[(MODEL, 252)])
                full = int(adapter.pipe.model.config.n_tokens)
                print(f"[설정] top_k: 기본 {adapter.pipe.model.config.top_k} → {full} (어휘 전체)", flush=True)
            print(f"\n=== {MODEL}(top_k={full}) L={L} {kind} {ds}: 예측 {len(X)}회 시작 {time.strftime('%H:%M:%S')} ===",
                  flush=True)
            t0 = time.time()
            torch.manual_seed(C.SEED_BASE + L + (kind == "price"))        # 02와 같은 시드 규칙
            q, batch_used = R02.run_gpu(adapter, X, C.BATCH[(MODEL, L)])
            q = R02.to_return_space(q, A, kind)
            df = R02.finalize(q, Y, M, np.zeros(len(X), bool))
            df.to_parquet(f, index=False)
            rec = {"model": MODEL, "top_k": full, "L": L, "input": kind, "dataset": ds, "n": len(df),
                   "sec": round(time.time() - t0, 1), "batch_end": batch_used,
                   "crossed_rate": float(df["crossed"].mean()), "nonfinite": int(df["nonfinite"].sum()),
                   "coverage": float(((df["y"] >= df["q1"]) & (df["y"] <= df["q9"])).mean()),
                   "finished": time.strftime("%Y-%m-%d %H:%M:%S")}
            with open(log, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            print(f"[저장] {f.name}  {rec}", flush=True)
            torch.cuda.empty_cache()
    print(f"\n[완료] infer {time.strftime('%H:%M:%S')}", flush=True)


def assemble(smoke):
    src = C.res_dir(smoke) / "raw"
    dst = out_dir(smoke) / "raw"
    dst.mkdir(parents=True, exist_ok=True)
    mine = {f"{MODEL}__L{L}_{k}__{ds}.parquet" for L, k in CONDS for ds in ["synth", "real"]}
    missing = [m for m in mine if not (dst / m).exists()]
    if missing:
        raise SystemExit(f"새 예측 파일이 없음 → infer 먼저: {missing}")
    n = 0
    for f in sorted(src.glob("*.parquet")):
        if f.name in mine:
            continue
        shutil.copy2(f, dst / f.name)
        n += 1
    print(f"[복사] 본 실행 예측 {n}개 → {dst}  (새 예측 {len(mine)}개는 그대로 둠)", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["infer", "assemble", "score", "analyze"])
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    T.verify_inputs()
    print(f"python {sys.version.split()[0]}, step={a.step}, smoke={a.smoke}, 시작 {time.strftime('%H:%M:%S')}", flush=True)
    if a.step == "infer":
        infer(a.smoke)
    elif a.step == "assemble":
        assemble(a.smoke)
    elif a.step == "score":
        patch(a.smoke)
        load("03_score_calibrate_v4.py").main(a.smoke)
    else:
        patch(a.smoke)
        load("07_analysis_v4.py").main(a.smoke)
    print(f"[완료] {a.step} {time.strftime('%H:%M:%S')}", flush=True)
