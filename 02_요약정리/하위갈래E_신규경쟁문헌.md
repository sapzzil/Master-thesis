# 하위갈래 E — 신규 경쟁문헌 (ProbFM / δ-Adapter / GLCP)

> 작성일: 2026-08-24
> 목적: 진행상황.md에 "[미확인] — 초록 수준 스크리닝만 완료, 정식 대조 미착수"로 표시되어 있던 3편
> (ProbFM, δ-Adapter, GLCP)을 정식 2단계 절차(원문 확보 → 구조화 요약)로 처리. 잠정 결론("정면충돌
> 아님, ProbFM은 동기 근거·δ-Adapter/GLCP는 3번째 기여 재료로 흡수")이 원문 대조에서도 유지되는지가
> 핵심 질문. 3단계 교차검증(Opus, 별도 세션)에서 재확인.

## 원문 확인 방식에 대한 정직한 고지

- 3편 모두 arXiv HTML 페이지(`arxiv.org/html/{id}`, ProbFM·δ-Adapter는 버전 미지정 URL, GLCP는
  `v1` 명시)를 `WebFetch` 도구로 조회했다. `WebFetch`는 페이지를 가져와 **소형 모델이 프롬프트에 맞춰
  가공한 응답**을 반환하는 방식이라, 원문 HTML 전체를 그대로 받아오지 못했다. 각 논문당 2~3회의
  질의로 Abstract·Introduction·Related Work·Method 일부·Conclusion 일부를 확보했으며, **큰따옴표로
  감싼 문장만 원문 직접인용으로 간주**하고 그 외 서술은 소형 모델의 요약/해석이므로 논문에 그대로
  인용하지 말 것.
- GLCP(2607.23165)는 `/html/` 엔드포인트에서 두 차례 HTTP 429(rate limit)를 겪어 재시도 간격을
  60~100초로 늘려 확보했다. 원문 대비 확보 비중이 셋 중 가장 낮다(Method·Conclusion 절 원문 텍스트
  미확보, 소형 모델의 해석적 요약에 의존한 부분이 있음) — **교차검증 1순위 대상**.
- Method 섹션의 수식·정확한 실험 수치(Table 값), Related Work 전문, References 목록은 **3편 모두
  미확보**. Appendix도 미확보.
- 각 논문의 상세 확보 내용·미확인 사항은 `01_자료원문/`의 개별 파일 참조:
  `2601.10591_ProbFM_...md`, `2601.20280_deltaAdapter_...md`, `2607.23165_GLCP_ABF-T_...md`.

---

## 논문별 표

| 논문명 | arXiv ID / 출처 | 원문 확인 수준 | 핵심 주장 (원문 근거) | 우리 연구와의 관계 |
|---|---|---|---|---|
| **ProbFM: Probabilistic Time Series Foundation Model with Uncertainty Decomposition** | arXiv 2601.10591 (JPMorganChase) | **부분** — Abstract·Introduction·Related Work 일부·실험 설계·Limitations 확인. Method 수식·Table 수치·References 미확보 | Deep Evidential Regression(DER) 기반 신규 TSFM 아키텍처. "current TSFMs...fail to provide the principled uncertainty decomposition and calibration guarantees" (원문). 콘포멀 예측을 "operates post-hoc without integration into the learning process"로 명시적 대비. "first application of evidential regression to time series foundation model architectures." 실험은 **암호화폐 실거래 데이터**(11자산, 2020.1~2025.10)만 사용 — **파라메트릭 합성 통제실험 없음**. Limitations에서 "may not capture all possible market regimes (e.g., extreme crashes, prolonged bear markets)" 자인. | **새 아키텍처 제안 논문이며, 우리의 진단적(diagnostic) 접근과는 다르다는 원 판단이 원문 대조에서도 유지됨.** 다만 ⚠️ **부분 수정 필요**: Table 1·4에서 콘포멀 예측을 실제 비교군에 넣어 트레이딩 지표상 우위를 주장한다는 점이 확인됨 — "정면충돌 아님"은 유지되나, "동기 근거"로만 쓸 때 "ProbFM 자신도 사후 보정과의 성능 비교를 이미 시도했다"는 사실을 반드시 함께 밝혀야 공정함(우리 3번째 기여의 차별점을 자산군·지표·실험설계 차이로 명시적으로 논증할 것). |
| **The Forecast After the Forecast: A Post-Processing Shift in Time Series (δ-Adapter)** | arXiv 2601.20280 (ICLR 2026) | **부분** — Abstract·모델-불가지성 서술·Introduction 일부·frozen-model 적용 방식 확인. Method 수식·실험 수치·References 미확보 | 재학습 없이 배포된 예측기를 개선하는 경량·모델-불가지 어댑터. "We keep all parameters of F fixed and introduce a lightweight, learnable adapter A_θ" — **베이스 모델을 동결한 진짜 사후(post-hoc) 방법 확인됨.** Quantile Calibrator·Conformal Corrector로 구간예측 보정. **Sundial-S, TTM-R2를 포함한 다수 SOTA 백본에서 검증** — 이 중 Sundial·TTM은 우리가 검토 중인 사전학습 TSFM 후보와 겹침. 금융/체제전환 특화 논의는 확인 안 됨(Exchange 데이터셋 정도만 금융 인접). | **model-agnostic 사후 보정 방법론 원 논문이라는 원 판단이 원문 대조에서 확인·강화됨.** 정면충돌 아니며 3번째 기여(사후 보정)의 구현 방법론 재료로 흡수 가능 — 오히려 Sundial-S·TTM-R2 실험이 있다는 것은 **우리 후보 모델과 직접 겹치는 선행 검증 사례**이므로 인용 가치가 원 판단보다 높아짐. Quantile Calibrator/Conformal Corrector의 정확한 수식은 재확인 필요. |
| **Adaptive Multi-Scale Forecasting and Gate-Localized Conformal Prediction (ABF-T-GLCP)** | arXiv 2607.23165 | **부분(셋 중 가장 얕음)** — Abstract·Introduction/Related Work 일부·Method 일부(수식 3, 게이트 의존성 서술) 확인. Method 전문·실험 수치·Conclusion 원문·References 미확보. 429 rate limit로 재시도 다수 | "model-agnostic framework for forecasting and uncertainty quantification in nonstationary multivariate time series." GLCP는 "the learned gate state, together with temporal recency, to select locally relevant calibration residuals"를 사용. 금융 원자재(commodity) 예측 실험, 비정상성(nonstationarity)을 핵심 동기로 명시 — 체제전환 축과 개념적으로 직결. **그러나 ABF-T는 "trained-from-scratch forecasters"를 대상으로 설계됨**("the Train and Val sets are used to fit the forecasting model")이며, GLCP의 국소화 가중치(수식 3)는 **ABF-T 자체의 학습된 게이팅 네트워크가 산출하는 게이트 벡터 π에 의존**한다. | ⚠️ **원 판단("정면충돌 아니고 3번째 기여의 재료로 흡수 예정")에 대한 수정 필요 가능성 — 이번 조사에서 발견된 가장 중요한 사실.** GLCP가 말하는 "model-agnostic"은 콘포멀 예측 일반의 속성(어떤 점예측기에도 사후 결합 가능하다는 것)을 가리키는 것으로 보이며, GLCP의 핵심 메커니즘(게이트 기반 국소화)은 ABF-T가 처음부터 학습시켜 만든 게이트 표현에 종속적이다. **동결된 사전학습 TSFM(Chronos·Moirai 등)의 출력에 GLCP를 그대로 이식할 수 있는지는 원문에서 확인되지 않았다** — 대안적 게이트 구성 방법에 대한 논의가 있는지가 관건이며 아직 미확인. 지금 단계의 잠정 결론: **"GLCP를 그대로 흡수"가 아니라 "GLCP의 국소화 아이디어(게이트/레짐 상태 기반 보정 잔차 선택)만 개념적으로 차용하고, 우리가 직접 사전학습 TSFM용 게이트-대체 표현(예: 모델의 은닉상태·예측분포 폭 등)을 설계"하는 쪽으로 3번째 기여를 재구성해야 할 가능성이 있다.** 정면충돌은 아니지만("GLCP는 처음부터 학습하는 예측기+보정을 결합한 프레임워크"이고 우리는 "동결 TSFM + 사후 보정"이라 연구 설계 자체가 다름), 흡수 가능성은 원 판단보다 제한적. |

---

## 확인하지 못한 것 (명시)

1. **GLCP Method 섹션 전문·Appendix** — 사전학습·동결 모델에 대한 대안 게이트 구성법을 논문이 논의하는지
   여부. 이것이 확인되기 전까지 GLCP를 3번째 기여의 직접 구현 재료로 확정하지 말 것.
2. **ProbFM Table 1·4의 정확한 수치** — 콘포멀 예측 대비 우위 폭이 어느 정도인지, 어떤 캘리브레이션
   세팅(커버리지 수준 등)에서 비교했는지 미확인. 이 수치를 확인해야 "3번째 기여가 왜 여전히 유효한가"를
   더 정밀하게 방어할 수 있음.
3. **δ-Adapter의 Sundial-S·TTM-R2 실험 정확한 수치·설정** — 우리 후보 모델과 겹치므로 재확인 우선순위
   높음. Chronos·Moirai·TimesFM에 대한 언급 여부도 본문 전체를 봐야 확정 가능(현재는 "확인 안 됨"이지
   "없다"고 단정한 것이 아님).
4. 3편 모두 References 목록 미확인 — 이들이 서로를 인용하는지, 우리가 이미 확보한 FinStressTS·
   Frequency Matters·Re(Visiting) 등을 인용하는지 확인 안 됨.
5. 3편의 저자 소속 중 GLCP는 확인 못 함.

---

## 종합 소견 — 잠정 결론이 원문 대조에서 얼마나 유지되는가

**ProbFM**: 원 판단 유지. 새 아키텍처(DER) 제안 논문으로, 진단적 접근인 우리 연구와 방법론적으로
다르다. 다만 콘포멀 예측과의 직접 비교 실험이 있다는 사실은 "동기 근거로만 인용"할 때 함께 밝혀야
공정하다 — ProbFM이 이미 "아키텍처 내장형이 사후 보정보다 낫다"고 주장한 맥락(크립토 트레이딩,
Evidential Regression vs conformal prediction)과 우리가 검증하려는 맥락(금융 메커니즘 다축 합성
통제 + 사전학습 TSFM 동결 + 사후 보정)이 다르다는 것을 명시적으로 논증해야 함.

**δ-Adapter**: 원 판단 유지·강화. 진짜 사후·모델동결형 보정 방법이며, 심지어 우리 후보 모델(Sundial,
TTM)에서 이미 검증된 사례가 있어 3번째 기여의 구현 방법론 재료로서 인용 가치가 원래 판단보다 높다.

**GLCP**: **원 판단에 수정이 필요할 가능성이 가장 높은 문헌.** "model-agnostic"이라는 표현과 실제
메커니즘(ABF-T의 학습된 게이트에 의존) 사이에 괴리가 있어 보인다. 이는 과거 3단계 교차검증에서
"초록 수준 판단이 원문에서 뒤집힌 전례"(Moirai 반전 오류)와 유사한 유형의 위험 신호다. 다만 이번
조사는 Method 섹션 전문을 확보하지 못한 상태에서 내린 잠정 판단이므로, **Opus 교차검증에서 이 지점을
최우선으로 재확인**해야 한다 — 특히 (a) GLCP가 사전학습 모델에 적용 가능한 대안 게이트 구성법을
논문 어딘가에서 논의하는지, (b) 우리가 "GLCP를 흡수"가 아니라 "GLCP의 아이디어만 차용해 재설계"로
표현을 낮춰야 하는지.
