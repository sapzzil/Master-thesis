# Frequency Matters: When Time Series Foundation Models Fail Under Spectral Shift — 독립 요약

## 서지정보
- 제목: Frequency Matters: When Time Series Foundation Models Fail Under Spectral Shift
- arXiv ID: 2511.05619
- 저자: Tianze Wang, Sofiane Ennadir, John Pertoft, Gabriela Zarzar Gandler, Lele Cao, Zineb Senane, Styliani Katsarou, Sahar Asadi, Axel Karlsson, Oleg Smirnov (소속: King AI Labs, Microsoft Gaming)
- 자료 형태: 본문 + 부록 A~F 전체(관련연구, 스펙트럼 분석, 데이터 생성, 분류 추가결과, 실험 세부사항, 고찰)

## 한 줄 요약
모바일 게임(Candy Crush Saga) 플레이어 참여도 예측이라는 산업 규모 과제에서 시계열 파운데이션 모델(TSFM, MOMENT)이 XGBoost/TabNet/PatchTST 같은 도메인 특화·전통 모델보다 뚜렷이 뒤처짐을 보이고, 그 핵심 원인을 "스펙트럼 이동(spectral shift)" — 사전학습 데이터와 다운스트림 데이터의 지배적 주파수 대역 불일치 — 으로 지목한 뒤, 통제된 합성 실험(사전학습에 존재한 "seen" 주파수 대역 vs. 존재하지 않은 "unseen" 대역)으로 이 가설을 검증한 논문.

## 문제의식/동기
- TSFM(파운데이션 모델)이 공개 벤치마크에서는 강한 성능을 보이며 시계열의 "BERT 모먼트"라는 기대를 받았지만, 산업 현장(특히 게임 텔레메트리처럼 불규칙·다중 스케일 리듬을 가진 도메인)에서 실제로 효과적인지는 불확실하다는 문제 제기.
- 핵심 질문: "왜 공개 벤치마크에서 뛰어난 TSFM이 실제 게임 애플리케이션에서는 성능이 떨어지는가?"
- 저자들의 가설: TSFM은 사전학습 중 기억한 주파수 성분에 의존하며, 다운스트림 데이터의 지배적 대역이 이 스펙트럼 밖에 있으면 일반화 성능이 저하된다. 이는 텍스트 기반 LLM과 달리, 시계열 데이터가 도메인 간 언어적/의미적 공통 구조를 공유하지 않고 표본율(sampling rate), 해상도, 시간적 역학(주기성, 비정상성 등)에 매우 민감하기 때문이라고 설명한다.

## 방법론

### (1) 산업 사례 데이터 — Player Engagement Prediction (PEP)
- 데이터: King의 Candy Crush Saga(모바일 match-3 게임)에서 추출한 다변량 시계열(MTS).
- 입력: 플레이어 1명당 최대 512 라운드(타임스텝), 최대 30일 lookback window, 32개 단변량 피처(진행도, 게임플레이, 자원, 전략, 컨텍스트 카테고리로 구성). 결측치는 명시적으로 인코딩.
- 예측 대상 라벨 2종: (1) 30일 이내 구매 여부(이진분류), (2) Engagement Score(연속 회귀 — 플레이 시간 등 행동 강도, 정규화됨).
- 데이터 규모: 226일간 824,208개 MTS 샘플, 약 40,000명 플레이어. player-holdout 검증/테스트 178,279/176,632개. temporal-holdout(주요 기간 종료 약 2개월 후 28일)은 약 7,000명·34,279 샘플, zero-shot 평가.
- 평가 프로토콜: player-holdout(플레이어 단위로 분리, 시간분리 없음) + temporal-holdout(과거로 학습, 미래에 zero-shot 평가).
- 비교 모델: XGBoost, TabNet(정형 피처 기반 산업 베이스라인), PatchTST(태스크 파인튜닝된 강한 모델), MOMENT-small(대표 오픈 TSFM, 선형 프로빙으로 경량 헤드만 학습).
- 평가지표: 분류는 Accuracy/AUC, 회귀는 MSE/MAE.

### (2) 스펙트럼 분석 (부록 B)
- MOMENT의 사전학습에 포함된 FordA, FaultDetectionA(UCR) 데이터셋과 자사 게임 데이터셋의 지배적 주파수를 비교, 두 데이터셋 간 지배 주파수가 근본적으로 다름을 시각적으로 확인(Figure 2).

