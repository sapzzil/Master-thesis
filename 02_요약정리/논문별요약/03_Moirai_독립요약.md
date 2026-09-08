# Moirai (2402.02592) 독립 정독 요약

> **중요 전제**: 확보된 원문 파일 자체가 "부분 수집" 상태다. 파일 상단의 메타데이터에 "서론~3장 Method의 Problem Formulation 도입부까지만 확보, Related Work 이후 3장 나머지, 4장 실험, 결론, Appendix A~D 전체는 미확보"라고 명시되어 있고, 실제로 본문은 3장 "Problem Formulation" 문단이 수식 정의 도중(N개 시계열 데이터셋 D의 표기를 정의하는 중) 끊긴 채 종료된다. 따라서 아래 요약은 **Abstract, 1장 Introduction, Table 1, 2장 Related Work, 3장 Problem Formulation 도입부**에서 직접 읽은 내용만을 근거로 하며, 아키텍처 세부 구조(마스크 인코더, Any-variate Attention의 구체적 수식, 확률적 출력 헤드), LOTSA 데이터셋의 도메인별 상세 수치, 실험 결과, 저자가 명시한 한계(Limitations 절)는 **원문에서 확인할 수 없어 이 요약에 포함하지 않는다.** 해당 항목들은 미확보 구간에 있을 가능성이 높다.

## 서지정보
- 제목: Unified Training of Universal Time Series Forecasting Transformers
- 저자: Gerald Woo, Chenghao Liu, Akshat Kumar, Caiming Xiong, Silvio Savarese, Doyen Sahoo (Salesforce AI Research)
- arXiv ID: 2402.02592
- 코드/데이터/가중치: https://github.com/SalesforceAIResearch/uni2ts

## 한 줄 요약
시계열 데이터의 이질성(빈도, 변량 수, 분포 특성) 문제를 해결하는 새로운 마스크 인코더 기반 Transformer 아키텍처 Moirai를, 9개 도메인·270억(27B) 개 이상의 관측치로 구성된 대규모 오픈 시계열 아카이브 LOTSA로 사전학습하여, 제로샷으로도 완전학습(full-shot) 베이스라인과 경쟁하거나 능가하는 "범용 시계열 예측(universal forecasting)" 모델을 제시한다.

## 문제의식/동기
- 기존 딥러닝 시계열 예측은 "데이터셋 하나당 모델 하나(one-model-per-dataset)" 프레임워크에 머물러 있어, 비전·언어 분야에서 대규모 사전학습 모델이 보여준 전이학습의 이점(데이터 효율성, 성능 향상)을 활용하지 못하고 있다.
- 범용 예측(universal forecasting) 모델—하나의 대규모 사전학습 모델이 임의의 시계열 예측 문제를 다룰 수 있는 모델—을 구축하는 데는 시계열 데이터 고유의 세 가지 난제가 있다고 저자들은 규정한다.
  1. **교차 빈도 학습(cross-frequency learning)**: 분(minutely)·시간(hourly)·일(daily) 등 샘플링 빈도가 시계열의 패턴을 좌우하는데, 서로 다른 빈도를 함께 학습하면 부정적 간섭(negative interference)이 발생한다는 선행연구(Van Ness et al., 2023)가 있으며, 기존 연구들은 빈도별로 별도 모델을 학습해 이 문제를 회피해 왔다(Oreshkin et al., 2020).
  2. **임의 변량 수 처리(any-variate)**: 다변량 시계열은 데이터셋마다 변량 수가 다르고, 각 변량이 의미상 서로 다른 양을 측정한다. 변량을 독립적으로 취급하면(Nie et al., 2023; Ekambaram et al., 2023) 문제를 피할 수 있지만, 범용 모델은 다변량 상호작용과 외생 공변량(exogenous covariates)까지 유연하게 다룰 수 있어야 한다.
  3. **분포 특성의 다양성**: 확률적 예측(probabilistic forecasting)은 실무자에게 중요한 요구사항이지만, 데이터셋마다 지지집합(support)과 분포 특성이 달라—예를 들어 양수 시계열에는 대칭 분포(정규분포, Student-T 등)가 부적합함—표준적인 단일 파라메트릭 분포 사전 지정 방식(Salinas et al., 2020, 즉 DeepAR류)은 대규모 데이터의 다양성을 담기에 유연성이 부족하다.
  4. (부차적으로) 범용 모델 학습에 필요한 충분히 크고 다양한 도메인의 시계열 데이터셋이 기존에는 부재했다.

