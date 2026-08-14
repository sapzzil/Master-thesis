# 하위갈래 D — TSFM 한계·실패 분석 (Negative Transfer / 도메인 적응 실패 / 사전학습 코퍼스 편향)

> 작성일: 2026-08-12
> 목적: "사전학습 TSFM의 불확실성 추정은 금융 데이터의 어떤 성질에서 붕괴하는가"라는 연구질문을 뒷받침할
> negative transfer·도메인 적응 실패·사전학습 코퍼스 편향 관련 선행연구 확장 조사.
> 이미 정독된 핵심 3편(Frequency Matters 2511.05619, Re(Visiting) 2511.18578, Internal Semantics 2511.15324)은
> 재정독하지 않고, 이들이 속한 문제의식(왜 TSFM이 이질적 도메인에서 무너지는가)을 뒷받침하는 **주변 문헌**을 찾았다.

## 원문 확인 방식에 대한 정직한 고지

- 모든 표의 "핵심 주장" 항목은 **arXiv abstract 페이지 원문(meta-citation_abstract 또는 렌더된 Abstract 문단)을 web_fetch로 직접 확인**했다.
- `Mix, Don't Pick`(2606.09912)만 HTML 전문(§1~§4, Conclusion, Impact Statement)까지 받아 대조했다. 나머지는 **Abstract/Introduction 수준까지만 확인**했고, 본문 실험 세부(수치·표)는 미확인이다 — 이 점을 표에 명시했다.
- `Dual Adaptation of TSFM for Financial Forecasting`(ICML 2025)은 OpenReview 원문이 봇 차단 페이지로 막혀 **1차 원문 확인 실패**. WebSearch가 반환한 요약문만 확보했으므로 신뢰도를 낮게 표시했다.
- Chronos 질소 예측 논문(ScienceDirect, negative transfer 사례로 검색됨)은 유료 게재지라 **원문 미확인**. 검색 스니펫에서만 "negative transfer" 사례가 언급됨 — 인용 금지, 참고용으로만 표에 남김.
- 두 번째 web_fetch 시도(`dl.acm.org` "Time-Series Foundation Models in Finance: Pretraining Corpora..." 논문)는 **빈 응답으로 접근 실패** — 확인 불가로 표시, 인용 금지.

---

## 논문별 표

