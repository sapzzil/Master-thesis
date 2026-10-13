# -*- coding: utf-8 -*-
"""
config_v4.py — 재실험 v4 사전등록 고정 설정
===========================================
이 파일의 값은 00_메타/재실험_계획서_v4.md 와 1:1로 일치해야 한다.
본 실행 전 git 커밋으로 동결하며, 동결 이후 변경은 계획서 §12 "계획 이탈 기록"에
사유와 함께 남기고 새 커밋으로만 허용한다.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]            # 04_실험코드/
DATA_RAW = ROOT / "data" / "raw"                       # 미국 5종목 (v3와 같은 파일, 수정 금지)
DATA_V4 = ROOT / "data" / "raw_v4"                     # 한국 5종목, 단계값
DATA_SYN = ROOT / "data" / "synthetic_v4"


def res_dir(smoke=False):
    return ROOT / ("results_v4_smoke" if smoke else "results_v4")


# ------------------------------------------------------------------ 공통 (계획서 §1)
SEED_BASE = 20261013
QLEVELS = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
LO_IDX, HI_IDX = 0, 8                 # 80% 구간 = [q0.1, q0.9]
NOMINAL = 0.80
CONTEXTS = [21, 252]
INPUTS = ["return", "price"]
EP_LEN, EP_WARM = 80, 20              # 에피소드 80일 = 준비 20 + 채점 60
P0 = 100.0

# ------------------------------------------------------------------ 합성 (계획서 §2)
N_SERIES = 100
WARMUP = 200
SIM_LEN = WARMUP + 252 + EP_LEN       # 532: 워밍업 200 + 과거 252 + 에피소드 80
FIRST_TARGET = WARMUP + 252           # 452: 에피소드 첫날(예측 대상)의 위치
LEVELS = json.loads((DATA_V4 / "synthetic_levels_v4.json").read_text(encoding="utf-8"))
SIGMA = LEVELS["daily_vol"]           # 일 변동(무조건부 표준편차) 2.11%
GARCH_ALPHA_SHARE = 0.10              # α:β = 1:9


def scenarios():
    """시나리오 17개: L1 공통 1개 + 4축 × L2~L5. (이름, 축, 단계, 모수)"""
    out = [("L1", "NONE", 1, {})]
    for L in ["L2", "L3", "L4", "L5"]:
        k = int(L[1])
        out.append((f"CL_{L}", "CL", k, {"ab": LEVELS["cluster_ab"][L]}))
        out.append((f"TL_{L}", "TL", k, {"nu": LEVELS["tail_nu"][L]}))
        out.append((f"RF_{L}", "RF", k, LEVELS["regime_freq"][L]))
        out.append((f"RS_{L}", "RS", k, LEVELS["regime_size"][L]))
    return out


AXES = ["CL", "TL", "RF", "RS"]
AXIS_HYP = {"CL": "H1", "TL": "H2", "RF": "H3a", "RS": "H3b"}

# ------------------------------------------------------------------ 실제 주식 (계획서 §3)
US = ["AAPL", "AMZN", "GOOG", "JPM", "META"]
KR = {"005930": "삼성전자", "000660": "SK하이닉스", "005380": "현대차", "015760": "한국전력", "012330": "현대모비스"}
REAL_FILES = {t: DATA_RAW / f"us_yf_{t}.parquet" for t in US}
REAL_FILES.update({c: DATA_V4 / f"kr_fdr_{c}.parquet" for c in KR})
REAL_START, REAL_END = "2015-01-02", "2026-09-22"
EVAL_START = "2017-01-02"             # 첫 예측 대상일
# 학습 데이터 누출 점검(보조): 모델 공개 다음 달 1일 이후 예측만 따로 집계 (보수적으로 공개월 제외)
RELEASE_AFTER = {
    "chronos_t5_base": "2024-04-01",   # Chronos 논문·가중치 2024-03 공개
    "moirai2": "2025-09-01",           # Salesforce 블로그 2025-08-08
    "timesfm25": "2025-10-01",         # 2025-09 공개
    "chronos2": "2025-11-01",          # Amazon Science 블로그 2025-10-20
}

# ------------------------------------------------------------------ 모델 (계획서 §4)
TSFM = ["chronos_t5_base", "chronos2", "timesfm25", "moirai2"]
BASELINES = ["rw", "garch_t"]
MODEL_IDS = {
    "chronos_t5_base": "amazon/chronos-t5-base",
    "chronos2": "amazon/chronos-2",
    "timesfm25": "google/timesfm-2.5-200m-pytorch",
    "moirai2": "Salesforce/moirai-2.0-R-small",
}
CHRONOS_SAMPLES = 200
# 배치 크기: 준비작업 k03에서 GPU 메모리 9,500MB 이하로 확인된 값. 실행 중 넘치면 자동으로 절반.
BATCH = {("chronos_t5_base", 21): 32, ("chronos_t5_base", 252): 4,
         ("chronos2", 21): 256, ("chronos2", 252): 256,
         ("timesfm25", 21): 256, ("timesfm25", 252): 256,
         ("moirai2", 21): 256, ("moirai2", 252): 256}
VRAM_LIMIT_MB = 9500


def conditions(model):
    """모델별 조건 목록 [(L, input)]."""
    if model in TSFM:
        return [(L, k) for L in CONTEXTS for k in INPUTS]
    if model == "rw":
        return [(21, "return"), (252, "return")]
    if model == "garch_t":
        return [(252, "return")]
    raise ValueError(model)


# ------------------------------------------------------------------ 사후보정 (계획서 §6)
ACI_ALPHA = 0.20
ACI_GAMMA = 0.05
ACI_CLIP = (0.02, 0.50)

# ------------------------------------------------------------------ 판정 (계획서 §7)
ALPHA_TEST = 0.05
SUBST_COV = 0.02                      # 커버리지 실질 기준 2%p
SUBST_QL = 0.02                       # 분위수 손실 실질 기준 RW 대비 2%
H5_BAND = (0.77, 0.83)                # 보정 후 커버리지 90% CI가 이 안이면 복원
N_BOOT = 2000
BOOT_SEED = 7

# ------------------------------------------------------------------ 입력 데이터 지문 (다르면 실행 중단)
EXPECTED_SHA256 = {
    "data/raw/us_yf_AAPL.parquet": "feba17c0703a1dbfdbff1e947908d76a46ffb51489f2a37ed7e67fc663c4653e",
    "data/raw/us_yf_AMZN.parquet": "79028a5a7ad55dde08e4f9d36957b0f7d2b87b8a5f5bbc6e67f9aba60d963e60",
    "data/raw/us_yf_GOOG.parquet": "5b50e25d2b849e01cc0e27f6afc3da302bb34ad633dd27f3b859cdd1c342d041",
    "data/raw/us_yf_JPM.parquet": "ee60a136a4be3347562559580faf2451bafb54bd2b12e884e308b372aeb8f910",
    "data/raw/us_yf_META.parquet": "63d4bbd86d6c23717aff11260c32ce39a863995540ff3980bec55b1b4c42bc21",
    "data/raw_v4/kr_fdr_000660.parquet": "065c40373c58b8e98cb3d26fe4f4413ff76d4e9be323d68fa6d8c6ee295316b7",
    "data/raw_v4/kr_fdr_005380.parquet": "c99efd3a838de947bde7ebe848a56c5ebf9c71b0ca1bcc4bfa43628922d26c93",
    "data/raw_v4/kr_fdr_005930.parquet": "f2e312fceef3fa9fe41dbedd9df4adb496bcabce504a980e6345b0b4e0988172",
    "data/raw_v4/kr_fdr_012330.parquet": "ec302c6971f67bee3c97c334073e794e516806b8142a74de1287655bf052fe8b",
    "data/raw_v4/kr_fdr_015760.parquet": "9b47330f2fb61ac9818919224a3ad0c27766503a2f5a71c785848d398849d58d",
    "data/raw_v4/synthetic_levels_v4.json": "eda266e4f53bbe350974ca4b0bf5423346a0e2f22978592772ae1acf8266f22e",
}
