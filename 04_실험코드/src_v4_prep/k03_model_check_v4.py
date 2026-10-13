# -*- coding: utf-8 -*-
"""
k03_model_check_v4.py — v4 준비: 모델 동작 확인 + 1회 예측 시간 측정 + 전체 시간 추정
=====================================================================================
v4 본 실험과 같은 형태(내일 1일 예측, 과거 21/252일, 입력 = 로그수익률 또는 가격)로
각 모델을 '가짜 데이터'에 돌려 다음을 확인한다.
  (1) 모델이 오류 없이 돌아가는가, 출력 형태는 무엇인가 (분위수 0.1~0.9를 얻을 수 있는가)
  (2) 출력이 정상인가: 유한값 비율, 분위수가 오름차순인 비율 (성능·커버리지는 계산하지 않음)
  (3) 1회 예측 시간과 GPU 메모리 → 본 실험 전체 소요시간 추정
금지: 실제 주가 사용, 커버리지·정확도 계산 (사전등록 보호)

실행:  conda activate thesis_v4
       python 04_실험코드/src_v4_prep/k03_model_check_v4.py            # 전체
       python 04_실험코드/src_v4_prep/k03_model_check_v4.py --only timesfm25   # 한 모델만
출력 (data/raw_v4/):
  model_check_v4.csv    모델 × 조건별 상태·배치크기·1회 시간·메모리·출력 점검
  projection_v4.csv     본 실험 예측 횟수 × 1회 시간 = 모델별 예상 시간, 축소 규칙 적용 결과(제안)
  env_v4.txt            GPU·패키지 버전

어댑터(모델 호출부)가 공식 API와 달라 오류가 나면: 해당 어댑터 함수 '안쪽'만 고치고,
무엇을 왜 바꿨는지 보고서에 그대로 적을 것. 측정 로직·데이터 생성·출력 형식은 고치지 말 것.
"""
import argparse
import gc
import importlib
import platform
import time
import traceback
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "raw_v4"
OUT.mkdir(parents=True, exist_ok=True)

QLEVELS = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
CONTEXTS = [21, 252]
INPUTS = ["return", "price"]
N_TIME = 1000            # 조건당 시간 측정용 예측 횟수 (느린 모델은 자동으로 200)
CHRONOS_SAMPLES = 200
# 본 실험 예측 횟수 (계획서 v4 §9): 합성 17 시나리오 × 100 계열 × 80일 + 실제 10종목 × 약 2,430일
N_PER_RUN = 17 * 100 * 80 + 10 * 2430
N_CONDITIONS = len(CONTEXTS) * len(INPUTS)


# ---------------------------------------------------------------- 가짜 데이터 (실제 주가 아님)
def fake_batch(n, ctx, seed):
    rng = np.random.default_rng(seed)
    r = rng.standard_t(5, size=(n, ctx)) * 0.018 / np.sqrt(5 / 3)   # 두꺼운 꼬리 가짜 수익률
    p = 100.0 * np.exp(np.cumsum(r, axis=1))
    return r.astype(np.float32), p.astype(np.float32)


# ---------------------------------------------------------------- 어댑터: (n, ctx) 배열 → (n, 9) 분위수 (입력과 같은 단위)
def _torch():
    import torch
    return torch


def _cuda_ok():
    try:
        return _torch().cuda.is_available()
    except Exception:  # noqa: BLE001
        return False


class ChronosT5:
    def __init__(self, size):
        torch = _torch()
        from chronos import ChronosPipeline
        self.model_id = f"amazon/chronos-t5-{size}"
        self.pipe = ChronosPipeline.from_pretrained(self.model_id, device_map="cuda", torch_dtype=torch.bfloat16)
        self.variant = "ChronosPipeline.predict(num_samples=200) → np.quantile"

    def __call__(self, x):
        torch = _torch()
        s = self.pipe.predict(torch.tensor(x, dtype=torch.float32), prediction_length=1,
                              num_samples=CHRONOS_SAMPLES)          # (n, S, 1)
        s = s.float().cpu().numpy()[:, :, 0]
        return np.quantile(s, QLEVELS, axis=1).T


