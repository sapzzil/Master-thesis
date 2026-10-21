# -*- coding: utf-8 -*-
"""
post_checks2_v4.py — Chronos-T5 추가 사후 점검 (미리 고정한 계획 밖, 결과와 무관하게 모두 보고)
==================================================================================
  e4  원 논문(Ansari 외, 2024 그림 12a) 조건에 가까운 과거 길이 512에서 정규분포 계열 점검(계열 30개, 배치 1:
      표본 200개가 과거 512일과 함께 메모리에 올라가 배치 4에서는 GPU 메모리가 넘쳐 100배 가까이 느려짐)
      - 독립 N(0,1), 독립 N(100,10²) : 기본 샘플링(top-k 50) 대 제한 해제(어휘 전체)
  e5  표본 수 점검: 합성 L1·과거 252일·수익률·제한 해제에서 표본 200개 대 1,000개 (계열 25개)
실행:  python post_checks2_v4.py --exp e4 [--smoke]   (04_실험코드/src_v4_post 에서)
출력:  results_v4_post/raw/{exp}__{variant}.parquet, results_v4_post/summary_{exp}.csv, run_log.jsonl
post_checks_v4.py의 공통 함수(채점·저장·과제)를 그대로 쓴다.
"""
import argparse
import json
import sys
import time

import numpy as np
import pandas as pd

import post_checks_v4 as P

C, T = P.C, P.T


def gauss(mu, sd, L, smoke):
    rng = np.random.default_rng(P.SEED + 512 + int(mu))
    n = 3 if smoke else 30                       # 과거 512일은 계산이 무거워 계열 30개(예측 2,400회)
    x = (mu + sd * rng.standard_normal((n, L + C.EP_LEN))).astype(np.float32)
    days = np.arange(C.EP_LEN)
    idx = (L + days)[:, None] + np.arange(-L, 0)[None, :]
    X = np.concatenate([s[idx] for s in x])
    Y = np.concatenate([s[L + days] for s in x]).astype(float)
    M = pd.DataFrame({"dataset": f"gauss{int(mu)}", "unit": np.repeat(np.arange(n), C.EP_LEN).astype(str),
                      "day": np.tile(days + 1, n)})
    return X, Y, M


def main(exp, smoke):
    torch = P.torch_()
    from chronos import ChronosPipeline
    pipe = ChronosPipeline.from_pretrained(C.MODEL_IDS["chronos_t5_base"], device_map="cuda", torch_dtype=torch.bfloat16)
    full = int(pipe.model.config.n_tokens)
    print(f"[설정] n_tokens={full}, 기본 top_k={pipe.model.config.top_k}, context_length={pipe.model.config.context_length}",
          flush=True)

    def fc(x, top_k=None, ns=C.CHRONOS_SAMPLES):
        kw = {} if top_k is None else {"top_k": top_k}
        s = pipe.predict(torch.tensor(x, dtype=torch.float32), prediction_length=1, num_samples=ns, **kw)
        return np.quantile(s.float().cpu().numpy()[:, :, 0], P.QL, axis=1).T

    def run(variant, X, Y, M, batch, extra, **kw):
        if (P.RAW / f"{exp}__{variant}.parquet").exists():
            print(f"[건너뜀] {exp}__{variant}", flush=True)
            return
        torch.manual_seed(P.SEED)
        print(f"\n=== {exp} {variant}: {len(X)}회 {extra} ===", flush=True)
        q = P.batched(fc, X, batch, **kw)
        P.save(exp, variant, M, Y, q, extra)

    if exp == "e4":
        L = 64 if smoke else 512
        for mu, sd, name in [(0.0, 1.0, "N01"), (100.0, 10.0, "N100")]:
            X, Y, M = gauss(mu, sd, L, smoke)
            run(f"{name}_L{L}_default", X, Y, M, 1, {"L": L, "top_k": 50})
            if name == "N01":
                run(f"{name}_L{L}_topkall", X, Y, M, 1, {"L": L, "top_k": full}, top_k=full)
    else:
        L = 21 if smoke else 252
        R, P_, A, Y, M = P.synth_L1(L, smoke)
        k = M["unit"].astype(int) < (2 if smoke else 25)
        R, Y, M = R[k.to_numpy()], Y[k.to_numpy()], M[k].reset_index(drop=True)
        run(f"L1_return_L{L}_topkall_s200", R, Y, M, 4, {"L": L, "top_k": full, "samples": 200}, top_k=full, ns=200)
        run(f"L1_return_L{L}_topkall_s1000", R, Y, M, 1, {"L": L, "top_k": full, "samples": 1000}, top_k=full, ns=1000)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--exp", required=True, choices=["e4", "e5"])
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        P.OUT = C.ROOT / "results_v4_post_smoke"
        P.RAW = P.OUT / "raw"
    P.OUT.mkdir(parents=True, exist_ok=True)
    T.verify_inputs()
    print(f"python {sys.version.split()[0]}, exp={a.exp}, smoke={a.smoke}, 시작 {time.strftime('%H:%M:%S')}", flush=True)
    main(a.exp, a.smoke)
    P.summarize(a.exp)
    print(f"\n[완료] {a.exp} {time.strftime('%H:%M:%S')}", flush=True)
