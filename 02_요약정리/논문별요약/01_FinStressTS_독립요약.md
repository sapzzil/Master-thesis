# FinStressTS: A Parametric Synthetic Benchmark for Time-Series Forecasting in Finance — 독립 요약

## 서지정보
- 저자: Jiaze Sun, Kelvin J.L. Koa(교신저자), Ruiyang Ni, Yize Liu, Haonan Chen, Ke-Wei Huang (National University of Singapore / Asian Institute of Digital Finance, Nanyang Technological University)
- arXiv: 2606.03184v1 [q-fin.CP], 2026-06-02 제출, CC BY 4.0
- 게재: KDD'26 (32nd ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.2, 2026-08-09~13, Jeju Island)
- 코드: https://github.com/jiazeee/FinStressTS

## 한 줄 요약
실제 금융 시계열 데이터는 여러 확률적 메커니즘(변동성 군집, 두꺼운 꼬리, 레짐 전환, 자기흥분 점프 등)이 뒤엉켜 있어 모델이 왜 실패하는지 원인 규명이 불가능하다는 문제의식에서, 6개 메커니즘 계열 × 5단계 강도로 구성된 30개 진단 환경의 파라메트릭 합성 벤치마크(FinStressTS)를 제안하고, 15개 모델(고전 계량경제 모델부터 Transformer, 확률적 생성모델까지)을 점예측(NMAE)·확률예측(CRPS)·데이터효율성(learning curve) 세 축으로 평가한 논문.

## 문제의식 / 동기
- 저자들은 실데이터 벤치마크의 근본적 한계로 "귀속(attribution) 불가능성"을 지적한다: 모델이 실데이터에서 성능이 나쁠 때, 그것이 분포 오정합 때문인지, 레짐 변화 적응 실패 때문인지, 데이터 부족 때문인지 구분할 수 없다. 생성 메커니즘이 관측 불가능하게 뒤섞여 있기 때문.
- 또한 실데이터는 단 하나의 실현 경로(single realized path)만 제공하므로, 꼬리 위험 보정(tail-risk calibration)이나 통제된 조건에서의 데이터 효율성 평가가 불가능하다.
- M6 Financial Forecasting Competition 등 최근 대규모 평가에서 정교한 딥러닝 모델이 단순 휴리스틱을 자주 이기지 못한다는 관찰이 있었으나, 이것이 시장의 본질적 예측불가능성 때문인지 모델의 구조적 결함 때문인지 실데이터로는 판별할 수 없다는 "방법론적 역설"을 강조한다.
- 기존 대안들도 미흡: 범용 시계열 벤치마크(TFB, Monash 등)는 금융 특유의 위험 프로파일을 반영하지 못하고, 기존 합성 데이터셋(GRATIS, TSGM 등)은 대체로 가우시안 가정에 의존해 현대 아키텍처를 제대로 시험하지 못하며, FinTSB 같은 금융 특화 벤치마크도 결국 실데이터에 의존해 지속적 업데이트가 필요하고 메커니즘이 뒤섞여 있다는 문제는 그대로 남는다.
- 즉 "파라메트릭 통제"와 "금융적 사실성"을 동시에 갖춘 중간지대(middle ground)가 없다는 것이 이 논문의 출발점.

## 방법론

### 설계 원칙 (4가지)
1. 계량경제학적 충실성(Econometric fidelity): 6개 메커니즘 모두 확립된 계량경제 이론(GARCH, HAR, Hawkes, Markov-switching 등)에 근거.
2. 진단적 통제(Diagnostic control): 파라미터(점프 강도, 레짐 전환 빈도 등)를 명시적으로 조절해 실패 임계점을 규명 가능하게 함.
3. 검증 가능한 정답(Verifiable ground truth): 생성과정을 완전히 알고 있으므로 진짜 조건부 분포 P(y_{t+1}|H_t)에 접근 가능 — 실데이터로는 불가능한 확률 보정 평가를 가능케 함.
4. 다변량 패널 구조: 공통 잠재요인(factor), 레짐, 시장 전반 점프 등을 통해 계열 간 공행성(co-movement)을 유도(임의의 공분산행렬이 아니라 해석 가능한 구조로).