class Chronos2:
    def __init__(self):
        from chronos import Chronos2Pipeline
        self.model_id = "amazon/chronos-2"
        self.pipe = Chronos2Pipeline.from_pretrained(self.model_id, device_map="cuda")
        self.variant = None

    def __call__(self, x):
        torch = _torch()
        # 이전 시험(k02)의 'cannot pin torch.cuda.FloatTensor' 오류는 입력 텐서가 GPU에 만들어졌다는 뜻.
        # 다른 라이브러리가 기본 장치를 cuda로 바꿨을 수 있어 기록하고, 입력은 명시적으로 CPU에 만든다.
        get_dev = getattr(torch, "get_default_device", None)
        self.default_device = str(get_dev()) if get_dev else "unknown"
        tries = [
            ("list of 1D CPU tensors", lambda: [torch.tensor(v, device="cpu") for v in x]),
            ("3D numpy (n,1,ctx)", lambda: x[:, None, :]),
            ("list of 1D numpy", lambda: [v for v in x]),
        ]
        last = None
        for name, make in tries:
            if self.variant is not None and name != self.variant:
                continue
            try:
                q, _ = self.pipe.predict_quantiles(make(), prediction_length=1, quantile_levels=QLEVELS)
                arr = np.stack([np.asarray(t.float().cpu() if hasattr(t, "cpu") else t) for t in q]) \
                    if isinstance(q, (list, tuple)) else np.asarray(q.float().cpu() if hasattr(q, "cpu") else q)
                arr = arr.reshape(len(x), -1)[:, -len(QLEVELS):]
                self.variant = name
                return arr
            except Exception as e:  # noqa: BLE001
                last = e
        raise last


class TimesFM25:
    def __init__(self, batch):
        import timesfm
        from timesfm import TimesFM_2p5_200M_torch
        self.model_id = "google/timesfm-2.5-200m-pytorch"
        self.m = TimesFM_2p5_200M_torch.from_pretrained(self.model_id, torch_compile=False)
        try:   # 모델 카드 예시 설정
            self.m.compile(timesfm.ForecastConfig(max_context=256, max_horizon=128, normalize_inputs=True,
                                                  use_continuous_quantile_head=True, per_core_batch_size=batch))
            self.variant = "ForecastConfig(normalize_inputs=True, use_continuous_quantile_head=True)"
        except TypeError:   # 이전 시험(k02)에서 동작한 설정
            self.m.compile(timesfm.ForecastConfig(max_context=256, max_horizon=128, per_core_batch_size=batch))
            self.variant = "ForecastConfig(default, k02)"

    def __call__(self, x):
        _, q = self.m.forecast(horizon=1, inputs=list(x))       # q: (n, h, 10) = 평균, 10~90% 분위
        q = np.asarray(q)
        return q[:, 0, 1:10]


class Moirai2:
    def __init__(self):
        from uni2ts.model.moirai2 import Moirai2Module
        self.model_id = "Salesforce/moirai-2.0-R-small"
        self.module = Moirai2Module.from_pretrained(self.model_id).to("cuda")
        self.cache = {}
        self.variant = "Moirai2Forecast.forward(past_target, past_observed_target, past_is_pad)"
        self.qlevels_attr = getattr(self.module, "quantile_levels", None)

    def __call__(self, x):
        torch = _torch()
        from uni2ts.model.moirai2 import Moirai2Forecast
        n, ctx = x.shape
        if ctx not in self.cache:
            m = Moirai2Forecast(prediction_length=1, target_dim=1, feat_dynamic_real_dim=0,
                                past_feat_dynamic_real_dim=0, context_length=ctx, module=self.module).to("cuda")
            m.eval()
            self.cache[ctx] = m
        pt = torch.tensor(x, dtype=torch.float32, device="cuda").unsqueeze(-1)
        with torch.no_grad():
            out = self.cache[ctx](past_target=pt, past_observed_target=torch.ones_like(pt, dtype=torch.bool),
                                  past_is_pad=torch.zeros((n, ctx), dtype=torch.bool, device="cuda"))
        a = out.float().cpu().numpy()
        self.last_shape = a.shape
        # 분위수 축(크기 9)을 찾아 (n, 9)로 정리
        axes = [i for i, s in enumerate(a.shape) if s == len(QLEVELS) and i != 0]
        if not axes:
            raise RuntimeError(f"출력에서 분위수 9개 축을 찾지 못함: shape={a.shape}")
        a = np.moveaxis(a, axes[0], -1).reshape(n, -1, len(QLEVELS))[:, 0, :]
        return a


