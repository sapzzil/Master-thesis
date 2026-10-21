# -*- coding: utf-8 -*-
"""
post_checks3_v4.py — 추가 점검 g1: Chronos-2의 극단 분위수로 90%·98% 구간 커버리지 확인
==========================================================================================
목적: 4.3.2절의 주장("꼬리가 두꺼우면 80% 구간 커버리지는 오르지만 99% 근처 구간에서는 반대로 내려간다")을
      이론 계산이 아니라 실제 모델 출력으로 확인한다. 네 모델 중 Chronos-2만 0.01~0.99 분위수를 직접 낸다.
방법: 본 실행(src_v4/02)과 같은 과제·같은 Chronos-2 호출로, 분위수 수준만 21개로 늘려 다시 예측한다.
      과제·데이터·배치는 02와 같다. 새 예측의 0.1·0.9 분위수가 본 실행과 같은지 먼저 확인한다(재현 점검).

실행 (04_실험코드/src_v4_post 에서):
  python post_checks3_v4.py env                 # 환경 점검(패키지 버전, GPU, 합성 데이터 지문) — GPU 안 씀
  python post_checks3_v4.py run --smoke         # 스모크: 작은 과제로 전 조건 1회씩, 소요 시간 측정
  python post_checks3_v4.py run                 # 본 실행: 합성 17개 시나리오 + 실제 10종목, 4개 조건
  python post_checks3_v4.py summary [--smoke]   # 커버리지 요약과 재현 점검 출력(CPU)
출력: results_v4_post/raw/g1__chronos2__L{L}_{input}__{dataset}.parquet (스모크는 results_v4_post_smoke/)
      results_v4_post/summary_g1.csv, results_v4_post/g1_repro.csv, results_v4_post/run_log.jsonl
      이미 있는 파일은 건너뛴다(중간에 끊겨도 다시 실행하면 이어서 함).
"""
import argparse
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "src_v4"
sys.path.insert(0, str(SRC))
import config_v4 as C  # noqa: E402
import tasks_v4 as T  # noqa: E402

QL21 = [0.01, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5,
        0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 0.99]
COLS = [f"p{int(round(q * 100)):02d}" for q in QL21]          # p01, p05, ..., p99
INTERVALS = {"80": ("p10", "p90"), "90": ("p05", "p95"), "98": ("p01", "p99")}
MODEL = "chronos2"


def out_root(smoke):
    return HERE.parent / ("results_v4_post_smoke" if smoke else "results_v4_post")