### 6개 메커니즘 계열 (각 5단계 진단레벨, 총 30개 환경)
1. **변동성 군집(Volatility clustering)**: 계통적 요인과 개별 잔차 모두 GARCH(1,1) 조건부 분산 동학을 따름. 통제 파라미터: 지속성(ρ=α+β), 이질성, 신호대잡음비(SNR).
2. **다중스케일 변동성 지속성(HAR-type)**: 일/주/월 스케일 지연 제곱 충격의 가중합으로 조건부 분산을 모델링(Corsi HAR 구조). 통제: 총 피드백 강도 s, 장기기억 비중 λ.
3. **두꺼운 꼬리/이상치**: GARCH 동학 위에 표준화된 Student-t 충격(자유도 ν)을 적용하고, 확률 π_out으로 추가적 이상치(outlier)를 독립적으로 주입. GARCH 재귀 자체는 base 성분에만 의존(이상치는 일시적 분포 이탈).
4. **레짐 전환(구조적 단절)**: 시장 전체 레짐 s_t∈{Up, Stable, Down}이 블록 길이 B 단위로 마르코프 체인을 따라 전환. 레짐별 평균/분산이 다르고, φ가 레짐 내 지속성을 통제. 기업별 노출계수(a_i, b_i)는 로그정규분포에서 추출.
5. **자기흥분 점프(Hawkes-type)**: 이산시간 Hawkes 강도 재귀 λ_t = μ + δ(λ_{t-1}-μ) + αN_{t-1}로 이벤트 클러스터링을 모델링. 안정성 조건 α < 1-exp(-β). 시장 전체 복합점프 J_t가 기업별 노출 γ_i를 통해 모든 계열에 영향.
6. **영과잉 희소 점프(Zero-inflated)**: 점프 카운트 N_t가 영과잉 포아송(ZIP(π,λ)) 분포를 따름(자기흥분 없음). 비유동자산/거래단위 데이터 특성을 모사.

### 실험 설계
- 각 메커니즘마다 N=50개 계열, T_total=2,000 스텝의 패널을 생성. 시간순 분할(train 60% / val 20% / test 20%), 표준화는 훈련구간 통계만 사용.
- 롤링 1스텝 예측(H=1), lookback window L=96, 파라미터는 학습 후 고정(온라인 업데이트 없음).
- 점예측 15개 모델 중 11개 평가: Naive, AR(1), HAR, VAR, DLinear, PatchTST, iTransformer, Autoformer, FEDformer, Nonstationary Transformer, TimeXer.
- 확률예측 6개 모델: DeepAR, TimeGrad, TSFlow, TimeMCL, RATD, QuantileFormer.
- 점예측 지표: NMAE_σ (변동성으로 정규화된 MAE, 식(3)).
- 확률예측 지표: CRPS(식4~5, 표본기반 추정), 다변량은 횡단면 합(cross-sectional sum) 기준 CRPS_sum을 |y_sum| 평균으로 정규화(식6).
- 데이터효율성: 훈련샘플 크기 n∈{100,200,300,400,600,800,1000,1200}으로 학습곡선(learning curve) 구성, 테스트셋은 고정.
- Monte Carlo 샘플 S=100.

## 핵심 결과 (구체적 수치)

### 점예측 (Table 2, NMAE_σ)
- 모든 케이스에서 Naive가 가장 나쁨(예: Case1 L1 1.1267). AR(1)/HAR/DLinear가 거의 항상 최상위권을 차지하고, Transformer 계열(특히 Autoformer, FEDformer)이 일관되게 열등. 예: Case1 L1에서 AR(1) 0.7970, HAR 0.7989, DLinear 0.7980 vs Autoformer 0.8629, FEDformer 0.8472.
- Finding 1 (Robustness trumps expressiveness): 단순 AR/HAR/DLinear가 Transformer를 일관되게 능가. 저자들은 저신호대잡음 환경(Case1-3)에서는 견고한 평균회귀가 핵심이지, 복잡한 패턴 매칭이 아니라고 해석. Nonstationary Transformer 같은 고용량 모델은 특이성 노이즈에 과적합.
- Finding 2 (Local attention > global mixing): Attention 기반 모델 중에서는 PatchTST가 대체로 최상위. 지역(local) 패치 구조가 전역 교차계열 혼합 없이 지역적 시간 구조를 보존하는 반면, iTransformer/TimeXer 같은 전역 상관 모델은 점프 주도 환경(Case5-6)에서 부진 — 전역 attention이 국소 충격 신호를 희석시킨다는 해석.
- Finding 3 (Decomposition fails without periodicity): Autoformer/FEDformer(계절-추세 분해, 주파수영역)는 거의 모든 환경에서 지속적으로 열등. 금융 수익률은 교통/에너지/날씨 데이터와 달리 주기적 구조가 약하고 확률적 변동성·레짐변화·두꺼운 꼬리가 지배적이기 때문에, 주기성 추출용 귀납편향이 오히려 방해가 됨.