## 방법론
원문에서 확인 가능한 범위는 다음과 같다(구체적 수식·레이어 구조는 미확보 구간에 있어 확인 불가).
- 출발점: 마스크 인코더(masked encoder) 아키텍처. 저자들은 이것이 사전학습 시계열 예측 모델을 확장(scale up)하는 데 강력한 후보 아키텍처임이 이전 연구(Woo et al., 2023)에서 보여졌다고 인용하며, 이를 토대로 새로운 변형을 도입한다고 밝힌다.
- 세 가지 문제에 대응하는 세 가지 제안(각각의 세부 메커니즘은 이 문서에서 개요 수준으로만 언급됨):
  1. **다중 입출력 투영층(multiple input/output projection layers)**: 빈도별로 서로 다른 패치 기반 투영(patch-based projection)을 학습하여 빈도별 패턴 차이를 흡수한다. 고빈도 데이터에는 더 큰 패치 크기를, 저빈도 데이터에는 더 작은 패치 크기를 사용하는 방식으로 투영층을 해당 빈도에 특화시킨다.
  2. **Any-variate Attention**: 시간 축과 변량 축을 동시에 하나의 시퀀스로 취급하는 어텐션 메커니즘을 제안. Rotary Position Embeddings(RoPE, Su et al., 2024)로 시간 축을, 학습된 이진 어텐션 바이어스(learned binary attention biases, Yang et al., 2022b)로 변량 축을 인코딩한다. 이를 통해 모델이 임의 개수의 변량을 입력으로 받을 수 있게 된다.
  3. **혼합 파라메트릭 분포(mixture of parametric distributions)**: 유연한 예측 분포를 확보하기 위해 여러 파라메트릭 분포의 혼합을 출력 분포로 사용한다. 저자들은 유연한 분포의 음의 로그우도(negative log-likelihood)를 최적화하는 것이 목표 지표(target metric) 최적화와도 경쟁력을 가진다는 선행연구(Awasthi et al., 2022)를 근거로, 이 방식이 사후에 어떤 목표 지표로든 평가될 수 있는 사전학습에 유리한 특성이라고 주장한다.
- 모델은 세 가지 크기로 학습되었다: MoiraiSmall(14M 파라미터), MoiraiBase(91M), MoiraiLarge(311M).
- 학습 시 컨텍스트 길이와 예측 길이를 무작위로 샘플링하여, 사전학습된 모델을 다운스트림에서 유연하게 사용할 수 있도록 한다(즉 고정된 컨텍스트/예측 길이에 종속되지 않음).
- (마스크 인코더의 구체적 마스킹 방식, 어텐션 레이어 수·차원 등 세부 아키텍처는 미확보 구간—Appendix B 등—에 있을 것으로 보이며 이 문서에는 없다.)

## 사전학습 데이터/코퍼스
- **LOTSA (Large-scale Open Time Series Archive)**: "가장 큰 오픈 시계열 데이터셋 모음"으로, **9개 도메인에 걸쳐 270억(27B) 개 이상의 관측치(observations)**를 포함한다고 서론과 Table 1에서 반복谁으로 명시된다("over 27B observations across nine domains").
- Table 1(사전학습 모델 비교표)에서 Moirai의 "Pre-training Data (Size)" 항목은 "LOTSA (>27B)"로 표기되어 있다. 비교 대상들의 규모:
  - TimeGPT-1: Unknown (100B)
  - ForecastPFN: Synthetic Data (60M)
  - Lag-Llama: Monash (<1B)
  - TimesFM: Wiki + Trends + Others (>100B)
  - TTM: Monash (<1B)
  - LLMTime: Web-scale Text (크기 미표기)
- **주의**: 이 문서에는 LOTSA를 구성하는 9개 도메인의 명칭, 도메인별 데이터셋 개수, 도메인별 관측치 수를 표로 제시하는 부분(원 논문의 Section 3 데이터 관련 부분 또는 Appendix에 있을 것으로 추정)이 포함되어 있지 않다. 따라서 **금융(Econ/Fin) 도메인 관련 구체적 수치는 이 문서에서 전혀 확인할 수 없다** — 원문 자체에 해당 내용이 없기 때문에 인용 불가.
- 3장 서두의 "Problem Formulation"에서는 N개 시계열로 구성된 데이터셋 D = {(Y^(i), Z^(i))}_{i=1}^N 를 정의하려는 수식이 등장하다가 문서가 끊긴다(Y가 관측 대상 시계열, Z가 아마도 공변량으로 추정되나 정의 문장이 완결되지 않아 확정할 수 없음).