class GarchT:
    """기준 모형(CPU). 계획서상 과거 252일·수익률 입력에서만 쓰이지만 측정은 같은 틀로 한다."""
    def __init__(self):
        self.model_id = "arch GARCH(1,1)-t"
        self.variant = "arch_model(r*100, vol=GARCH, dist=t).fit → 1일 조건부 분포 분위수"

    def __call__(self, x):
        from arch import arch_model
        from scipy import stats
        out = np.empty((len(x), len(QLEVELS)))
        for i, r in enumerate(x):
            res = arch_model(r.astype(float) * 100, vol="GARCH", p=1, q=1, dist="t", rescale=False).fit(disp="off", show_warning=False)
            f = res.forecast(horizon=1, reindex=False)
            mu, var = f.mean.values[-1, 0], f.variance.values[-1, 0]
            nu = res.params["nu"]
            sc = np.sqrt(var * (nu - 2) / nu)
            out[i] = (mu + sc * stats.t.ppf(QLEVELS, nu)) / 100
        return out


MODELS = {   # 빠른 모델부터 (중간에 끊겨도 결과가 남도록)
    "moirai2": lambda b: Moirai2(),
    "timesfm25": lambda b: TimesFM25(b),
    "chronos2": lambda b: Chronos2(),
    "chronos_t5_base": lambda b: ChronosT5("base"),
    "chronos_t5_large": lambda b: ChronosT5("large"),
    "garch_t": lambda b: GarchT(),
}
TRIAL_LIMIT_SEC = 120  # 배치 시험 1회가 이보다 오래 걸리면 더 작은 배치
VRAM_LIMIT_MB = 9500   # 이보다 크면 Windows 'Sysmem Fallback'(일반 RAM 차용)으로 보고 더 작은 배치로 내림
BATCH_TRY = {"chronos_t5_large": [16, 8, 4, 2, 1], "chronos_t5_base": [64, 32, 16, 8, 4, 1],
             "chronos2": [256, 64], "timesfm25": [256, 64], "moirai2": [256, 64], "garch_t": [50]}


# ---------------------------------------------------------------- 측정
def to_return_space(q, p_last, kind):
    if kind == "return":
        return q
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.log(q / p_last[:, None])


def run_condition(adapter, key, ctx, kind, batch):
    r, p = fake_batch(N_TIME, ctx, seed=ctx * 10 + (kind == "price"))
    x = r if kind == "return" else p
    p_last = p[:, -1]
    adapter(x[:batch])                                    # 워밍업
    torch = _torch()
    torch.cuda.synchronize()
    torch.cuda.reset_peak_memory_stats()
    n = N_TIME
    t0 = time.perf_counter()
    outs, done = [], 0
    while done < n:
        outs.append(adapter(x[done:done + batch]))
        done += len(outs[-1])
        if len(outs) == 1:
            first = (time.perf_counter() - t0) / done
            if first > 1.0:                                # 매우 느리면 50회만
                n = min(n, max(50, batch))
            elif first > 0.2:                              # 느리면 200회만
                n = min(n, max(200, batch))
    torch.cuda.synchronize()
    sec = (time.perf_counter() - t0) / done
    n = done
    q = to_return_space(np.concatenate(outs)[:n], p_last[:n], kind)
    fin = np.isfinite(q).all(axis=1)
    mono = (np.diff(q, axis=1) >= -1e-9).all(axis=1)
    return {"sec_per_forecast": sec, "n_timed": n, "peak_mem_mb": torch.cuda.max_memory_allocated() / 2**20,
            "finite_ratio": fin.mean(), "monotone_ratio": (mono & fin).mean(),
            "q10_mean": np.nanmean(q[:, 0]), "q50_mean": np.nanmean(q[:, 4]), "q90_mean": np.nanmean(q[:, 8])}


def _is_oom(e):
    torch = _torch()
    return isinstance(e, getattr(torch, "OutOfMemoryError", ())) or "out of memory" in str(e).lower()


def pick_batch(key, adapter, ctx, kind):
    """GPU 메모리(10GB)를 넘지 않는 가장 큰 배치를 찾는다. 넘침(일반 RAM 차용)도 실패로 본다."""
    torch = _torch()
    for b in BATCH_TRY[key]:
        r, p = fake_batch(b, ctx, seed=1)
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()
        try:
            t0 = time.perf_counter()
            adapter(r if kind == "return" else p)
            el = time.perf_counter() - t0
            peak = torch.cuda.max_memory_allocated() / 2**20
            if peak > VRAM_LIMIT_MB:
                print(f"    배치 {b}: 최대 메모리 {peak:.0f}MB > {VRAM_LIMIT_MB}MB → 더 작은 배치", flush=True)
                continue
            if el > TRIAL_LIMIT_SEC and b != BATCH_TRY[key][-1]:
                print(f"    배치 {b}: 시험 1회 {el:.0f}초 > {TRIAL_LIMIT_SEC}초 → 더 작은 배치", flush=True)
                continue
            return b
        except Exception as e:  # noqa: BLE001
            if not _is_oom(e):
                raise
        torch.cuda.empty_cache()
        gc.collect()
    raise RuntimeError(f"배치 1에서도 메모리 {VRAM_LIMIT_MB}MB 초과 또는 OOM")


