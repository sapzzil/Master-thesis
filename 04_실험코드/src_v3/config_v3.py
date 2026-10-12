# -*- coding: utf-8 -*-
"""
config_v3.py — 재실험 v3 사전등록(pre-registered) 고정 설정
=============================================================
이 파일의 값은 00_메타/재실험_계획서_v3.md 와 1:1로 일치해야 한다.
추론 실행 전 git 커밋으로 동결(freeze)하며, 동결 이후 변경은 계획서 부록
"계획 이탈 기록"에 사유와 함께 남기고 새 커밋으로만 허용한다.
"""
from pathlib import Path
import numpy as np

# -----------------------------------------------------------------------------
# 경로 (v2 산출물과 섞이지 않도록 전부 *_v3 디렉터리 사용)
# -----------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]          # 04_실험코드/
DATA_RAW = ROOT / "data" / "raw"                     # 기존 원천 데이터(재다운로드 금지)
DATA_SYN = ROOT / "data" / "synthetic_v3"
RES = ROOT / "results_v3"
RAW_FC = RES / "raw_forecasts"
TABLES = RES / "tables"

# -----------------------------------------------------------------------------
# 공통
# -----------------------------------------------------------------------------
SEED_BASE = 20261013          # 모든 난수의 기준 시드
N_SERIES = 100                # 시나리오당 시계열 수 (v2: 20)
CONTEXT_LEN = 512
HORIZON = 20
NUM_SAMPLES = 100
BURN_IN = 200
P0 = 100.0

# -----------------------------------------------------------------------------
# 합성 3축 (레벨 값은 v2에서 실제로 사용한 값을 유지)
# 모든 축: 무조건부 평균 0, 무조건부 분산 SIGMA_UNC^2 = 1e-4
# -----------------------------------------------------------------------------
SIGMA_UNC = 0.01
SIGMA_UNC_SQ = SIGMA_UNC ** 2

GARCH_LEVELS = {"L1": 0.30, "L2": 0.60, "L3": 0.85, "L4": 0.95, "L5": 0.98}   # alpha+beta
GARCH_ALPHA_SHARE = 0.10                                                       # alpha:beta = 1:9

TAIL_LEVELS = {"L1": 30.0, "L2": 10.0, "L3": 5.0, "L4": 3.5, "L5": 2.5}       # Student-t 자유도

REGIME_LEVELS = {"L1": 0.02, "L2": 0.05, "L3": 0.10, "L4": 0.20, "L5": 0.35}  # 대칭 전이확률 p
# 원래 형태(σ 비율 3.75배, 두 상태 평균 차 0.0025)를 유지하되
# (1) 평균을 ±0.00125 대칭으로 두어 무조건부 평균 0,
# (2) 전체를 상수 c로 스케일해 무조건부 분산 1e-4가 되게 한다.
_REG_SIGMA_RAW = (0.008, 0.030)
_REG_MU_RAW = (+0.00125, -0.00125)
_V_RAW = 0.5 * (_REG_SIGMA_RAW[0] ** 2 + _REG_SIGMA_RAW[1] ** 2) + 0.25 * (_REG_MU_RAW[0] - _REG_MU_RAW[1]) ** 2
REGIME_SCALE = float(np.sqrt(SIGMA_UNC_SQ / _V_RAW))
REGIME_SIGMA = tuple(REGIME_SCALE * s for s in _REG_SIGMA_RAW)
REGIME_MU = tuple(REGIME_SCALE * m for m in _REG_MU_RAW)

AXES = {
    "GARCH": GARCH_LEVELS,
    "TAIL": TAIL_LEVELS,
    "REGIME": REGIME_LEVELS,
}

# -----------------------------------------------------------------------------
# 실측 시장
# -----------------------------------------------------------------------------
US_TICKERS = ["AAPL", "AMZN", "GOOG", "JPM", "META"]
KR_TICKERS = ["069500"]
MARKET_FILES = {t: DATA_RAW / f"us_yf_{t}.parquet" for t in US_TICKERS}
MARKET_FILES["069500"] = DATA_RAW / "kr_fdr_069500.parquet"   # yfinance판은 가격 오차·결측 32일 → FDR 사용
MASTER_CALENDAR = "AAPL"     # 패널 윈도우 기준 날짜 달력
PANEL_STEP = 60              # 패널 윈도우 시작점 간격(거래일)
STREAM_LEN = 100             # H5 전용 연속 구간: 각 자산 마지막 100거래일(20일 x 5개 연속 윈도우)
LEAKAGE_SPLIT_DATE = "2024-03-01"   # 보조 분석: TSFM 공개 이전/이후 구간 분리

# -----------------------------------------------------------------------------
# 모델
# -----------------------------------------------------------------------------
MODELS = ["chronos-tiny", "chronos-base", "moirai-small", "moirai-base", "garch_t", "random_walk"]
TSFM = ["chronos-tiny", "chronos-base", "moirai-small", "moirai-base"]
MODEL_IDS = {
    "chronos-tiny": "amazon/chronos-t5-tiny",
    "chronos-base": "amazon/chronos-t5-base",
    "moirai-small": "Salesforce/moirai-1.0-R-small",
    "moirai-base": "Salesforce/moirai-1.0-R-base",
}
MOIRAI_PATCH = 32

# -----------------------------------------------------------------------------
# 사후보정 (v2 설정 그대로 동결 — v3 데이터는 이 설정에 대한 외표본 검증)
# -----------------------------------------------------------------------------
ACI_ALPHA = 0.10
ACI_GAMMA = 0.05
ACI_CLIP = (0.01, 0.40)
QACI_PCT_CLIP = (0.5, 99.5)       # Step1 Quantile-Index ACI 분위 한계
CQR_M0 = 20                        # 층화 사전 잔차 수
CQR_QLEVEL_CLIP = (10.0, 99.5)     # Step2 잔차 분위 한계(%)
# 에피소드(보정 상태 리셋 단위)
#   synth_*        : 시계열(series_id)마다 리셋
#   market_panel   : 윈도우(series_id)마다 리셋   ← 시장 H5 주분석
#   market_stream  : 자산별 연속 100일, 윈도우를 과거→최근 순서로 처리  ← 보조분석

# -----------------------------------------------------------------------------
# 분석·판정
# -----------------------------------------------------------------------------
ALPHA_TEST = 0.05
N_BOOT = 2000
BOOT_SEED = 7
EQUIV_MARGIN = 0.03               # H5 '복원' 판정: 커버리지 90% CI가 [0.87, 0.93] 안
