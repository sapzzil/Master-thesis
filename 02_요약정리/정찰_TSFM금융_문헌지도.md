# 2단계 정찰 — TSFM × 금융 문헌 지도

> 작성일 2026-08-12. 서브에이전트 4개 병렬 조사(Sonnet) 결과 종합.
> 목적: 1단계 주제 확정 전 "무엇이 선점됐고 무엇이 비었는가" 판정.

---

## 0. 한 줄 결론

**판정: (나) 부분 선점.** 아이디어와 거의 같은 문제의식의 논문(FinStressTS, KDD 2026)이 이미 존재하나,
**사전학습 TSFM을 대상으로 하지 않았고, 합성-실측 대조를 하지 않았다.** 이 두 지점이 확실한 공백.

---

## 1. 가장 위협적인 선행연구 — FinStressTS

**[FinStressTS: A Parametric Synthetic Benchmark for Time-Series Forecasting in Finance](https://arxiv.org/abs/2606.03184)**
(Sun, Koa et al., NUS, KDD 2026) — [코드 공개](https://github.com/jiazeee/FinStressTS)

- 금융 메커니즘 6개를 파라미터화한 합성 벤치마크: 변동성 군집(GARCH), 다중스케일 지속성(HAR),
  두꺼운 꼬리, 체제전환, 자기여기 점프(Hawkes), 영과잉 → 30개 진단 환경
- 15개 모델(AR/HAR/VAR/DLinear/PatchTST/iTransformer/Autoformer/FEDformer/TimeXer/DeepAR/TimeGrad 등)을
  **각 환경마다 처음부터 학습**시켜 NMAE·CRPS로 평가
- 발견: 단순 선형/AR이 견고, Transformer·전역 attention은 국소 충격에 취약

### 우리와의 결정적 차이 (= 공백)
1. **사전학습 TSFM(TimesFM/Chronos/Moirai/TTM)을 전혀 다루지 않음** — 논문 전체에 언급 없음(확인됨)
2. **합성 임계점이 실제 주가의 어디쯤인지 대조하는 실험 없음** — 순수 벤치마크
3. 저자들이 Limitations에서 "사전학습 모델도 같은 취약점을 물려받는가"를 **미해결 과제로 명시**

→ **인용 필수. 서론에 명시적 차별화 문장 필요.**

---

## 2. 인접 선행연구 (단일 축 통제실험 계열 — 이미 붐빔)

| 논문 | 통제 축 | 대상 | 도메인 |
|---|---|---|---|
| [Frequency Matters: When TSFMs Fail Under Spectral Shift](https://arxiv.org/abs/2511.05619) (NeurIPS 2025 WS) | 주파수 | zero-shot TSFM | 게임 |
| [Evaluating TSFMs on Noisy Periodic Time Series](https://arxiv.org/abs/2501.00889) | 노이즈·주기·샘플링률 | zero-shot TSFM | 일반 |
| [Trend strength predicts when generative FMs win](https://arxiv.org/html/2607.19383) | 트렌드 강도 | TSFM | 일반 |
| [Benchmarking M-LTSF: Frequency and Noise-Based Evaluation](https://arxiv.org/html/2510.04900v1) | SNR·주파수·노이즈 | 학습형 모델 | 일반 |
| [On the Internal Semantics of TSFMs](https://arxiv.org/abs/2511.15324) | 합성 개념(AR1/레벨시프트/분산) | TSFM 내부 레이어 | 일반 |
| [Non-Stationarity in the Embedding Space of TSFMs](https://arxiv.org/pdf/2604.16428) | 비정상성 | TSFM 임베딩 | 일반 |
| [Position: Universal TSFMs Rest on a Category Error](https://www.arxiv.org/abs/2602.05287) | (이론) | — | 이론 |

**시사점**: "합성 통제실험으로 TSFM 실패 임계점을 찾는다"는 패러다임 자체는 더 이상 참신하지 않음.
**금융 다축 + 사전학습 TSFM + 실측 대조**의 조합이 차별점이어야 함.

---

## 3. TSFM 금융 적용 현황 — 결론이 갈리고 있음

| 논문 | 대상 | 결론 |
|---|---|---|
| [Re(Visiting) TSFM in Finance](https://arxiv.org/abs/2511.18578) (FoFI 2026) | 미국 CRSP + 다국가 Compustat, 20억+ 관측 | **off-the-shelf TSFM은 zero-shot·fine-tune 모두 부진.** from-scratch 사전학습만 유효. TimesFM R²=-2.80%, Chronos R²=-1.37% |
| [Pretrained TSFM for Financial Return Forecasting](https://arxiv.org/abs/2606.27100) | 미국 개별주 5종 | **TSFM이 10개 과제 중 8개 승리** (Moirai-2.0, TimesFM-2.5 최상위) |
| [Forecasting Realized Volatility with TSFM](https://arxiv.org/abs/2607.05291) | 주식·외환·선물 50자산, 9 TSFM vs 8 HAR 계열 | **균일한 이득 없음.** TTM만 Log-HAR을 근소하게 이김 |
| [DELPHYNE](https://arxiv.org/abs/2506.06288) | 일반+금융 혼합 사전학습 | 기존 TSFM은 negative transfer로 이득 없음 → 금융 특화 모델 제안 |
| [Kronos](https://arxiv.org/abs/2508.02739) (AAAI 2026) | 45개 거래소 K-line 12억건 | 범용 TSFM은 K-line에서 비사전학습 모델보다도 떨어짐 |
| [FinCast](https://arxiv.org/abs/2508.19609) (CIKM 2025) | 주식·원자재·선물 | 10억 파라미터 금융 특화, 범용 대비 MSE 20% 개선 |
| [Financial Fine-tuning a Large Time Series Model](https://arxiv.org/abs/2412.09880) | 금융 1억 시점 | TimesFM zero-shot 불만족 → continual pretraining으로 개선 |

### ★ 핵심 관찰 — 문헌 모순
2511.18578("TSFM 부진")과 2606.27100("TSFM 8/10 승리")이 **정면으로 배치**됨.
자산별로도 승자가 갈림(META는 iTransformer 승, BTC는 zero-shot Chronos 승).
**이 모순을 설명하는 연구가 없음** → 우리 연구의 강력한 동기.
가설: "자산이 어느 축의 어느 위치에 있느냐"가 승패를 가른다.

---

## 4. 적응·PEFT 기법 현황

- **LoRA는 이미 baseline.** [Beyond LoRA](https://arxiv.org/abs/2409.11302)가 FourierFT/BitFit/VeRA로 LoRA를 이미 능가
  (Chronos-Tiny + FourierFT가 파라미터 2,400개로 SOTA 70만 파라미터 능가) — 단 **검증 도메인은 헬스케어(ICU)**
- **금융에서 LoRA는 오히려 실패 사례로 축적 중**:
  - [RefineBridge](https://arxiv.org/pdf/2512.21572): "LoRA는 금융 데이터에서 underperform" 명시
  - [Foundation Models and Fine-Tuning 서베이](https://arxiv.org/html/2607.23146): GIFT-Eval의 Econ/Fin 도메인에서
    **zero-shot이 최강**, FFT·LoRA 모두 못 이김
  - [When Directional Accuracy Lies](https://arxiv.org/abs/2607.12248): TimesFM+LoRA 방향정확도 80%가
    상승장 base-rate 아티팩트임을 폭로
- **공백**: 선택적/가법적 PEFT(FourierFT, BitFit, VeRA)를 **금융에 적용한 사례 전무**
- **서베이가 명시한 open problem**: "어떤 상황(모델 규모/도메인/horizon)에서 어떤 적응 전략을 써야 하는지
  원리적 기준이 없음", "TSFM의 이론적·실증적 이해 부족"

---

## 5. 한국 시장 — 명확한 공백

- **TSFM(TimesFM/Chronos/Moirai/Kronos 등)을 KOSPI/KOSDAQ에 적용한 논문: 확인되지 않음**
  (영문·KCI·국내 학위논문 모두 검색)
- 국내 연구는 전부 LSTM/CNN/감성분석 계열. Transformer 계열조차 국내 공백 시사
- 신흥국 TSFM 사례는 존재: [인도네시아 Lag-Llama](https://www.oajaiml.com/archive/assessing-lag-llama-in-probabilistic-time-series-forecasting-for-the-indonesian-stock-market),
  [폴란드 EPS 예측](https://www.tandfonline.com/doi/full/10.1080/00128775.2025.2534144) — **동아시아 사례 없음**
- 가장 근접한 국내 연구: [Triple Barrier Labeling, Korean Markets](https://arxiv.org/abs/2504.02249)
  (2006–2024 KOSPI/KOSDAQ 전종목, LSTM)
- KOSPI가 포함된 국제 CRPS 비교연구 1건: [arXiv 2508.18921](https://www.arxiv.org/pdf/2508.18921)
- ⚠️ 한국 시장 특수요인: 상하한가 제도(2026년 단일가매매 전환 논의 중 → 구조적 단절 위험),
  개인투자자 거래비중 급변(2026.1월 48.19% → 최근 31.23%)

---

## 6. 평가 프로토콜 — 차별점 후보

- **MSE 비판은 문헌에 실재**. 가장 강한 1차 출처: [FinTSB](https://arxiv.org/abs/2502.18834) (ICAIF 2025 WS Best Paper,
  [코드](https://github.com/TongjiFinLab/FinTSB)) — Diversity Gap / Standardization Deficit / Real-World Mismatch 3대 결함 지적
- **필수 통계검정**: Diebold-Mariano(pairwise), Model Confidence Set(다중비교). QLIKE(변동성 전용)
- **데이터 누출**: [Profit Mirage](https://arxiv.org/abs/2510.07920) — LLM 가중치 내재 누출은 파이프라인 감사로 못 잡음.
  [Look-Ahead-Bench](https://arxiv.org/pdf/2601.13770) — LLM이 학습 윈도우 내 S&P500 종가를 1% 미만 오차로 암기
  → **TSFM도 사전학습 코퍼스에 주가가 포함됐을 가능성. 반드시 통제 대상.**
- 실증: 2023–2025 주요 학회 164편 중 look-ahead bias 명시 인정 26.8%, survivorship bias 1.2%
  → 명시적 통제만으로도 차별점

---

## 7. 실험 인프라 — ⚠️ 데이터 리스크 발견

| 라이브러리 | 상태 (2026.8 기준) | 조치 |
|---|---|---|
| `pykrx` | **불안정** — 2026.2.27 이후 대규모 다운/400 에러, 로그인 인증 요구로 변경 | 단독 의존 금지. 조기 확보 후 로컬 캐싱 |
| `FinanceDataReader` | pykrx와 동시 다운 사례(2026.2) | 백업 경로로만 |
| `yfinance` | 429 rate limit 다발, 비공식 스크래핑 | 대량 호출 금지, 캐싱 필수 |
| `chronos-forecasting` | ✅ Small+Base+Large 합 ~4GB → **RTX 3080 10GB 충분** | 주력 |
| `timesfm` | ✅ 설치 용이, 경량 | 주력 |
| `uni2ts` (Moirai) | ✅ 활발 | VRAM 미확인 |
| `gluonts` | ✅ CRPS 등 확률평가 지표 내장 | 평가에 활용 |
| `arch` | ✅ 안정 | GARCH/HAR 베이스라인 |
| `qlib` | ✅ 활발 | 중국 A주 중심, 한국 어댑터 직접 구현 필요 |
| `vectorbt` | ❌ **오픈소스판 유지보수 중단**(0.28.1이 마지막) | 사용 지양 |
| `mlfinlab` | ❌ **All rights reserved, 오픈소스 아님** | 개념만 참고, 직접 구현 |

**즉시 조치 필요**: 한국 데이터를 조기에 확보해 로컬 스냅샷으로 고정할 것. 데이터 소스가 죽으면 논문이 멈춤.

---

## 8. 종합 — 확정 주제안

### 제목 (가제)
> **금융 시계열의 어떤 성질이 사전학습 시계열 파운데이션 모델을 무너뜨리는가**
> — 파라메트릭 합성 진단과 실측 대조, 그리고 한국 시장 검증

### 기여 3가지
1. **[진단]** FinStressTS의 금융 메커니즘 축(공개 코드 활용)에 **처음으로 사전학습 zero-shot TSFM**을 투입,
   축별 파괴 임계점 측정 — FinStressTS가 Limitations로 남긴 바로 그 질문
2. **[매핑]** 합성 임계점 ↔ 실제 자산의 통계량(추정 SNR, 꼬리지수, Hurst, 체제전환 빈도) 대조.
   **선행연구 전무.** → 이것으로 2511.18578 vs 2606.27100의 **문헌 모순을 설명**
3. **[검증]** 한국 시장(KOSPI/KOSDAQ) 적용 — TSFM×한국 최초. 누출 통제·DM 검정 포함 엄밀 프로토콜

### 왜 실현 가능한가
- 전 과정 **추론만** — 학습 없음. RTX 3080 10GB로 충분(Chronos 전 크기 합 ~4GB)
- 합성데이터 생성기 **이미 공개**(FinStressTS GitHub) → 밑바닥 구현 불필요
- 성능이 안 나와도 결과가 됨 (임계점이 어디든 그게 발견)

### 방어 논리
- "벤치마킹 아니냐" → 기여 2가 답. 합성 축으로 **원인을 분리**하는 것은 실데이터로는 불가능
- "FinStressTS와 뭐가 다르냐" → 대상 모델(from-scratch vs 사전학습), 실측 대조 유무
- "한국 시장이 왜 중요하냐" → 단독 novelty로 쓰지 않음. 기여 2의 **검증 사례**로만 배치

### 남은 리스크
- FinStressTS 후속 연구가 같은 공백을 먼저 메울 가능성 → 속도가 방어책
- 한국 데이터 소스 불안정 → 조기 스냅샷 확보로 대응