| 논문명 | arXiv ID / 출처 | 원문 확인 수준 | 핵심 주장 (원문 근거) | negative transfer / 도메인실패와의 관련성 |
|---|---|---|---|---|
| **Mix, Don't Pick: Why Synthetic Corpus Composition Matters for TSFM Pretraining** | arXiv 2606.09912 | **[3단계 검증에서 정정] 부분 확인**(Abstract~Conclusion·Impact Statement·References는 확인했으나 Appendix B~I는 미확보 — "전문 확인"은 과장이었음) | "Choosing the wrong synthetic generator... under identical training budgets, the best and worst generators produce up to a 2× gap in forecasting error" (Abstract, 축자 일치). ~~"generator rankings differ substantially between Chronos-T5-Mini and Moirai-Small"~~ **[3단계 검증에서 정정] 이 문장은 원문에 없음(인용부호 오용). 실제 원문은 "generator rankings are not stable across architectures"** — 의미는 보존되나 직접인용 표기가 부적절했으므로 인용부호 없이 서술할 것. Conclusion: "synthetic data should not be treated as a monolithic category. Different generators encode different temporal structures, and their usefulness depends on how those structures interact with the model architecture and the downstream evaluation distribution." | **사전학습 코퍼스 편향의 직접 증거.** 합성 데이터 생성기 선택 자체가 다운스트림 성능을 2배 가르고, 그 순위가 모델 아키텍처마다 달라짐 — 즉 "코퍼스 구성 = 모델 특이적 성능 결정 요인"이라는 우리 연구의 핵심 전제(TSFM 붕괴가 모델·도메인 상호작용에서 온다는 것)를 뒷받침. Impact Statement에서 "finance"를 명시적으로 언급하며 코퍼스 구성이 downstream reliability에 영향을 준다고 경고. |
| **Are Time-Series Foundation Models Deployment-Ready? A Systematic Study of Adversarial Robustness Across Domains** | arXiv 2505.19397 (v2) | **[3단계 검증에서 정정] 완전 확인**(Abstract부터 Discussion/Broader Impacts까지 본문 전체 확보 — "Abstract+Introduction만"은 과소평가였음) | "even minimal perturbations can induce significant and controllable changes in forecast behaviors—including trend reversal, temporal drift, and amplitude shift" (Abstract). "we identify potential architectural designs, such as structural sparsity and multi-task pretraining, that may improve robustness." 6개 TSFM(TimesFM, UniTS, Moirai, TabPFN-TS, Chronos, TimeMoE)을 energy/weather/transportation/web/healthcare/sales 도메인에서 평가. | **엄밀히는 적대적 강건성 논문**(자연적 도메인 이동이 아닌 의도적 섭동)이라 "negative transfer"와 동일 현상은 아니지만, "TSFM이 도메인 간 일관되게 취약(consistent vulnerabilities across models)"하다는 결론은 우리의 "TSFM 붕괴가 어떤 도메인 성질에서 발생하는가" 질문과 인접. 금융(financial manipulation)을 고위험 시나리오로 명시. **주의: 우리 논문에서 negative transfer의 직접 근거로 쓰면 안 되고, "TSFM 전반의 취약성" 배경 문헌으로만 인용.** |
| **Out-of-Distribution Generalization in Time Series: A Survey** | arXiv 2503.13868 (v3, Information Fusion 2026 게재) | Abstract만 확인 | "Time series frequently manifest distribution shifts, diverse latent features, and non-stationary learning dynamics... We organize our analysis across three foundational dimensions: data distribution, representation learning, and OOD evaluation." (Abstract) | TSFM 특정 논문이 아니라 **시계열 OOD 일반화 방법론 서베이**. Negative transfer의 상위 개념(분포이동 하에서의 일반화 실패)을 체계적으로 정리한 1차 서베이로, 우리 논문 서론에서 "OOD 일반화" 개념 정의·분류체계 인용에 유용. 금융 도메인 특정 논의는 확인 못 함(본문 미확인). |
| **The Impact of Data Set Similarity and Diversity on Transfer Learning Success in Time Series Forecasting** | arXiv 2404.06198 (v2) | **[3단계 검증에서 정정] Abstract~6장 도입부까지 확인**("Abstract만"은 과소평가였음. 로컬 사본은 6장 본문 중간에서 절단됨) | "source-target similarity reduces forecasting bias, while source diversity improves forecasting accuracy and uncertainty estimation, **but increases the bias**" (Abstract). 5개 공개 소스 데이터셋 → 5개 타겟(실제 도매 데이터 포함)에 대해 zero-shot·fine-tuned 예측의 accuracy/bias/**uncertainty estimation**을 체계적으로 측정. | **가장 직접적으로 관련된 논문.** 우리 연구질문("불확실성 추정이 무너지는 조건")과 동일한 세 축(accuracy, bias, uncertainty estimation)을 이미 다뤘고, "소스 다양성이 불확실성 추정을 개선하지만 편향은 늘린다"는 트레이드오프를 실증. 다만 (a) TSFM이 아니라 사전학습 신경망 일반, (b) 금융 도메인 미포함, (c) 다양성-유사성 척도가 우리의 "금융 메커니즘 축"과 다름 — 이 지점이 우리 논문의 차별점(금융 특이 메커니즘 축으로 세분화)을 강화하는 근거로 쓸 수 있음. |
| **Estimating Time Series Foundation Model Transferability (TimeTic)** | arXiv 2509.23695 | Abstract 확인 | "TSFMs offer strong zero-shot forecasting via large-scale pre-training, yet fine-tuning remains critical for boosting performance in domains with limited public data... efficiently identifying the best model for downstream fine-tuning becomes increasingly challenging." In-context-learning 기반 전이가능성 예측 프레임워크(TimeTic) 제안, 10개 데이터셋·10개 TSFM·3개 예측과제 벤치마크. | 전이가능성을 **사전에 예측**하려는 시도 자체가 "어떤 소스-타겟 조합에서 전이가 실패(=negative transfer)하는지 사전에 알 수 없다"는 문제의식의 방증. 우리 연구는 "사후 진단"이 아니라 "합성 통제실험으로 붕괴 조건을 원인별로 분해"한다는 점에서 접근이 다름 — 상호보완적 인용 가능. **[3단계 검증에서 정정]** 금융 도메인 언급은 Abstract에는 없지만 **Introduction 첫 문단에 "...such as healthcare and finance (Fu et al., 2024)"로 명시**되어 있음(로컬 사본이 완전 확보 상태라 확인 가능했음). |
| **Dual Adaptation of Time-Series Foundation Models for Financial Forecasting** | ICML 2025 (OpenReview id: SSdBpVNYxd) — **arXiv ID 확인 불가** | **원문 접근 실패**(OpenReview 봇차단). WebSearch 요약만 확보 | (2차 출처, 신뢰도 낮음) TimesFM 기반 경량 어댑터: "Generalizer Adapter"(자산 간 공통 시간 패턴 학습) + "Identity Signature"(자산별 고유신호). 추론 시 Identity Signature를 제거해 미지 자산에 일반화. "The application of foundation models to finance remains constrained by data scarcity, volatility, and overfitting." | 도메인 적응 실패(정확히는 "실패를 막기 위한 대응책") 사례로 인용 가능성 있으나 **원문 미확인 상태이므로 논문에 직접 인용 금지**. 재확인이 필요하면 별도 세션에서 OpenReview 로그인 후 재시도하거나 ICML 2025 프로시딩 PDF를 직접 검색할 것. |
| ~~Chronos 질소 예측 논문 (negative transfer 사례)~~ | ScienceDirect (S2589914725001677) | **원문 미확인** — 검색 스니펫만 존재 | "For long-term 48h forecasts, transferring from a low-complexity station to a high-complexity one caused negative transfer" (검색 엔진 요약, 원문 대조 안 됨) | 구체적인 "negative transfer" 실증 사례로 매력적이나 **1차 확인 없이는 인용 금지**. 유료 게재지라 이번 조사에서 접근 불가. |
| ~~Time-Series Foundation Models in Finance: Pretraining Corpora, Architectures... (ACM)~~ | ACM DL (10.1145/3785706.3785728) | **접근 실패**(빈 응답) | 확인 불가 | 제목상 금융 TSFM 사전학습 코퍼스 편향을 정면으로 다룰 것으로 보이나 **원문을 전혀 확인하지 못함**. 인용 금지. 재시도 가치 있음(다른 경로로 PDF 확보 시도 권장). |

---

## 확인하지 못한 것 (명시)

1. ~~Frequency Matters / Re(Visiting) / Internal Semantics 세 편의 참고문헌 목록을 재확인하지 않았다~~ →
   **[3단계 검증에서 완료]** 세 논문의 References를 전수 확인함(Frequency Matters 17건, Re(Visiting) 66건 —
   Chrome `javascript_tool`로 `.ltx_bibitem` 노드 직접 추출, Internal Semantics 15건, 총 98건). **negative
   transfer·도메인 적응 실패·사전학습 코퍼스 편향을 주제로 하는 인용문헌은 0건.** 세 논문 모두 자기 자신의
   실패 사례만 보고할 뿐 선행 실패연구를 인용하지 않으며, 서로도 인용하지 않는다(단 셋 다 2025년 11월
   arXiv 동시기 공개라 상호인용이 물리적으로 어려웠을 수 있다는 단서 병기 필요 — 공정성을 위해). 결론:
   **원 요약이 독립 키워드 검색으로 대체한 것은 결과적으로 문헌 손실이 없었다.**
   - 인접 신규 후보 3건(원문 미확인, 최하 신뢰도): arXiv 2510.03358(Rank Structure/Flow-of-ranks),
     arXiv 2409.12915(Wiliński et al. — Internal Semantics가 스스로 밝힌 최근접 선행연구인데 우리 목록에
     없었음, 추가 확인 권장), Cartea et al. 2025 "The Limited Virtue of Complexity in a Noisy World"
     (저SNR이 대형모델을 무너뜨린다는 금융계량 쪽 대응물 — 우리 연구의 SNR 축과 개념적으로 직결되어
     우선순위 높음)
2. Dual Adaptation 논문과 Chronos 질소예측 논문, ACM 논문 3편은 원문 미확인 — 표에 취소선으로 표시하고 인용 금지 처리(3단계 검증에서도 재확보 시도 안 함, 상태 유지).
3. 나머지 4편(2606.09912 제외)은 본문 실험 결과(구체적 수치·표)까지는 확인하지 못했고 Abstract/Introduction 수준 확인에 그쳤다. 논문에 구체적 수치를 인용하려면 재방문 필요.

---

## 종합 소견 — "금융 데이터의 어떤 성질이 TSFM을 무너뜨리는가"와의 연결

이번 조사에서 확보한 문헌들은 negative transfer·도메인 적응 실패를 크게 두 갈래로 설명한다. 하나는 **사전학습 코퍼스 구성 문제**(Mix, Don't Pick)로, 어떤 데이터/생성기를 얼마나 섞느냐가 다운스트림 성능을 2배까지 가르고 그 최적 구성이 모델 아키텍처마다 다르다는 것이다. 이는 우리가 이미 확보한 "TSFM마다 금융 데이터에서의 승패가 갈린다"(Brini: TTM만 승리, Re(Visiting): 전반적 부진, arXiv 2606.27100: 8/10 승리)는 문헌 간 모순을, "모델별로 사전학습 코퍼스가 다르고 그 코퍼스가 금융과 얼마나 이질적인가가 다르기 때문"이라는 메커니즘으로 설명할 수 있는 여지를 준다. 다만 이 논문은 금융 도메인을 직접 다루지 않으므로, 우리 논문에서는 "코퍼스 편향이 존재한다는 일반 원리"의 근거로만 쓰고 금융 특이적 주장에는 쓸 수 없다.

다른 하나는 **소스-타겟 유사성/다양성이 불확실성 추정에 미치는 영향**(arXiv 2404.06198)이다. 이 논문은 우리 연구질문과 거의 동일한 세 지표(accuracy, bias, uncertainty estimation)를 다루면서 "소스 다양성이 불확실성 추정을 개선하지만 편향은 늘린다"는 트레이드오프를 이미 실증했다 — 즉 **"불확실성 추정 붕괴"라는 현상 자체는 TSFM 이전부터 전이학습 일반에서 관찰되어 온 것**이며, 우리 논문의 기여는 이를 (a) 사전학습 TSFM이라는 특정 모델군에, (b) 금융이라는 특정 타겟 도메인에, (c) 파라메트릭 합성 통제라는 방법론으로 좁혀 원인을 분해한다는 점에 있다. 이 논문이 쓴 "유사성/다양성" 척도는 우리가 쓸 "SNR·자기상관·비정상성·변동성 군집·체제전환"이라는 금융 메커니즘 축보다 훨씬 일반적(feature-based)이어서, 우리 쪽이 더 해석 가능하고 금융에 특화된 진단을 제공한다는 차별점 주장이 가능하다.

한편 적대적 강건성 논문(2505.19397)과 OOD 서베이(2503.13868)는 "TSFM이 도메인 전반에서 구조적으로 취약하다"는 배경을 넓게 뒷받침하지만, 금융이라는 특정 도메인이나 불확실성 추정(CRPS·캘리브레이션)이라는 특정 지표를 다루지 않는다. 이들은 논문 서론의 동기 부여("TSFM의 실패는 일반적 현상이며 금융도 예외가 아니다")에 배경 문헌으로 쓰되, 우리 연구의 공백(negative transfer 실증은 있지만 금융×불확실성 추정 교집합은 비어 있음)을 재확인하는 용도로만 사용해야 한다. TimeTic(2509.23695)은 "어떤 조합에서 전이가 실패할지 사전에 알 수 없다"는 문제의식을 공유하지만 예측(prediction) 접근이라 우리의 원인 분해(diagnosis) 접근과는 상보적 관계로 인용 가능하다.

---

## 레퍼런스 관리용 요약 (BibTeX 등록 후보)

| 우선순위 | 논문 | 등록 권장 여부 |
|---|---|---|
| 높음 | Mix, Don't Pick (2606.09912) | 등록 권장 — 전문 확인됨 |
| 높음 | Impact of dataset similarity/diversity on TL (2404.06198) | 등록 권장 — 연구질문과 직결 |
| 중간 | OOD Generalization in Time Series Survey (2503.13868) | 등록 권장 — 개념 정의용 |
| 중간 | Adversarial Robustness of TSFMs (2505.19397) | 등록 권장 — 배경 문헌 |
| 중간 | TimeTic (2509.23695) | 등록 권장 — 상보적 접근 |
| 보류 | Dual Adaptation (ICML 2025) | 원문 재확인 후 등록 |
| 금지 | Chronos 질소예측 (ScienceDirect) | 원문 확보 전까지 인용 금지 |
| 금지 | ACM Pretraining Corpora in Finance | 원문 확보 전까지 인용 금지 |