### (3) 합성 실험 설계 (본문 3.1절 + 부록 C)
1. 주파수 추출: 사전학습에 쓰인 실제 시계열 x(t)에 대해 FFT를 적용, 상위 5개 지배 주파수(및 진폭)를 추출하여 [f_low, f_high] 대역을 정의.
2. 신호 생성:
   - Seen 대역: [f_low, f_high] 범위 내에서 균일 샘플링한 주파수들의 사인파 합 + 무작위 위상 + 약한 가산성 노이즈.
   - Unseen 대역: [f_low+δ, f_high+δ] (δ는 두 구간이 겹치지 않고 원 신호의 전체 주파수 범위 내에 머물도록 랜덤 결정).
3. 라벨링: 회귀 타깃은 사용된 주파수 합의 z-score 정규화 값(식 3, 4). 분류 라벨은 seen/unseen 여부(부록 D에서는 인접 주파수 구간, 예 [0,10] vs [10,20]Hz의 중앙값 기준 이진 분류).
4. 평가: 사전학습된 MOMENT 백본을 동결(freeze)하고 경량 회귀/분류 헤드만 학습(linear probing).
- 기반 데이터셋: FordA, FordB, FaultDetectionA, FaultDetectionB(센서), SmallKitchenAppliances, ElectricDevices(전력 소비), 분류 추가실험에는 ECG5000, SwedishLeaf도 포함 — 모두 MOMENT 사전학습에 쓰인 데이터셋 계열.
- 학습: Adam optimizer, 분류는 BCE, 회귀는 MSE, 50 epoch, lr=1e-3. 각 실험 3회 반복 후 평균±표준편차 보고.
- 하드웨어: CPU, NVIDIA GPU(L4 24GB, T4 16GB), Apple M1 MAX(MPS 32GB); MOMENT 대규모 학습은 최대 8-GPU 분산 데이터병렬.

## 핵심 결과
- 산업 벤치마크(Table 1): PatchTST가 전반적으로 최고 성능(player-holdout Accuracy 0.939/AUC 0.982, temporal-holdout Accuracy 0.921/AUC 0.975). XGBoost, TabNet도 MOMENT보다 우수. MOMENT-small은 모든 지표에서 최하위(예: player-holdout Accuracy 0.758/AUC 0.791, MSE 2.250; temporal-holdout Accuracy 0.701/AUC 0.749, MSE 2.854) — 즉 공개벤치마크 성공을 거둔 TSFM이 산업 현장에서는 도메인 적응 모델·전통 트리 모델에도 못 미침.
- 합성 회귀 실험(Table 2): 6개 데이터셋 전부에서 seen 대역 MSE/MAE가 unseen 대역보다 일관되게 낮음(예: ElectricDevices MSE 0.644±0.002(seen) vs 0.952±0.003(unseen); FaultDetectionA 0.689 vs 0.942 등). 모델(백본)은 동결된 채 헤드만 학습했으므로, 이는 순수하게 인코더가 추출한 표현의 질 차이를 반영.
- 합성 분류 실험(Table 3, 부록 D): 대체로 seen 대역에서 정확도/AUC가 더 높은 경향(예: ElectricDevices Accuracy 0.785 vs 0.650, AUC 0.890 vs 0.716; FaultDetectionA Accuracy 0.766 vs 0.651; ECG5000 0.809 vs 0.591; SwedishLeaf 0.689 vs 0.600). 단, FordA/FordB/SmallKitchenAppliances/FaultDetectionB는 seen과 unseen 차이가 작거나 오히려 unseen이 근소하게 높은 경우도 존재(예: FordB Accuracy 0.826 vs 0.838, SmallKitchenAppliances 0.708 vs 0.756) — 저자는 이를 특별히 언급하지 않고 "전반적 경향이 재확인됐다"고만 서술함.
- 결론적으로 저자들은 이 결과들이 스펙트럼 불일치(spectral mismatch) 가설을 뒷받침한다고 주장하며, TSFM이 "일반화 가능한 시간적 표현"을 진정으로 학습했다기보다 특정 주파수 대역과 결부된 패턴을 암기했을 가능성을 제기.

## 저자가 스스로 밝힌 한계 (Limitations, 3.3절 원문 인용)
> "Our evidence is drawn from one industrial domain (mobile gaming) and a single TSFM configuration, and we are conducting broader validations at the moment."

> "The synthetic probes also simplify real-world dynamics, relying on sinusoidal signals that do not fully capture irregular sampling, burstiness, or regime shifts."