### 확률예측 (Table 3, CRPS)
- Finding 4 (Parametric alignment yields efficiency): DeepAR이 30개 설정 중 24개에서 최고 CRPS 달성. 저자는 DeepAR의 시변 스케일(σ_t)을 갖는 자기회귀 가우시안 우도가 Case1/2를 생성하는 GARCH 동학과 "구조적으로 동형(isomorphic)"이기 때문이라고 설명 — 올바른(단순해도) 파라메트릭 명세가 정지 레짐에서는 유연하지만 데이터 소모적인 밀도추정기보다 낫다는 결론.
- Finding 5 (Flexibility wins under multimodality): DeepAR의 한계는 Case4(레짐전환)와 Case6(영과잉 점프)에서 드러남 — 진짜 사후분포가 다중모드이거나 영과잉일 때 TSFlow(정규화 흐름 기반)가 DeepAR을 능가(예: Case4 L1). 예: Case4 L1에서 DeepAR 0.6840, TimeGrad 0.6039, TSFlow 0.8521, TimeMCL 1.9729, RATD 0.9902.
- Finding 6 (Diffusion models struggle with structural breaks): RATD는 매끄러운 변동성 과정에서는 성능이 좋지만 불연속적 메커니즘(Case4, 6)에서 저하 — 확산모델의 잔차가 노이즈 분포가 순간적으로 바뀌는 구조적 단절에 적응하기 어렵다는 해석. (예: Case4 L2 RATD 2.2090, Case6 L4 RATD 2.3690로 매우 높음(나쁨).)

### 데이터 효율성 (Figure 2, 3 기반 서술)
- "조기 포화(Early Saturation)" 효과: 변동성(Case1)·꼬리(Case3) 메커니즘에서는 성능이 훈련데이터의 약 40% 지점에서 빠르게 포화되고 이후 정체 — 1스텝 금융예측의 "신호"가 정보희박(information-sparse)하다는 뜻으로, 데이터를 늘려도 노이즈만 더 샘플링하는 셈.
- 유일한 예외는 Case4(레짐전환)로, 대규모 샘플에서도 학습곡선이 가파르게 유지됨 — 잠재적 구조변화 추론은 정보밀도가 높은(information-dense) 과제.
- 확률예측 데이터효율성: DeepAR은 정지 설정(Case1-3)에서 매우 소량의 샘플로도 안정화(data-efficient). TSFlow/TimeMCL 같은 유연한 생성모델은 데이터량이 늘수록 뚜렷이 개선되며, 경쟁력 있는 보정에 도달하려면 대략 2~3배 더 많은 데이터가 필요.

