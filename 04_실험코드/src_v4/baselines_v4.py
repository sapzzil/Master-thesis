# -*- coding: utf-8 -*-
"""baselines_v4.py — 기준 모형 (CPU). Random Walk, GARCH(1,1)-t (매일 재추정). 병렬 실행을 위해 별도 모듈."""
import time
import warnings

import numpy as np
from scipy import stats

import config_v4 as C

QL = C.QLEVELS
Z_Q = stats.norm.ppf(QL)


def rw_quantiles(R):
    """Random Walk: 과거 L일 수익률의 평균·표준편차(ddof=1)를 갖는 정규분포."""
    mu = R.mean(1, dtype=np.float64)
    sd = R.std(1, ddof=1, dtype=np.float64)
    return mu[:, None] + sd[:, None] * Z_Q[None, :], np.zeros(len(R), bool)


def _garch_one(r):
    warnings.filterwarnings("ignore")
    from arch import arch_model
    try:
        res = arch_model(np.asarray(r, float) * 100, mean="Constant", vol="GARCH", p=1, q=1, dist="t",
                         rescale=False).fit(disp="off", show_warning=False)
        f = res.forecast(horizon=1, reindex=False)
        mu, var, nu = f.mean.values[-1, 0], f.variance.values[-1, 0], res.params["nu"]
        if not (np.isfinite(mu) and np.isfinite(var) and var > 0 and np.isfinite(nu) and nu > 2):
            raise ValueError("비정상 추정치")
        q = (mu + np.sqrt(var * (nu - 2) / nu) * stats.t.ppf(QL, nu)) / 100
        return q, False
    except Exception:  # noqa: BLE001  — 사전 고정 대체 규칙: 과거 L일 정규분포(RW와 같음)
        r = np.asarray(r, float)
        return r.mean() + r.std(ddof=1) * Z_Q, True


def _garch_chunk(chunk):
    out = [_garch_one(r) for r in chunk]
    return np.stack([o[0] for o in out]), np.array([o[1] for o in out])


def garch_quantiles(R, workers, progress):
    chunks = [R[i:i + 500] for i in range(0, len(R), 500)]
    t0 = time.time()
    res = []
    if workers > 1:
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=workers) as ex:
            for i, r in enumerate(ex.map(_garch_chunk, chunks)):
                res.append(r)
                progress(i + 1, len(chunks), t0)
    else:
        for i, c in enumerate(chunks):
            res.append(_garch_chunk(c))
            progress(i + 1, len(chunks), t0)
    return np.concatenate([r[0] for r in res]), np.concatenate([r[1] for r in res])