## 핵심 실험 결과
이 문서에는 실험 섹션(4장) 자체가 포함되어 있지 않다. 서론에서 서술적으로만 다음이 언급된다:
- "in-distribution 및 out-of-distribution 설정 모두에서 실험적 평가를 수행했으며, Moirai가 최신 완전학습(full-shot) 베이스라인 대비 일관되게 경쟁력 있거나 더 우수한 성능을 달성함을 보였다"(원문: "we perform experimental evaluations on both in and out-of-distribution settings, and show that Moirai consistently achieves competitive or superior performance compared to state-of-the-art full-shot baselines").
- 구체적인 수치, 데이터셋별 지표(CRPS, MASE 등), 표/그래프는 이 문서에 전혀 없다.

## 저자가 스스로 밝힌 한계
이 문서에는 Limitations 절이나 그에 준하는 한계 논의가 포함되어 있지 않다(미확보 구간에 있을 가능성이 있음). 다만 서론에서 간접적으로 드러나는 스코프 한정 요소는 다음과 같다:
- Table 1에서 Moirai는 "Any-variate (Zero-shot)", "Probabilistic Forecasting", "Flexible Distribution" 세 항목 모두 체크(✓)되어 있어, 저자들이 스스로 이 세 가지를 자사 모델의 핵심 차별점으로 제시하고 있다는 점에서, 역으로 비교 대상 모델들(TimesFM, TTM 등)의 어떤 항목이 부족한지를 프레이밍하는 방식으로 자사 강점을 강조하고 있음을 확인할 수 있다. 그러나 이는 "한계 고백"이 아니라 비교표를 통한 강점 제시이다.

## 흥미롭거나 특기할 만한 점
- 모델명 "Moirai"는 그리스 신화의 운명의 여신들(모이라이, 영어로 흔히 "The Fates")에서 따온 것이라고 각주에서 직접 밝히고 있다("destiny"의 의인화라는 점에서 "미래를 예측한다"는 모델의 기능과 언어유희적으로 연결).
- Table 1은 경쟁 모델들을 세 가지 축(any-variate 제로샷 가능 여부, 확률적 예측 여부, 유연한 분포 여부)으로 정리하며, 데이터 규모만 보면 TimeGPT-1(100B)과 TimesFM(>100B)이 LOTSA(27B)보다 크다고 명시되어 있다 — 즉 저자들은 "가장 큰 데이터"라는 프레이밍보다는 "가장 큰 오픈(open) 데이터셋"이라는 프레이밍을 사용하고 있어("largest collection of open time series datasets"), 규모 경쟁이 아니라 개방성(open-source)과 아키텍처 설계의 정교함을 차별점으로 내세우는 전략이 엿보인다.
- Any-variate Attention에서 시간 축은 RoPE(상대적 위치 인코딩), 변량 축은 학습된 이진 어텐션 바이어스로 서로 다른 방식을 적용한다는 설계는, "시간"과 "변량"이라는 이질적인 두 축을 하나의 시퀀스에 녹이면서도 각각에 적합한 귀납적 편향(inductive bias)을 부여하려는 시도로 읽힌다.
- Related Work에서 "Reprogramming"이라는 최근 흐름(LLM을 시계열에 파인튜닝으로 재활용)을 별도 카테고리로 소개하며 Moirai의 접근(처음부터 시계열 전용으로 사전학습)과 대비시키고 있다는 점이 방법론적 포지셔닝을 이해하는 데 참고가 된다.
- 원문 확보 상태 자체가 이 요약의 신뢰도에 미치는 영향: 이 논문은 시계열 파운데이션 모델 중 가장 자주 인용되는 것 중 하나이며 아키텍처·데이터·실험 디테일이 핵심인데, 현재 확보된 원문은 딱 그 핵심 내용(3장 나머지, 4장, Appendix) 직전에서 끊겨 있다. 후속 작업에서는 반드시 나머지 구간(특히 LOTSA 도메인별 표, Any-variate Attention 수식, 확률적 헤드 수식, 실험 표, Limitations)을 재수집해야 온전한 정독이 가능하다.