# ------------------------------------------------------------------ 환경 점검
def env():
    import torch
    print(f"python {platform.python_version()}")
    print(f"torch {torch.__version__}, CUDA 사용 가능 {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        p = torch.cuda.get_device_properties(0)
        print(f"GPU {p.name}, 메모리 {p.total_memory / 2**30:.1f}GB")
    for pkg in ["chronos-forecasting", "numpy", "pandas", "scipy", "pyarrow"]:
        r = subprocess.run([sys.executable, "-m", "pip", "show", pkg], capture_output=True, text=True)
        v = [ln for ln in r.stdout.splitlines() if ln.startswith("Version:")]
        print(f"{pkg}: {v[0].split(': ')[1] if v else '설치 안 됨'}")
    T.verify_inputs()
    fp = T.synth_fingerprint()
    exp = json.loads((SRC / "synth_fingerprint_expected.json").read_text(encoding="utf-8"))
    bad = [sc for sc, v in exp.items()
           if not (np.isclose(fp.loc[sc]["sum"], v["sum"], rtol=0, atol=1e-9)
                   and np.isclose(fp.loc[sc]["sumsq"], v["sumsq"], rtol=1e-9) and int(fp.loc[sc]["n"]) == v["n"])]
    print("합성 데이터 지문: " + ("일치(17개 시나리오)" if not bad else f"불일치 {bad}"))
    main_raw = C.res_dir(False) / "raw"
    have = sorted(p.name for p in main_raw.glob("chronos2__*.parquet")) if main_raw.exists() else []
    print(f"본 실행 Chronos-2 예측 파일: {len(have)}개 (재현 점검용, 8개면 정상)")


# ------------------------------------------------------------------ 예측
class Chronos2Q21:
    def __init__(self):
        from chronos import Chronos2Pipeline
        self.pipe = Chronos2Pipeline.from_pretrained(C.MODEL_IDS[MODEL], device_map="cuda")

    def __call__(self, x):
        import torch
        q, _ = self.pipe.predict_quantiles([torch.tensor(v, device="cpu") for v in x], prediction_length=1,
                                           quantile_levels=QL21)
        arr = np.stack([np.asarray(t.float().cpu() if hasattr(t, "cpu") else t) for t in q]) \
            if isinstance(q, (list, tuple)) else np.asarray(q.float().cpu() if hasattr(q, "cpu") else q)
        return arr.reshape(len(x), -1)[:, -len(QL21):]


def predict(adapter, X, batch):
    import torch
    out, i, t0 = [], 0, time.time()
    report = max(1, len(X) // 10)
    nxt = report
    while i < len(X):
        try:
            q = adapter(X[i:i + batch])
        except Exception as e:  # noqa: BLE001
            if "out of memory" in str(e).lower() and batch > 1:
                torch.cuda.empty_cache()
                batch = max(1, batch // 2)
                print(f"    메모리 부족 → 배치 {batch}로 줄여 계속", flush=True)
                continue
            raise
        q = np.asarray(q, dtype=np.float64)
        if q.shape != (len(X[i:i + batch]), len(QL21)):
            raise RuntimeError(f"출력 형태 이상: {q.shape}")
        out.append(q)
        i += len(q)
        if i >= nxt or i == len(X):
            el = time.time() - t0
            print(f"    {i}/{len(X)} ({i / len(X) * 100:.0f}%) 경과 {el / 60:.1f}분, "
                  f"남은 예상 {el / i * (len(X) - i) / 60:.1f}분", flush=True)
            nxt += report
    return np.concatenate(out)


def run(smoke):
    import torch
    root = out_root(smoke)
    raw = root / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    gpu = torch.cuda.get_device_properties(0).name
    print(f"[설정] 모델 {C.MODEL_IDS[MODEL]}, 분위수 {len(QL21)}개, GPU {gpu}, 스모크 {smoke}", flush=True)
    adapter = None
    for L in C.CONTEXTS:
        for kind in C.INPUTS:
            for ds in ["synth", "real"]:
                f = raw / f"g1__{MODEL}__L{L}_{kind}__{ds}.parquet"
                if f.exists():
                    print(f"[건너뜀] {f.name} 이미 있음", flush=True)
                    continue
                R, P, A, Y, M = T.tasks(ds, L, smoke)
                X = R if kind == "return" else P
                print(f"\n=== g1 L={L} {kind} {ds}: 예측 {len(X)}회 시작 {time.strftime('%H:%M:%S')} ===", flush=True)
                if adapter is None:
                    adapter = Chronos2Q21()
                t0 = time.time()
                q = predict(adapter, X, C.BATCH[(MODEL, L)])
                if kind == "price":
                    with np.errstate(divide="ignore", invalid="ignore"):
                        q = np.log(q / A[:, None])
                nonfinite = ~np.isfinite(q).all(1)
                crossed = (np.diff(q, axis=1) < 0).any(1) & ~nonfinite
                qs = np.sort(q, axis=1)
                df = M.copy()
                df["y"] = Y
                for k, c in enumerate(COLS):
                    df[c] = qs[:, k]
                df["crossed"], df["nonfinite"] = crossed, nonfinite
                df.to_parquet(f, index=False)
                sc = df["in_main"] & (df["day"] > C.EP_WARM)
                covs = {k: float(((df.y >= df[a]) & (df.y <= df[b]))[sc].mean()) for k, (a, b) in INTERVALS.items()}
                rec = {"exp": "g1", "L": L, "input": kind, "dataset": ds, "n": len(df), "n_scored": int(sc.sum()),
                       "sec": round(time.time() - t0, 1), "gpu": gpu, "crossed_rate": float(crossed.mean()),
                       "nonfinite": int(nonfinite.sum()), **{f"cov{k}": v for k, v in covs.items()},
                       "finished": time.strftime("%Y-%m-%d %H:%M:%S")}
                with open(root / "run_log.jsonl", "a", encoding="utf-8") as fh:
                    fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                print(f"[저장] {f.name}: 커버리지 80% {covs['80']*100:.1f}, 90% {covs['90']*100:.1f}, "
                      f"98% {covs['98']*100:.1f}  (채점 {rec['n_scored']}건, {rec['sec'] / 60:.1f}분)", flush=True)
                del R, P, A, Y, M, X, q, df
                torch.cuda.empty_cache()
    print(f"\n[완료] g1 {time.strftime('%H:%M:%S')}", flush=True)


# ------------------------------------------------------------------ 요약(CPU)
def summary(smoke):
    root = out_root(smoke)
    rows, rep = [], []
    for f in sorted((root / "raw").glob("g1__*.parquet")):
        d = pd.read_parquet(f)
        L = int(f.name.split("__L")[1].split("_")[0])
        kind = f.name.split("__L")[1].split("_")[1]
        ds = f.name.rsplit("__", 1)[1].replace(".parquet", "")
        sc = d["in_main"] & (d["day"] > C.EP_WARM)
        key = "scenario" if ds == "synth" else None
        groups = d[sc].groupby("scenario") if key else [("real", d[sc])]
        for name, g in groups:
            r = {"L": L, "input": kind, "dataset": ds, "scenario": name, "n": len(g)}
            for k, (a, b) in INTERVALS.items():
                r[f"cov{k}"] = round(((g.y >= g[a]) & (g.y <= g[b])).mean() * 100, 2)
            rows.append(r)
        # 재현 점검: 본 실행의 0.1·0.9 분위수와 비교
        mf = C.res_dir(False) / "raw" / f"{MODEL}__L{L}_{kind}__{ds}.parquet"
        if mf.exists():
            m = pd.read_parquet(mf)
            if len(m) == len(d):
                dq = max(np.nanmax(np.abs(m["q1"].to_numpy() - d["p10"].to_numpy())),
                         np.nanmax(np.abs(m["q9"].to_numpy() - d["p90"].to_numpy())))
                cm = ((m.y >= m.q1) & (m.y <= m.q9))[sc].mean() * 100
                cn = ((d.y >= d.p10) & (d.y <= d.p90))[sc].mean() * 100
                rep.append({"L": L, "input": kind, "dataset": ds, "max_abs_diff_q10_q90": dq,
                            "cov80_main": round(cm, 3), "cov80_g1": round(cn, 3)})
            else:
                rep.append({"L": L, "input": kind, "dataset": ds, "note": f"행 수 다름 {len(m)} vs {len(d)}"})
        else:
            rep.append({"L": L, "input": kind, "dataset": ds, "note": "본 실행 파일 없음"})
    s = pd.DataFrame(rows)
    s.to_csv(root / "summary_g1.csv", index=False, encoding="utf-8-sig")
    r = pd.DataFrame(rep)
    r.to_csv(root / "g1_repro.csv", index=False, encoding="utf-8-sig")
    pd.set_option("display.width", 200)
    print("[재현 점검] 본 실행 대비 0.1·0.9 분위수 최대 차이와 80% 커버리지")
    print(r.to_string(index=False))
    print("\n[요약] 조건별 커버리지(%) — 합성은 L1과 각 축 L5만 표시")
    show = s[(s.dataset == "real") | s.scenario.astype(str).str.contains("L1|L5")]
    print(show.to_string(index=False))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["env", "run", "summary"])
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    print(f"[시작] {a.cmd} smoke={a.smoke} {time.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
    if a.cmd == "env":
        env()
    elif a.cmd == "run":
        run(a.smoke)
    else:
        summary(a.smoke)
