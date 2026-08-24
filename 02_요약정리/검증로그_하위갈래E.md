# 검증로그 — 하위갈래 E (신규 경쟁문헌: ProbFM / δ-Adapter / GLCP)

> 작성일: 2026-08-24
> 작성자: 3단계 교차검증 에이전트 (Opus, 독립 세션 — 원 요약 작성자와 분리)
> 대상: `하위갈래E_신규경쟁문헌.md` 및 그 근거가 된 원문 노트 3건
>   - `2601.10591_ProbFM_Probabilistic_TSFM_Uncertainty_Decomposition.md`
>   - `2601.20280_deltaAdapter_PostProcessing_Shift_TimeSeries.md`
>   - `2607.23165_GLCP_ABF-T_GateLocalized_Conformal_Prediction.md`
> 원칙:
>   1. 원 요약 파일의 서술을 신뢰하지 않고, **본 검증자가 직접 arXiv 원문(abs/html/pdf)을 재조회**해
>      문장 단위로 대조한다.
>   2. 큰따옴표로 인용된 영문 문장은 **전부 원문 존재 여부를 개별 확인**한다(과거 "인용부호는 있으나
>      원문에 없는 문장" 사례 재발 방지).
>   3. 판정은 CONFIRMED / PARTIALLY CONFIRMED(수정 필요) / REVERSED 중 하나로 명시한다.
>   4. **원 요약 파일은 직접 수정하지 않는다.** 수정 제안만 본 로그에 남긴다.

## 본 검증에서 실제로 수행한 원문 재조회

| 논문 | 재조회한 URL | 확보 범위 |
|---|---|---|
| GLCP | `arxiv.org/abs/2607.23165`, `arxiv.org/html/2607.23165v1`, `www.arxiv.org/pdf/2607.23165` | Abstract 전문(축자), Method(게이트 정의·수식 3·데이터분할), Intro/Related Work, **Conclusion 전문(축자)**, Limitations, 실험설정·수치, 베이스라인 전체 목록 |
| ProbFM | `arxiv.org/abs/2601.10591v1`, `arxiv.org/html/2601.10591v1` | Abstract 전문(축자), Introduction, 실험 백본 설정, Table 1·Table 4, 데이터 설명, **Limitations 전문(Appendix F, 축자)** |
| δ-Adapter | `arxiv.org/abs/2601.20280`, `arxiv.org/html/2601.20280v1`, `www.arxiv.org/pdf/2601.20280`, GitHub `Anoise/Adapter` | Abstract 전문(축자), 동결(frozen) 관련 Method 문장, **Table 1(사전학습 모델 대상) 백본·수치**, 데이터셋 목록, **Conclusion 전문(축자)** |

세 편 모두 **arXiv에 실재하는 논문임을 독립 확인**했다(제목·저자·투고일 일치). 원 요약의 서지사항에
날조는 없다. 다만 GLCP의 저자 소속은 본 검증에서도 확인하지 못했다.

원 요약이 "미확보"로 남겼던 항목 중 **GLCP Conclusion·Limitations 전문, GLCP 실험 수치·베이스라인
목록, ProbFM Table 1·4, ProbFM Limitations 전문, δ-Adapter Table 1·Conclusion**을 이번에 확보했다.
이 신규 확보분에서 **원 요약을 뒤집는 사실 2건과 날조 인용 1건**이 나왔다.

---

## 1. 핵심 검증 지점 — GLCP의 "model-agnostic"과 동결 TSFM 적용 가능성

### 원 요약의 잠정 판단
> "GLCP가 ABF-T라는 처음부터 학습하는 예측기의 게이트 표현에 의존하므로, 동결된 사전학습 TSFM에
> 그대로 사후 이식하기 어려울 수 있다" — 그리고 이것이 "Moirai 반전 오류와 유사한 위험 신호"일 수 있음.

### 판정: **잠정 판단은 옳다(뒤집히지 않음). 단, "위험 신호"가 아니라 오히려 우리에게 유리한 근거다.**

원 요약은 이 지점을 "우리 3번째 기여의 설계 전제와 정면으로 부딪힐 수 있다"는 **위험**으로 서술했으나,
이번에 확보한 Conclusion 원문은 정반대의 함의를 갖는다. 근거는 세 가지다.

**(a) 논문 스스로 "foundation backbone 통합"을 미해결 과제(Future Work)로 명시했다** — 신규 확보,
결정적 증거. Conclusion 마지막 문장(축자 인용):

> "Future work includes improving the efficiency of these components, extending guarantees to broader
> forms of nonstationarity, and integrating stronger domain-specific or foundation forecasting
> backbones."

즉 GLCP 저자들 자신이 **파운데이션 백본과의 결합은 아직 하지 않았고 앞으로 할 일**이라고 적었다.
이것은 우리 3번째 기여가 GLCP에 흡수되는 것이 아니라, **GLCP가 남긴 빈칸을 우리가 메우는 구도**임을
저자 진술로 뒷받침한다. 진행상황.md의 FinStressTS·Re(Visiting) 항목처럼 "저자 스스로 인정한 공백"
유형의 강한 인용 근거로 쓸 수 있다.

**(b) "model-agnostic"의 의미가 원문에서 명확히 한정된다.** 축자 인용:

> "Rather than proposing a new forecasting backbone, ABF-T is a model-agnostic framework that combines
> scale-specific forecasts through validation-anchored adaptation and sparse predictive transfer.
> It can therefore be paired with different statistical or neural forecasting architectures."

두 번째 문장("It can therefore be paired with different ... architectures")이 정의를 확정한다.
model-agnostic = **프레임워크 내부의 스케일별 전문가(expert)로 어떤 아키텍처든 끼워 넣을 수 있다**는
뜻이지, **외부의 동결된 모델에 사후 부착 가능하다**는 뜻이 아니다. 원 요약의 해석이 정확했다.

실제 실험에서 "alternative backbones"로 검증한 것도 **PatchTST** 하나이며, 이 역시 프레임워크 안에서
처음부터 학습된다:
> "Table 4 uses PatchTST as a strong neural backbone to test whether ABF-T-GLCP remains effective
> beyond HAR experts."

또한 논문 전체에 "foundation model"은 위 Future Work 문장 1회뿐이고, **"pretrained", "pre-trained",
"frozen", "Chronos", "Moirai", "TimesFM", "zero-shot"은 단 한 번도 등장하지 않는다.**

데이터 분할도 예측기 학습이 프레임워크에 내장되어 있음을 확인시킨다(축자, 원 요약의 인용이 정확):
> "The Train and Val sets are used to fit the forecasting model and perform model selection, including
> anchor selection, multi-scale blending, and sparse predictive transfer"
> "The Cal set is used for GLCP bandwidth selection and conformal calibration, while the Test set is
> reserved exclusively for final evaluation."

**(c) 그러나 — 원 요약보다 차용 가능성이 *높다*. 게이트 입력 z가 부분적으로 예측기 비의존적이다.**
이것이 원 요약이 놓친 두 번째 신규 사실이다. 게이트 입력의 정의(축자):

> "the gate input z_{t,j} is constructed only from information in F_t, including asset-specific
> multi-scale volatility summaries and scale-expert signals, with no future outcome information."

즉 z는 **불투명한 신경망 은닉상태가 아니라**, (i) 자산별 다중스케일 **변동성 요약통계** — 관측
시계열만으로 계산 가능, 어떤 예측기와도 무관 — 와 (ii) scale-expert 신호 — 이쪽만 ABF-T 의존 — 의
혼합이다. 게이트 π = g_θ(z)의 g_θ만이 ABF-T와 함께 학습된다("Rather than assigning fixed scale
weights, we learn an asset-specific gating network.").

→ 실무적 함의: **동결 TSFM에 대해 z의 (i) 성분(변동성 요약)은 그대로 재현 가능하고, (ii) 성분은
TSFM 자신의 출력(예측 분위수 폭, 샘플 분산 등)으로 대체 설계할 수 있다.** TSFM 가중치를 건드리지
않으므로 "재학습 없는 사후 보정"이라는 우리 설계 전제는 **깨지지 않는다**(경량 게이트/국소화 함수만
캘리브레이션 셋에서 적합하는 것은 δ-Adapter의 어댑터 학습과 동일한 범주의 작업이다).

Limitations도 이 대체 설계의 성패 조건을 알려준다(축자):
> "The framework relies on informative predictive-state representations. If the gate fails to
> distinguish regimes, localized calibration may be less effective."

→ 우리가 설계할 게이트-대체 표현이 **체제(regime)를 구분할 만큼 정보량이 있어야 한다**는 것이 논문이
명시한 성립 조건이며, 이는 우리 체제전환 축 실험에서 직접 검증 가능한 형태의 가설이다.

### 결론 — "3번째 기여의 재료로 흡수"는 과장인가?
**과장이다. 표현을 낮춰야 한다.** "GLCP를 흡수"가 아니라 다음 두 가지로 분리해 서술해야 한다.
- **직접 재료로 쓸 수 있는 것**: ① 국소화 아이디어(체제 표현 + 시간 근접성으로 캘리브레이션 잔차를
  선택), ② 수식 3의 국소화 가중치 형태, ③ **콘포멀 베이스라인 목록**(아래), ④ 저자가 명시한 성립
  조건(게이트의 체제 구분력).
- **그대로 쓸 수 없는 것**: ABF-T의 학습된 게이트 π 자체. 동결 TSFM용 게이트-대체 표현은 **우리가
  직접 설계·검증해야 하는 우리 기여**다.

**신규 부수확 — 3번째 기여의 콘포멀 베이스라인 세트를 원문에서 확보했다.** GLCP가 비교한 UQ
베이스라인 전체 목록: **ACI, AgACI, SAOCP, RCQR, EnbPI, RLCP, MoECP.** 특히 RLCP는 국소화 계열이라
우리 실험의 직접 비교군으로 적합하다. 예측 베이스라인은 "Single-Scale, Equal-Weight, and
Asset-Specific Gated Scale MoE".

**GLCP 실험설정·수치(신규 확보)**: 밀리초 단위 원자재 선물 **55종**, 5분봉 리샘플링,
**2022-08-01 ~ 2023-08-01(1년)**. h=48·명목 90%에서 GLCP(Asym.) 커버리지 0.908 / 폭 3.06 /
interval score 3.48 vs ACI 커버리지 0.907 / 폭 4.22 / 4.79. 점예측 h=48 MAE 1.043(최고 베이스라인
1.105 대비 5.59% 개선), h=96 MSE 3.270(3.848 대비 15.02% 개선).

---

## 2. δ-Adapter — 진짜 post-hoc·frozen인가, Sundial-S·TTM-R2는 실재하는가

### 판정: **CONFIRMED. 원 요약보다 더 강한 근거를 확보했다.**

**(a) 동결 여부 — 원 요약이 인용한 두 문장 모두 원문에 축자로 존재함을 확인했다.**
> "We keep all parameters of F fixed and introduce a lightweight, learnable adapter A_θ with parameters
> θ trained on D."
> "Since A is a tiny network (e.g., shallow MLP or low-rank head) trained while F remains frozen, it
> produces consistent gains with negligible training time and zero changes to F's inference interface."

Conclusion 전문(신규 확보, 축자) 첫 문장이 성격을 못박는다:
> "We present δ-Adapter, a lightweight and post-hoc framework that improves frozen forecasters via
> bounded input nudges and output residual corrections."

→ **"post-hoc" + "frozen forecasters"가 저자 자신의 단어로 확인**된다. 진행상황.md의 사후 보정 방향
서술("모델 자체는 얼려두고 출력값에 보정 함수만 사후 적용")과 정확히 일치한다.

**(b) Sundial-S·TTM-R2 실험은 실재한다 — 그리고 원 요약이 놓친 결정적 사실이 있다.**
해당 실험은 흩어져 있는 게 아니라 **사전학습 모델만 모은 전용 표**다. Table 1 캡션(축자):
> "The improvement of δ-Adapter on Pre-Trained models."

확보 수치(Ada-X = input nudging, Ada-Y = output residual correction):
| 백본 | 데이터 | 원본 MSE | Ada-X | Ada-Y |
|---|---|---|---|---|
| Sundial-S (univariate) | ELC | 0.427 | 0.334 | 0.404 |
| TTM-R2 (multivariate) | ELC | 0.180 | 0.167 | 0.168 |
| TTM-R2 (multivariate) | Weather | 0.150 | 0.148 | 0.143 |

⚠️ Sundial-S/Weather 행은 확보 응답이 "0.427→0.025"로 나왔는데, ELC 행과 원본값이 동일(0.427)하고
개선폭이 비현실적이라 **소형 모델의 전사 오류로 판단**한다. 이 행은 인용 금지, PDF 표 직접 확인 필요.

그 외 백본: DistPred, iTransformer, FourierGNN, FreTS, Autoformer, PatchTST, TimeMixer.
데이터셋 전체: ETTh1, ETTh2, ETTm1, ETTm2, ELC, Exchange, Traffic, Weather.
→ 원 요약의 "금융 특화 실험 없음, Exchange 정도만 금융 인접"은 **정확**하다.

**(c) Chronos·Moirai·TimesFM 언급 여부 — 본문 전체 검색 결과 "없음"으로 확정 가능.**
"Chronos", "Moirai", "TimesFM", "zero-shot"은 **0회**. "foundation model"은 Appendix A.3에 1회
("foundation-model initiatives, TimeGPT...OneFitAll...TimeLLM...UniTime...DAM that pre-train on
massive heterogeneous corpora"). 원 요약은 이를 "잠정 판단, 단정 금지"로 남겼으나 **이제 단정해도
된다** — 단, PDF 전문 기준의 검색이므로 참고문헌 표기 변형 가능성은 남는다.

**(d) 보정 컴포넌트 정의(축자, 신규 확보 — 원 요약의 미확인 항목 1번을 부분 해소)**
> Quantile Calibrator: "horizon-wise quantile functions as bounded offsets from the point forecast,
> with a monotonic parameterization and pinball-loss training."
> Conformal Corrector: "a scale function for normalized-residual conformal prediction, delivering
> finite-sample coverage with personalized, heteroscedastic intervals."

→ Conformal Corrector는 **normalized-residual(정규화 잔차) 콘포멀**이다. 우리가 검토 중인 분위수
보정/콘포멀과 같은 계열이며, 구현 재료로 그대로 쓸 수 있다. 저장소도 확인함(GitHub `Anoise/Adapter`,
"[ICLR26]" 표기, 하위 디렉터리 AdaCali / AdaIntpX / Adapter-X+Y) — 5단계 구현 시 참조 가능.

---

## 3. ProbFM — 콘포멀 예측 비교 실험 서술은 정확한가

### 판정: **원 요약에 사실오류가 있다. 그리고 오류의 방향은 우리에게 유리하다(위협 과대평가).**

**(a) ⚠️ Table 1은 성능 비교표가 아니라 분류(taxonomy) 표다 — 원 요약의 사실오류.**
원 요약은 "Table 1·4에서 콘포멀 예측을 실제 비교군에 넣어 트레이딩 지표상 우위를 주장한다"고 했으나,
Table 1은 손실함수 유형별로 대표 모델을 나열한 **관련연구 정리표**다:

| Loss Function | Probabilistic | Deep Learning | Foundation Models |
|---|---|---|---|
| Gaussian NLL | Yes | DeepAR, LSTM-NLL | – |
| Student-t NLL | Yes | Student-t RNN | Lag-Llama |
| Quantile Loss | Yes | TFT, DeepQuantile | – |
| Conformal Prediction | Yes | CP-LSTM | TimeGPT |
| Evidential Regression | Yes | Evidential LSTM/GRU | ProbFM (Ours) |

수치 비교는 **Table 4 하나뿐**이다. "Table 1·4에서" 표현은 수정해야 한다.

**(b) ⚠️ 결정적 — 콘포멀 대비 비교는 TSFM이 아니라 1층 LSTM에서 수행되었다.**
Abstract 축자:
> "we conduct an extensive controlled comparison study using a consistent LSTM architecture across five
> probabilistic methods: DER, Gaussian NLL, Student's-t NLL, Quantile Loss, and Conformal Prediction."

실험 설정 축자:
> "All methods use the same base model architecture: a 1-layer LSTM with 32 hidden dimensions."
> "By holding the architecture constant while varying only the probabilistic modeling approach, any
> observed differences ... can be directly attributed to the loss function and uncertainty estimation
> mechanism rather than confounding architectural factors."

**그리고 ProbFM의 트랜스포머 파운데이션 모델 자체는 논문에서 학습·평가되지 않는다.** 보고된 모든 결과가
1층 LSTM(은닉 32) 기반이다. Limitations(Appendix F)도 이를 자인한다:
> "Alternative Architectures: We focus on LSTM-based implementations. Other architectures may yield
> different trade-offs."

→ 함의: ProbFM은 "**사전학습 TSFM에서** 아키텍처 내장형 UQ가 사후 콘포멀 보정보다 낫다"를 **전혀
입증하지 않았다.** 논문 제목·초록의 "foundation model" 프레이밍과 실제 실험 사이에 간극이 있다.
우리 3번째 기여(동결 사전학습 TSFM + 사후 보정)와는 **비교 대상 자체가 다르다.**

**(c) Table 4의 실제 내용 — 비교 조건이 우리와 어떻게 다른가.**
BTC 단일 자산 트레이딩 성과:
| Method | Annual Sharpe | Sortino | Max DD (bps) | Calmar | Win Rate |
|---|---|---|---|---|---|
| MSE (Baseline) | 0.90 | 1.52 | -15.89 | 1.98 | 0.51 |
| Quantile Loss | 1.13 | 1.90 | -15.14 | 2.60 | 0.52 |
| **Adaptive Conformal (MSE)** | **0.98** | **1.64** | **-15.14** | **2.25** | **0.51** |
| **Evidential Regression (ProbFM core)** | **1.33** | **2.27** | **-15.14** | **3.04** | **0.52** |

우리 연구와 다른 점(방어 논거로 그대로 사용 가능):
1. **지표가 다르다.** Sharpe·Sortino·Calmar·승률 등 **트레이딩 성과 지표**이며, **CRPS도 캘리브레이션
   (PIT·커버리지)도 비교표에 없다.** 우리 논문의 핵심 지표가 여기서는 평가되지 않았다.
2. **자산군이 다르다.** 암호화폐 11종(ADA, BNB, BTC, DASH, DOGE, ETH, LTC, SOL, USDC, USDT, XRP),
   2020-01-01 ~ 2025-10-03 일별 로그수익률. Table 4는 그중 **BTC 단일 종목**. USDC·USDT 같은
   스테이블코인이 자산군에 포함된 점도 특기할 만하다(변동성 구조가 이질적).
3. **콘포멀 세팅이 빈약하다.** "Adaptive Conformal Prediction: Base predictor (MSE) + calibration set
   for intervals"가 전부이며, **명목 커버리지 수준도 콘포멀 변형(split/adaptive 세부)도 명시되지 않았다.**
   즉 사후 보정 쪽을 성실하게 튜닝한 비교라고 보기 어렵다.
4. **모델이 다르다.** 1층 LSTM vs 우리의 동결 사전학습 TSFM.

→ **"ProbFM이 사후 보정보다 우월함을 입증했다"는 위협 서술은 과대평가다.** 다만 인용 시
"ProbFM은 LSTM 통제실험에서 트레이딩 지표상 DER이 adaptive conformal을 앞섰다고 보고했다"까지는
정확히 밝히는 것이 공정하다.

**(d) 합성 통제실험 없음 — 원 요약의 판단 유지(CONFIRMED).** 다만 ProbFM이 말하는 "controlled
comparison study"는 **합성 데이터 통제가 아니라 아키텍처를 고정한 통제**라는 점을 구분해 서술해야
한다. 우리의 "파라메트릭 합성 통제실험"과 용어가 겹치므로 혼동 주의.

**Limitations 전문(Appendix F, 신규 확보, 축자)** — 4개 항목: Dataset Scope(암호화폐 11종 한정),
Market Regime Coverage, Transaction Costs(슬리피지·수수료·마켓임팩트 미반영), Alternative
Architectures(LSTM 한정).

---

## 4. 인용문 진위 검사 결과

전수 대조 결과 **날조 인용 1건, 축자 아닌 인용(truncation/오탈자) 5건**을 발견했다.

### 🚨 날조 — 원문에 존재하지 않는 문장
| 파일 | 인용된 문구 | 판정 |
|---|---|---|
| GLCP 원문노트 Abstract 절 / E요약 | `"applicability beyond financial contexts"` | **원문에 없음.** 실제 Abstract: "Additional results indicate that the framework extends beyond the motivating financial application." 실제 본문: "Although developed for financial commodity forecasting, the proposed framework is broadly applicable to forecasting problems involving related time series with heterogeneous temporal dynamics." → **인용부호 안의 문구는 원문 어디에도 없다. 즉시 삭제·교체 필요.** 과거 조작 인용 사례와 동일 패턴. |

### ⚠️ 축자 아님 — 의미는 보존되나 인용부호를 붙일 수 없음
| 파일 | 인용된 문구 | 실제 원문 |
|---|---|---|
| ProbFM | "...calibration guarantees required for effective decision-making." | 실제는 뒤에 **"in quantitative finance"**가 더 붙는다 (문장 중간에서 끊음) |
| ProbFM | "pre-specify distributional components and cannot distinguish between epistemic uncertainty and aleatoric uncertainty" | 실제는 괄호 설명 포함: "...epistemic uncertainty **(reducible through more data)** and aleatoric uncertainty **(irreducible data noise)**" |
| ProbFM | "We understand that the evaluation period may not capture all possible market regimes (e.g., extreme crashes, prolonged bear markets)." | 실제는 뒤에 **", in which we will further cover more market regimes in subsequent works"**가 이어짐 |
| GLCP | "typically define calibration relevance through **time**, covariates, or external similarity..." | 실제는 "through **temporal proximity**, covariates, or external similarity" (단어 다름) |
| GLCP | "the learned forecasting **regime** representation, enabling the same adaptive representation to support both forecasting" | 실제는 "the learned forecasting**-**regime representation, enabling the same adaptive representation to support both forecasting **and uncertainty quantification**" (하이픈, 문장 중간 절단) |

### ✅ 축자 확인 — 원문에 그대로 존재
ProbFM: "restrictive distributional assumptions, conflate different sources of uncertainty, or lack
principled calibration mechanisms" / "Deep Evidential Regression (DER) to provide principled
uncertainty quantification with explicit epistemic-aleatoric decomposition" / "ProbFM learns optimal
uncertainty representations through higher-order evidence learning while maintaining single-pass
computational efficiency" / "impose strong distributional assumptions that may not hold" /
"Conformal prediction provides coverage guarantees but operates post-hoc without integration into the
learning process, limiting its ability to provide nuanced uncertainty information for decision-making"
(원 요약은 앞 절반만 인용 — 의미 왜곡은 없음) / "This marks the *first* application of evidential
regression to time series foundation model architectures." / ECE·temperature scaling 대비 문장 /
"competitive forecasting accuracy while providing explicit epistemic-aleatoric uncertainty decomposition".

δ-Adapter: frozen 관련 2개 문장 모두 축자 확인. Abstract 전문 축자 확인.

GLCP: Abstract 전문 축자 확인. "reuses the forecasting model's learned predictive-state representation
as the localization variable, coupling point prediction and uncertainty calibration through the same
adaptive regime representation" / "typically assumes that adaptively combining multiple experts is
always beneficial" / "the validation-best expert as a stable forecasting anchor"(실제 "selects the
validation-best expert...") / "applies multi-scale corrections only when they improve validation
performance" / "market conditions evolve"(실제 "As market conditions evolve") / "forecasting models
that perform well in one period to deteriorate in another" / "Rather than proposing a new forecasting
backbone, ABF-T is a model-agnostic framework..." / Train·Val 분할 문장 / "Forecasting financial
commodity markets is fundamental to portfolio allocation, risk management, derivative pricing, and
trading." — **모두 축자 확인.**

수식 3도 원문과 일치 확인:
`w_g^(h,t,j) = λ^(t−g) · exp(−‖π_g^(h,j) − π_t^(h,j)‖²₂ / (2τ²))`,
"where λ∈(0,1] controls temporal recency and τ>0 determines the degree of gate-based localization."

---

## 5. 3개 잠정 결론에 대한 명시적 판정

| # | 잠정 결론 | 판정 | 근거 요약 |
|---|---|---|---|
| 1 | **ProbFM** — 정면충돌 아님 | **CONFIRMED** | 새 아키텍처(DER) 제안 논문이며 진단적 접근이 아님. 합성 통제실험 없음. 저자 스스로 콘포멀을 "operates post-hoc without integration into the learning process"로 별개 계열로 분리. **추가로**, 실험이 전부 1층 LSTM이라 사전학습 TSFM 영역과 겹치지도 않음 → 충돌 가능성은 원 판단보다 **더 낮다**. |
| 1b | **ProbFM** — 동기 근거로 인용 가능 | **PARTIALLY CONFIRMED (수정 필요)** | 인용 가능 자체는 유지(산업계 JPMorganChase도 TSFM UQ 공백을 인정). 단 E요약의 서술에 **사실오류 2건**(Table 1을 비교표로 오인, 비교 백본을 TSFM으로 암시)이 있어 수정 필수. 수정 후에는 **경고가 아니라 강화 근거**가 된다. |
| 2 | **δ-Adapter** — 정면충돌 아님 + 3번째 기여 재료로 흡수 | **CONFIRMED (강화)** | "post-hoc framework that improves frozen forecasters"(Conclusion 축자). Table 1이 **"Pre-Trained models" 전용 표**이고 Sundial-S·TTM-R2 수치 실재. Conformal Corrector = normalized-residual 콘포멀로 우리 계열과 동일. Chronos·Moirai·TimesFM 0회 → **우리 주 후보 모델에서의 검증은 여전히 공백**이며 이것이 우리 몫이다. |
| 3 | **GLCP** — 정면충돌 아님 + 3번째 기여 재료로 흡수 | **정면충돌 아님: CONFIRMED / 재료로 흡수: PARTIALLY CONFIRMED (수정 필요 — "흡수"는 과장)** | 프레임워크 안에서 예측기를 처음부터 학습(Train·Val로 fit)하고 게이트 π를 공유하는 설계이므로 동결 TSFM에 그대로 이식 불가 — 원 잠정 판단 **유지**. 논문 전체에 pretrained/frozen/Chronos/Moirai/TimesFM **0회**, foundation은 Future Work 1회. **단 "위험 신호"라는 원 요약의 성격 규정은 REVERSED**: Conclusion이 foundation backbone 통합을 미해결 과제로 명시했고, 게이트 입력 z가 부분적으로 예측기 비의존(변동성 요약)이라 대체 표현 설계가 가능하다. |

**총평**: 이번 검증에서 **잠정 결론이 REVERSED된 항목은 없다.** Moirai 사례 같은 결론 반전은 발생하지
않았다. 다만 (i) GLCP 인용문 1건이 **날조**로 확인되었고, (ii) ProbFM 항목에 **사실오류 2건**이
있었으며, (iii) GLCP를 "우리 설계와 정면으로 부딪힐 수 있는 위험"으로 규정한 성격 판단은 **원문
Conclusion 확보로 뒤집혔다**(위험 → 우리에게 유리한 공백 근거).

---

## 원 요약 파일에 반영이 필요한 수정 제안

`하위갈래E_신규경쟁문헌.md` 및 개별 원문 노트에 대한 수정 제안. **본 검증자는 직접 수정하지 않았다.**

### 🚨 최우선 (사실오류·날조)

**[E-1] GLCP 원문노트 및 E요약에서 `"applicability beyond financial contexts"` 인용을 삭제하라.**
원문에 존재하지 않는 날조 인용이다. 다음 축자 인용 중 하나로 교체:
- Abstract: "Additional results indicate that the framework extends beyond the motivating financial application."
- 본문: "Although developed for financial commodity forecasting, the proposed framework is broadly applicable to forecasting problems involving related time series with heterogeneous temporal dynamics."

**[E-2] ProbFM 행에서 "Table 1·4에서 콘포멀 예측을 실제 비교군에 넣어"를 "Table 4에서"로 수정하라.**
Table 1은 손실함수별 대표 모델을 나열한 **관련연구 분류표**이지 성능 비교표가 아니다.

**[E-3] ProbFM 행·종합소견에 "비교 실험의 백본은 1층 LSTM(은닉 32)이며, ProbFM의 트랜스포머 파운데이션
모델 자체는 논문에서 학습·평가되지 않았다"는 문장을 추가하라.** 근거: "All methods use the same base
model architecture: a 1-layer LSTM with 32 hidden dimensions." + Limitations "We focus on LSTM-based
implementations." 이는 ProbFM의 위협도를 크게 낮추는 사실이며, 현재 E요약은 이를 누락해 위협을
과대평가하고 있다.

**[E-4] GLCP 행의 성격 규정을 "위험 신호"에서 "우리 기여를 뒷받침하는 저자 진술"로 전환하라.**
현재 문구 "우리 3번째 기여의 설계 전제와 정면으로 부딪힐 수 있다 — Moirai 반전 오류와 유사한 유형의
위험"은 원문 Conclusion과 배치된다. 다음 축자 인용을 추가하고 서술을 교체:
> "Future work includes ... integrating stronger domain-specific or foundation forecasting backbones."
→ "GLCP 저자들 자신이 파운데이션 백본과의 결합을 미해결 과제로 명시했다. 즉 우리의 3번째 기여는
GLCP에 흡수되는 것이 아니라 GLCP가 남긴 빈칸을 메우는 위치에 있다."

### ⚠️ 중요 (표현 강도 조정)

**[E-5] 진행상황.md의 "GLCP를 3번째 기여 재료로 흡수" 표현을 낮춰라.** 제안 문구:
> "GLCP는 **아이디어 차용** 대상이다 — 국소화 개념(체제 표현 + 시간 근접성 기반 캘리브레이션 잔차
> 선택)과 국소화 가중치 형태(수식 3), 콘포멀 베이스라인 세트를 가져오되, **동결 사전학습 TSFM용
> 게이트-대체 표현의 설계·검증은 본 연구의 기여**로 남는다."

**[E-6] GLCP 원문노트에 게이트 입력 z의 정의를 추가하라(신규 확보, 3번째 기여 설계에 직결).**
> "the gate input z_{t,j} is constructed only from information in F_t, including asset-specific
> multi-scale volatility summaries and scale-expert signals, with no future outcome information."
→ z가 변동성 요약통계(예측기 비의존) + scale-expert 신호(예측기 의존)의 혼합이므로, 동결 TSFM에서는
전자를 그대로 재현하고 후자를 TSFM 출력(분위수 폭·샘플 분산 등)으로 대체하는 설계가 가능하다.
성립 조건은 Limitations가 명시: "If the gate fails to distinguish regimes, localized calibration may
be less effective."

**[E-7] δ-Adapter 행을 강화하라.** Table 1 캡션이 **"The improvement of δ-Adapter on Pre-Trained
models."**로, 사전학습 모델 전용 표라는 사실을 명시. Conclusion 축자("post-hoc framework that improves
frozen forecasters")를 인용 근거로 추가. Conformal Corrector가 **normalized-residual 콘포멀**임을 명시.

**[E-8] δ-Adapter의 Chronos·Moirai·TimesFM 언급 여부를 "확인 안 됨"에서 "본문 전문 검색 결과 0회"로
승격하라.** 단 참고문헌 표기 변형 가능성은 각주로 남길 것.

**[E-9] 축자 아닌 인용 5건(위 4절 표)의 인용부호를 제거하거나 원문 축자로 교체하라.** 특히 ProbFM의
"...required for effective decision-making."은 뒤에 "in quantitative finance"가 붙는다.

### 📌 보강 (신규 확보 정보 반영)

**[E-10]** GLCP 실험설정 추가: 원자재 선물 55종, 5분봉, 2022-08-01~2023-08-01. 수치: h=48 명목 90%에서
GLCP(Asym.) 커버리지 0.908/폭 3.06 vs ACI 0.907/폭 4.22; 점예측 h=48 MAE 5.59% 개선, h=96 MSE 15.02% 개선.
alternative backbone은 **PatchTST**(HAR 전문가 대비 검증용), 역시 프레임워크 내 학습.

**[E-11]** GLCP 콘포멀 베이스라인 목록을 별도 항목으로 기록: **ACI, AgACI, SAOCP, RCQR, EnbPI, RLCP,
MoECP**. 5단계 3번째 기여의 비교군 후보로 직접 사용. 특히 **RLCP**는 국소화 계열이라 우선순위 높음.

**[E-12]** ProbFM 비교조건을 우리 연구와 대조하는 표를 추가: 지표(트레이딩 성과 vs CRPS·캘리브레이션),
자산군(암호화폐 11종·Table 4는 BTC 단독 vs 합성 3축+미국 대표자산), 모델(1층 LSTM vs 동결 사전학습
TSFM), 콘포멀 세팅(명목 커버리지·변형 미명시 vs 명시적 설계). 이 표가 3번째 기여 방어의 핵심 논거다.

**[E-13]** ProbFM Limitations 4개 항목(Dataset Scope / Market Regime Coverage / Transaction Costs /
Alternative Architectures)을 원문노트에 추가. 특히 Transaction Costs 미반영은 Table 4 트레이딩 지표의
해석 한계를 보여주므로 인용 가치가 있다.

**[E-14]** δ-Adapter 저장소 정보 추가: GitHub `Anoise/Adapter`("[ICLR26]" 표기), 하위 디렉터리
AdaCali / AdaIntpX / Adapter-X+Y. 5단계 구현 시 참조. 데이터셋 전체 목록(ETTh1/h2/m1/m2, ELC,
Exchange, Traffic, Weather)도 확정 기록.

**[E-15]** 진행상황.md "확정된 차별점" 표의 δ-Adapter/GLCP 열을 분리하라. 현재 두 논문이 한 열로
묶여 있으나 성격이 전혀 다르다 — δ-Adapter는 **동결 사전학습 모델 대상 실증 있음**(Sundial-S·TTM-R2),
GLCP는 **동결 모델 대상 실증 없음**(from-scratch 프레임워크). "사전학습 TSFM" 행에서 δ-Adapter는 △가
아니라 ✅에 가깝고, GLCP는 ❌가 맞다.

---

## 여전히 확인 불가인 것

1. **δ-Adapter Table 1의 Sundial-S/Weather 행 수치** — 확보 응답이 "0.427→0.025"로 ELC 행과 원본값이
   중복되고 개선폭이 비현실적이다. **소형 모델 전사 오류로 판단하며, 인용 금지.** PDF 표를 사람이
   직접 확인해야 한다. TTM-R2 행과 Sundial-S/ELC 행도 마찬가지로 인용 전 재확인 권장.
2. **GLCP 저자 소속기관** — abs 페이지·HTML·PDF 어디서도 확보하지 못했다. (저자 구성상 KAUST 계열로
   추정되나 **추정일 뿐이며 근거 없이 기재 금지**.)
3. **3편의 References 목록 전체** — 여전히 미확보. 이들이 서로를 인용하는지, FinStressTS·Frequency
   Matters·Re(Visiting)를 인용하는지 확인 못 했다. 4단계 최종취합 전에 확인 권장.
4. **ProbFM의 콘포멀 명목 커버리지 수준과 변형(split/adaptive 세부)** — 원문에 명시가 없는 것으로
   보이나, Appendix 전문을 못 봤으므로 "논문에 없다"고 단정하지 않는다. 현재는 "본문 범위에서
   명시되지 않음"까지만 기술할 것.
5. **ProbFM 데이터 출처 "Stooq"** — 원 요약노트가 기재했으나 본 검증에서 확인하지 못했다. 자산 목록과
   기간은 확인됐으나 출처는 미확인이므로 인용 시 주의.
6. **ProbFM Method의 DER 손실함수 수식·coverage loss 정의** — 미확보. 우리 논문에서 ProbFM을 방법론
   수준으로 대조할 계획이라면 추가 확보 필요(현재 계획상으로는 동기 근거 인용이므로 필수는 아님).
7. **GLCP 수식 3 이외의 Method 수식(게이트 네트워크 g_θ의 구조·학습 목적함수)** — "we learn an
   asset-specific gating network" 수준의 서술만 확보. **우리가 게이트-대체 표현을 설계하려면 이
   부분이 필요하므로 5단계 착수 전 PDF 정독 필수.**
8. **본 검증 자체의 한계** — 모든 원문 접근이 `WebFetch`(소형 모델 가공 응답)를 경유했다. 축자 인용
   확인은 "존재/부재" 판정 신뢰도가 높으나, **표의 숫자는 전사 오류에 취약**하다(위 1번이 실례).
   Table 4(ProbFM)·GLCP 커버리지 수치도 논문에 실제로 기재하기 전에는 PDF를 사람이 직접 대조할 것.