즉 (1) 산업 근거가 게임이라는 단일 도메인, 단일 TSFM(MOMENT-small) 구성에만 의존하며 더 폭넓은 검증은 진행 중이라는 점, (2) 합성 프로브가 사인파 기반이라 불규칙 샘플링, 버스트성(burstiness), 레짐 변화 등 실세계 역학을 완전히 포착하지 못한다는 점을 명시적으로 인정. 이런 제약에도 불구하고 일관된 경향이 있으므로 실무적 시사점(스펙트럼 겹침 평가, 주파수 인지 증강/경량 적응, 스펙트럼 강건성 벤치마크 채택)을 제시한다고 서술.

## "finance" 단어의 등장 여부 및 맥락
원문에 "finance"라는 단어가 등장하지만, 이 논문 자신의 실험 도메인으로서가 아니라 **일반적 시계열 응용 도메인 나열** 및 **관련 연구(다른 TSFM들) 소개**의 맥락에서만 나타난다.
1. Introduction 1문단: "Time series data are pervasive across various domains, including finance, healthcare, energy, and gaming." — 시계열이 쓰이는 도메인 예시 중 하나로 나열.
2. Introduction 3문단: "sampling rates, periodicities, and nonstationarities differ significantly between, e.g., electricity, healthcare, finance, and gaming." — 도메인 간 이질성 예시로 다시 나열.
3. 부록 A(관련연구), Moirai 소개: "making it effective not only for forecasting but also for classification and imputation tasks across domains such as healthcare and finance." — Moirai라는 타 논문의 적용 도메인 언급.
4. 부록 A, TimesFM 소개: "it demonstrates strong zero-shot performance across diverse application domains, including finance, energy, and traffic." — TimesFM의 적용 도메인 언급.

즉, 이 논문 자체의 실험(PEP 산업 사례, 합성 실험)에는 금융 데이터가 전혀 사용되지 않았고, "finance"는 오직 배경 설명·타 모델 소개 문맥에서만 등장한다. 본 논문의 결론(스펙트럼 이동 가설)을 금융 도메인에 직접 적용한 근거는 원문에 없음.

## 흥미롭거나 특기할 만한 점
- 저자 소속이 King(모바일 게임사) AI Labs와 Microsoft Gaming으로, 순수 학계가 아닌 산업 현장(게임 텔레메트리) 데이터를 직접 활용한 실증 논문. 실제 서비스 데이터(플레이어 82만+ 샘플)를 사용했다는 점에서 설득력 있는 산업적 근거 제시.
- "BERT moment"라는 표현으로 TSFM에 대한 업계의 과도한 기대를 언급하며 이를 비판적으로 검증하는 논조.
- 회귀 라벨 설계가 흥미로움: 사용된 주파수의 합을 z-score 정규화하여 라벨로 삼음으로써, 모델이 "주파수 자체의 스케일"을 이용해 쉽게 맞추는 것을 방지하고 순수하게 시간적 표현(temporal representation)의 질을 평가하려는 의도가 명시됨(부록 C, 식 3~4).
- 분류 실험(Table 3)에서 일부 데이터셋(FordB, SmallKitchenAppliances)은 unseen이 오히려 seen보다 근소하게 높은 성능을 보였는데도, 본문에서는 "similar trends are observed, further validating our hypothesis"라고만 서술하며 이 예외를 구체적으로 논하지 않음 — 가설에 부합하지 않는 부분에 대한 논의가 다소 약한 지점으로 보임.
- FaultDetectionB는 분류 정확도가 seen 0.444, unseen 0.472로 랜덤 수준(0.5)에도 못 미치고 표준편차(AUC ±0.306, ±0.190)가 극단적으로 커서, 이 데이터셋에서는 결과의 신뢰도 자체가 낮아 보이나 본문에서 별도로 언급되지 않음.
- 부록 F에서 향후 방향으로 "사전학습에 지배 주파수 대역을 예측하는 보조 과제(auxiliary task) 추가" 또는 "주파수 기반 데이터 증강/샘플링으로 커버리지 확장"을 제안 — 구체적 방법론 제시라기보다 가설적 제언 수준.
- 실험은 전부 "linear probing"(백본 동결)만 수행했고, 파인튜닝(fine-tuning) 시 스펙트럼 이동 문제가 완화되는지는 다루지 않음 — 이는 한계로 명시되지는 않았지만 방법론적으로 스코프가 제한된 지점.