## 저자가 밝힌 한계 (Section 6, 원문 그대로 반영)
1. FinStressTS는 전체 시장 시뮬레이터가 아니라 진단 벤치마크임 — 지정가 주문서(limit order book) 등 실제 시장의 많은 복잡성을 모델링하지 않음. 따라서 여기서의 강한 성능이 곧 거래 수익성을 보증하지 않으며, 실데이터 평가를 대체하는 것이 아니라 보완하는 것으로 봐야 함.
2. 6개 메커니즘 계열은 각각 정형화된 계량경제 공식으로 구현되어 근거는 있지만 총망라적이지 않음 — 확률변동성(stochastic volatility) 등 대안적 DGP나 파라미터 구성이 다른 학습 동학을 유발하고 상대적 순위를 바꿀 수 있음. 메커니즘 계열별 다중 변형을 추가하는 것이 향후 과제.
3. 현재 벤치마크는 고정 호라이즌 예측에 초점을 두며 (i) 다단계(multi-step) 예측, (ii) 비정상성 하 온라인 적응, (iii) 포트폴리오 배분 등 의사결정 인지형(decision-aware) 평가를 아직 다루지 않음. 복합 스트레스(예: 레짐전환+두꺼운꼬리+점프 동시발생) 상호작용 확장도 향후 과제.
4. 15개 모델을 평가했지만 시계열 방법론은 계속 진화하므로 지속적 벤치마크 갱신이 필요. 학습곡선·분포 지표 계산은 추가 연산비용을 요구해 매우 큰 모델에서는 진단 세밀도가 제한될 수 있음.

## 흥미롭거나 특기할 만한 점 (직접 읽으며 느낀 것)
- 이 논문의 가장 강한 주장은 "복잡성(capacity)이 아니라 귀납편향(inductive bias)의 정합성이 성능을 결정한다"는 것인데, 이를 뒷받침하는 근거로 HAR을 원래 실현변동성(realized volatility) 모델링용으로 제안된 모델임에도 여기서는 평균(mean) 예측용 선형 다중스케일 자기회귀 베이스라인으로 "용도 변경"해서 쓴 점이 눈에 띈다(Table 2 각주에 명시). 이는 방법론적으로 다소 인위적일 수 있어 결과 해석 시 유의할 부분.
- DeepAR이 30개 설정 중 24개에서 최고 CRPS를 기록했다는 것은 상당히 인상적인 결과이며, "정확한 파라메트릭 가정이 유연한 비모수적 모델보다 데이터가 제한된 환경에서 우월하다"는 이 논문의 핵심 메시지를 매우 직접적으로 뒷받침한다. 다만 이것이 DeepAR의 가우시안-시변분산 구조가 GARCH 생성과정과 "동형(isomorphic)"이기 때문이라는 저자의 설명은, 뒤집어 말하면 이 벤치마크가 GARCH류 DGP를 다수 포함하도록 설계되어 있어 GARCH와 구조적으로 유사한 모델(DeepAR)에게 유리하게 편향되어 있을 가능성을 시사한다 — 저자들도 이를 명시적으로 "한계"로 인정하지는 않았지만, 다른 DGP(예: 확률변동성)를 시도하면 결과가 달라질 수 있다는 한계 2번 서술과 맞닿아 있다.
- Case5(자기흥분 점프)와 Case6(영과잉 점프)에서 여러 확률모델의 CRPS가 1.0을 넘거나 심지어 2.0 이상으로 치솟는 경우(RATD가 Case4 L2에서 2.2090, Case6 L4에서 2.3690)가 나타나는데, 이는 상당히 심각한 미보정(miscalibration)이며, "딥러닝 확률모델이 구조적 단절/희소 이벤트에서 체계적으로 실패한다"는 결론에 힘을 싣는 구체적 사례로 보인다.
- Table 3의 각주에서 저자들 스스로 원문 HTML 추출 과정의 셀 정렬 이슈를 언급하지는 않았지만(이는 이 요약 작성자가 원문 md 파일 수집 시점에 표기한 주석), 원 논문의 표 자체는 병합 셀이 많아 나나 다른 독자가 참고할 때 PDF 원문 대조가 필요할 수 있다는 점은 유의할 실무적 포인트.
- Appendix A의 수식들은 상당히 꼼꼼하게 각 메커니즘의 파라미터화(예: HAR을 s, λ 두 개의 해석가능한 파라미터로 재매개변수화하는 방식, Hawkes의 분기비율(branching ratio) br_disc)를 설명하고 있어, 재현성 측면에서는 우수해 보인다. 다만 Appendix A.6(Case 6)의 서술이 원문 수집 과정에서 문장 중간에 끊긴 것으로 보이며, 이 부분은 본 요약자가 확인한 원문 md 파일 자체의 한계(웹 fetch 범위 문제)로 보인다 — 필요시 원문 PDF 재확인이 필요.