def save_rows(rows, only):
    df = pd.DataFrame(rows)
    path = OUT / "model_check_v4.csv"
    if only and path.exists():
        old = pd.read_csv(path)
        df = pd.concat([old[old["model"] != only], df], ignore_index=True)
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return df


def main(only):
    torch = _torch()
    env = [f"python {platform.python_version()}", f"torch {torch.__version__}, cuda {torch.version.cuda}"]
    if torch.cuda.is_available():
        pr = torch.cuda.get_device_properties(0)
        env.append(f"GPU {pr.name}, total {pr.total_memory / 2**30:.1f} GiB")
    for pkg in ["chronos", "timesfm", "uni2ts", "transformers", "pykrx", "FinanceDataReader", "arch"]:
        try:
            mod = importlib.import_module(pkg)
            env.append(f"{pkg} {getattr(mod, '__version__', '?')}")
        except Exception as e:  # noqa: BLE001
            env.append(f"{pkg} 불러오기 실패: {e}")
    (OUT / "env_v4.txt").write_text("\n".join(env), encoding="utf-8")
    print("\n".join(env))

    rows = []
    for key, make in MODELS.items():
        if only and key != only:
            continue
        print(f"\n=== {key} 시작 {time.strftime('%H:%M:%S')} ===", flush=True)
        adapter, load_err = None, None
        try:
            adapter = make(BATCH_TRY[key][0])          # 모델은 한 번만 불러옴
        except Exception as e:  # noqa: BLE001
            load_err = f"LOAD ERR {type(e).__name__}: {str(e)[:300]}"
            traceback.print_exc()
        for ctx in CONTEXTS:
            for kind in INPUTS:
                if key == "garch_t" and (ctx != 252 or kind != "return"):
                    continue
                rec = {"model": key, "context": ctx, "input": kind}
                if adapter is None:
                    rec["status"] = load_err
                    rows.append(rec)
                    continue
                try:
                    b = pick_batch(key, adapter, ctx, kind)
                    rec.update({"model_id": adapter.model_id, "batch": b})
                    rec.update(run_condition(adapter, key, ctx, kind, b))
                    rec["variant"] = adapter.variant
                    if key == "chronos2":
                        rec["default_device"] = getattr(adapter, "default_device", "")
                    if key == "moirai2":
                        rec["raw_output_shape"] = str(getattr(adapter, "last_shape", ""))
                        rec["module_quantile_levels"] = str(adapter.qlevels_attr)
                    rec["status"] = "OK"
                except Exception as e:  # noqa: BLE001
                    rec["status"] = f"ERR {type(e).__name__}: {str(e)[:300]}"
                    traceback.print_exc()
                rec["finished_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                print(rec, flush=True)
                rows.append(rec)
                save_rows(rows, only)
                torch.cuda.empty_cache()
                gc.collect()
        del adapter
        torch.cuda.empty_cache()
        gc.collect()
    df = save_rows(rows, only)

    # 전체 시간 추정 (계획서 §9 축소 규칙 적용 제안)
    ok = df[df["status"] == "OK"]
    proj = ok.groupby("model")["sec_per_forecast"].mean().rename("mean_sec").to_frame()
    proj["n_conditions"] = [1 if m == "garch_t" else N_CONDITIONS for m in proj.index]
    proj["hours_full"] = proj["mean_sec"] * N_PER_RUN * proj["n_conditions"] / 3600
    proj.to_csv(OUT / "projection_v4.csv", encoding="utf-8-sig")
    print("\n[예상 시간: 모델별, 4조건 합계]\n", proj.round(3).to_string())
    print("※ 축소 여부(Chronos large→base, 샘플·기간 축소)는 Claude가 계획서 §9 규칙으로 최종 결정")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", choices=list(MODELS), default=None)
    main(ap.parse_args().only)
