# Chronos: Learning the Language of Time Series — 독립 정독 요약

## 서지정보
- 제목: Chronos: Learning the Language of Time Series
- 식별자: arXiv 2403.07815
- 저자: Abdul Fatir Ansari, Lorenzo Stella, Caner Turkmen 외 (AWS AI Labs, Amazon Supply Chain Optimization Technologies, UC San Diego, University of Freiburg, Rutgers University, UC Berkeley, New York University 소속 공저)
- 코드/모델: https://github.com/amazon-science/chronos-forecasting
- (원문 수집 상태: Introduction~Conclusion, Acknowledgements, References 일부까지 확보. Appendix 전체(데이터셋 상세 목록 등)는 원문 파일에 없어 이번 요약에서 다루지 못함)

## 한 줄 요약
시계열 값을 스케일링·양자화를 통해 고정된 어휘(토큰)로 변환한 뒤, 기존 언어모델(T5 계열) 아키텍처를 구조 변경 없이 그대로 학습시켜, 별도의 시계열 전용 설계 없이도 강력한 zero-shot 확률적 예측을 달성하는 사전학습 프레임워크.

## 문제의식/동기
- 시계열 예측은 전통적으로 ARIMA/ETS 같은 로컬(개별 시계열별) 통계모델이 지배했으나, 최근 딥러닝 기반 글로벌 모델(DeepAR, TFT, PatchTST 등)로 이동. 그러나 대부분 "같은 데이터셋으로 학습·예측"하는 체제에 머물러 있고, 범용(general-purpose) 시계열 파운데이션 모델은 아직 부재.
- LLM의 zero-shot 능력에 자극받아, 기존 접근은 (1) LLM에 자연어로 직접 프롬프트(LLMTime, PromptCast) (2) LLM 파인튜닝(GPT4TS, Time-LLM) 두 갈래였으나, 각각 태스크별 프롬프트 엔지니어링/파인튜닝이 필요하거나 GPT-3, Llama2 같은 거대 모델의 연산비용에 의존한다는 한계가 있음.
- 저자들은 근본적 질문을 던짐: "다음 토큰을 예측하는 언어모델"과 "다음 값을 예측하는 시계열 모델" 사이에 근본적 차이가 있는가? 이 질문이 Chronos 개발의 출발점.
- 또한 저자들은 "범용 시계열 예측 모델 개발에는 모델링 프레임워크보다 공개 시계열 데이터의 (양·질 모두에서) 부족이 더 결정적인 문제"라고 명시적으로 지적함.

## 방법론
### 아키텍처
- 기존 언어모델 아키텍처(주로 T5, encoder-decoder)를 어떤 구조 변경도 없이 그대로 사용. 유일한 변경은 vocabulary size를 시계열 토큰 어휘 크기(|V_ts|)에 맞춰 조정(임베딩 레이어를 truncate/extend)하는 것뿐.
- decoder-only 모델(GPT-2)로도 실험하여 프레임워크가 encoder-decoder에 국한되지 않음을 보임.
- 시간/주파수 정보(day-of-week 등의 시간 특징)는 의도적으로 사용하지 않음 — "counter-intuitively, in Chronos, we ignore time and frequency information, treating the 'time series' simply as a sequence."

### 토큰화·양자화 방식
1. **스케일링(Scaling)**: 평균 스케일링(mean scaling) 채택. x̃_i = (x_i - m)/s 에서 m=0, s = (1/C)Σ|x_i| (히스토리 구간의 절댓값 평균). 평균 스케일링을 택한 이유는 0값을 보존한다는 특성(예: 상품 판매량 0, 야간 태양광 발전량 0 등 의미 있는 0값) 때문.
2. **양자화(Quantization)**: 실수 구간을 B개의 bin으로 나눔. bin 중심 c_1<...<c_B와 경계 b_i를 설정하여 양자화 함수 q와 역양자화 함수 d를 정의(식 1). bin 배치는 데이터 의존적(quantile binning) 또는 균일(uniform binning) 방식이 가능한데, 미지의 downstream 데이터셋 분포가 학습 분포와 크게 다를 수 있으므로 균일 binning을 채택.
   - 한계로 명시: 예측 범위가 [c_1, c_B]로 제한되어, 강한 추세(trend)를 가진 시계열을 모델링하는 것이 이론적으로 불가능함을 스스로 지적(5.7절에서 실증적으로 재확인).
3. 특수 토큰 PAD(패딩/결측치 대체), EOS(시퀀스 종료) 추가.
4. 학습 설정에서는 bin 구간 [c_1=-15, c_B=+15], vocabulary size |V_ts|=4096(특수토큰 포함, B=4094개 bin), context length 512, prediction length 64.

### 학습 목적함수
- 출력 분포로 V_ts 상의 categorical distribution 사용. 양자화된 정답 라벨과 예측 분포 간 cross-entropy를 최소화(식 2). 즉 "회귀를 분류로 수행(regression via classification)".
- 이 손실은 거리 인식(distance-aware)이 아님을 저자가 명시 — bin i가 bin i+1보다 i+2에 가깝다는 정보를 손실함수 자체는 반영하지 않으며, 모델이 학습 데이터의 bin 인덱스 분포로부터 인접 bin 간의 연관성을 스스로 학습하기를 기대함.
- Categorical output의 장점 두 가지를 저자가 직접 제시: (1) 아키텍처/목적함수 변경 없이 기존 언어모델링 라이브러리(HuggingFace transformers)를 그대로 활용 가능 (2) 출력 분포 구조에 제약이 없어 멀티모달 분포 등 임의의 분포를 학습 가능.
- 서수형(ordinal) 변수로 모델링하는 것이 더 적절할 수 있다는 점도 인정하며, 향후 연구 과제로 남김(label smoothing 등을 통한 위상 정보 주입 제안).

### 확률적 출력 생성 방법
- 학습된 categorical 분포로부터 토큰을 순차적으로(autoregressive) 샘플링하여 여러 개의 sample path(궤적)를 생성.
- 각 궤적의 토큰 ID를 역양자화 함수 d로 실수값으로 변환한 뒤, 역스케일링(평균 스케일링의 경우 scale s를 곱함)을 적용해 최종 예측값 산출.
- 여러 샘플 경로로부터 예측 분포(predictive distribution)를 구성 — WQL 계산 시 20개의 샘플 경로로 quantile 추정, MASE 계산에는 median(0.5-quantile) 예측 사용.

### 데이터 증강 기법
- **TSMixup**: 이미지 분류의 Mixup을 시계열로 확장. 서로 다른 학습 데이터셋에서 k~U{1,K}개의 시계열(길이 l~U{l_min,l_max})을 샘플링, 각각 스케일링 후 Dirichlet(α) 분포에서 뽑은 가중치로 convex combination(식 3)을 생성. 논문 설정에서 K=3이며, 원본 시계열이 확률 1/3로 증강에 포함되도록 설계.
- **KernelSynth**: Gaussian process 기반 합성 데이터 생성. Automatic Statistician(Duvenaud et al., 2013)에서 영감을 받아, 선형(추세)·RBF(국소 변동)·주기(계절성) 커널 등을 담은 kernel bank K에서 j~U{1,J}개 커널을 샘플링해 +/× 이항연산으로 무작위 결합, 결과 커널로 GP prior에서 시계열을 샘플링.
- 학습 시 TSMixup 증강과 KernelSynth 합성 데이터를 9:1 비율로 샘플링.

## 사전학습 데이터/코퍼스
- 전체 데이터 수집: "our dataset collection comprises 55 datasets from multiple sources, including the Monash Time Series Forecasting Repository (Godahewa et al., 2021), the M-competitions ... and public domain datasets from Kaggle."
- 도메인 구성 (원문 인용): "we collected a wide variety of publicly available datasets spanning various application domains including energy, transport, healthcare, retail, web, weather, finance, and with sampling frequencies ranging from 5 minutes up to yearly."
  - → **금융(finance) 데이터가 도메인 목록에 명시적으로 포함되어 있음**을 확인. 다만 원문 확보 부분(Appendix B 미포함)에는 각 도메인별 데이터셋 개수·비중에 대한 구체적 수치가 없어, finance 데이터가 전체 대비 얼마나 되는지는 이번 원문에서 확인 불가.
- 55개 데이터셋을 세 그룹으로 분류:
  1. Pretraining-only: 13개 데이터셋, 795,936개 시리즈 (사전학습 전용)
  2. Benchmark I: 15개 데이터셋, 97,272개 시리즈 (사전학습 + in-domain 평가)
  3. Benchmark II: 27개 데이터셋, 190,674개 시리즈 (zero-shot 평가 전용)
- 학습에 사용된 것은 총 28개 데이터셋(Pretraining-only 13 + Benchmark I 15), 약 890K개의 단변량(univariate) 시계열, 약 84B(840억) 개의 관측치(토큰) 규모.
- 학습 데이터 구성: 10M개의 TSMixup 증강 시계열 + 1M개의 KernelSynth 합성 시계열.
- T5 계열 4개 크기(Mini 20M, Small 46M, Base 200M, Large 710M) + GPT-2 base(90M) 학습. 8×A100(40GB) GPU, 200K step, AdamW(weight decay 0.01), 초기 학습률 0.001에서 선형 감쇠.

## 핵심 실험 결과
- **Benchmark I (in-domain, 15개 데이터셋)**: Chronos-T5 Base/Large가 로컬 통계모델(AutoETS, AutoARIMA), 태스크별 딥러닝 모델(PatchTST, DeepAR), 다른 사전학습 모델(Lag-Llama, Moirai-1.0-R) 모두를 능가하는 최고 성능(WQL, MASE 기준). 심지어 가장 작은 Chronos-T5(Mini, 20M)조차 Moirai-1.0-R의 최고 모델(Large, 311M)보다 우수 — Moirai가 더 큰 코퍼스로 학습했음에도.
- **Benchmark II (zero-shot, 27개 데이터셋)**: Chronos 모델은 학습 중 한 번도 보지 못한 데이터셋임에도 확률적 예측(WQL)에서 2~4위, 점예측(MASE)에서 Chronos-T5(Large)가 2위(강한 SCUM 앙상블까지 능가). Moirai-1.0-R, Lag-Llama, LLMTime, ForecastPFN, GPT4TS 모두를 능가. 단, Moirai-1.0-R은 Benchmark II의 다수 데이터셋을 이미 사전학습에 포함했을 가능성이 있어 비교가 완전히 공정하지 않을 수 있음을 저자들이 스스로 지적.
- **파인튜닝**: Chronos-T5(Small)을 Benchmark II 각 데이터셋에 대해(dataset-agnostic 방식으로) 저비용 파인튜닝(1000 step)한 결과, Benchmark II 전체에서 1위(가장 큰 zero-shot Chronos 모델들과 태스크별 최고 모델들을 모두 능가).
- **하이퍼파라미터 분석**:
  - 모델 크기가 커질수록 학습 손실 및 downstream 성능 모두 개선(더 큰 모델 탐색은 추론속도 문제로 하지 않음).
  - **LLM 사전학습 가중치(T5, C4로 사전학습) 초기화는 랜덤 초기화 대비 이점이 없거나 오히려 약간 열등** — "these results suggest that LLM initialization offers relatively little advantage in the context of time series forecasting, and instead random initialization may be the preferable choice."
  - TSMixup 증강은 in-domain 성능엔 큰 차이 없지만 zero-shot 성능을 개선.
  - 합성 데이터(KernelSynth) 비율은 약 10%에서 가장 일관된 성능 개선, 그 이상은 성능 저하 경향. 순수 합성 데이터만으로 학습한 모델도 절대 성능 면에서 상당히 양호하며 ForecastPFN을 능가.
  - 학습 스텝(최대 1M)이 늘수록 성능 개선 지속.
  - context length는 1024까지 늘리면 개선되나 그 이상은 정체/악화 — 단, 고빈도(≥15분) 데이터셋이 평가셋에 부족하다는 평가 한계 때문일 수 있다고 저자가 지적.
  - vocabulary size 증가 시 MASE는 개선되나 WQL은 처음엔 개선 후 특정 크기 이상에서 악화 — 이는 지표 특성(스케일 불변 vs 스케일 의존)에 기인한다고 해석.

## 저자가 스스로 밝힌 한계
1. **양자화 범위 제한**: bin 중심 범위가 [-15, +15]로 고정되어 있어, 원 시계열 값 범위는 [-15s, 15s](s=스케일)로 제한됨. 이론적으로 강한 trend를 가진 시계열은 표현이 불가능. 실제로 지수적(exponential) trend 예측에는 어려움을 보임(선형 trend는 정확히 예측).
2. **스케일-정밀도 트레이드오프(overflow/precision loss)**: s가 값 범위에 비해 매우 작으면(예: 희소한 spike 시계열) 관측치가 표현 가능 범위를 벗어남. 반대로 s가 분산에 비해 매우 크면(예: 큰 평균 + 작은 분산의 사인파) 토큰 간 간격(30s/(B-1))이 커져 정밀도 손실 발생. 임시방편으로 표준화(standardization) 등 대안적 정규화를 inference-time heuristic으로 제안하나 근본적 해결은 향후 과제로 남김.
3. **context가 짧으면 trend를 과소추정**하는 경향(Air Passengers 데이터 사례로 시연) — 충분히 긴 context가 필요.
4. **cross-entropy가 거리 비인식(non-distance-aware)** 이라는 점을 목적함수 설계상의 한계로 인정, ordinal 회귀 방식의 도입이나 label smoothing을 통한 위상 정보 주입을 향후 연구로 제안.
5. **추론 속도**: 더 큰 Chronos 모델의 추론 속도는 태스크별 딥러닝 모델보다 느림(로컬 통계모델과 비슷한 수준). 더 큰 모델 크기를 탐색하지 않은 이유로도 언급됨.
6. **평가 설계의 한계**: context length 실험에서 고빈도(≥15분) 데이터셋이 벤치마크에 충분치 않아 장기 context의 이점을 결론적으로 검증하지 못했다고 인정.
7. **범위 제약**: 단변량(univariate), 균일 간격(uniformly-spaced) 시계열 예측에만 집중했고, 외생변수(exogenous covariates), 다변량(multivariate) 예측, 불규칙 샘플링(irregularly-sampled) 시계열은 다루지 않음 — 이를 6.1절에서 향후 연구 방향으로 명시.
8. **데이터 부족 문제 자체를 한계로 인정**: "in contrast to NLP, high-quality public time series data remains limited. This poses a dilemma... selecting more datasets for training leaves fewer for zero-shot evaluation."

## 흥미롭거나 특기할 만한 점
- 논문 제목의 언어유희: "Chronos"는 시간(chronos)을 뜻하지만, Conclusion에서 저자들은 "Chronos... is, paradoxically, agnostic to time"이라고 표현 — 시간/주파수 특징을 의도적으로 배제하고 순수 시퀀스로만 다룸에도 시계열을 다루는 모델이라는 역설을 스스로 지적.
- **regression via classification** 프레임을 명시적으로 채택하고 이를 위한 이론적 근거(Torgo & Gama, 1997; Stewart et al., 2023)까지 인용하며, 강화학습 분야의 유사 연구(Farebrother et al., 2024, "Stop regressing")를 향후 연구 참고점으로 제시한 점이 흥미로움 — 시계열 예측을 분류 문제로 재정의하는 접근이 여러 분야에서 동시에 나타나는 흐름을 보여줌.
- LLM 사전학습 가중치가 시계열 예측에 도움이 되지 않는다는 실험 결과는 "LLM이 사전에 학습한 언어 지식이 시계열의 패턴 인식에 전이된다"는 일부 통념(LLMTime 등 LLM 직접 활용 접근의 암묵적 전제)에 반하는 발견으로, Chronos가 "언어모델 지식"이 아니라 "언어모델 아키텍처/학습 절차"만을 재활용하고 있음을 실증적으로 뒷받침.
- AR(p) 프로세스 실험에서, 프로세스가 복잡해질수록(AR(3), AR(4)) Chronos-T5(Base)가 정확한 차수로 피팅한 AR 모델과 대등한 성능을, AutoARIMA보다는 더 나은 성능을 보인다는 점 — 특정 시계열 구조에 대한 사전 지식 없이도 patterns을 "인식"하는 능력을 시사.
- Categorical 분포 기반 예측이 멀티모달(multimodal) 분포까지 자연스럽게 표현할 수 있음을 KDE 시각화로 보여준 점(Figure 15) — 파라메트릭 분포(Gaussian, Student-t)나 quantile regression 기반 모델은 이런 유연성을 갖기 어려움.
- 순수 합성 데이터(KernelSynth)만으로 학습한 모델이 실제 데이터를 전혀 보지 못했음에도 여러 베이스라인을 능가했다는 결과는, 합성 데이터의 질이 실제 데이터의 "대체재"로서 상당한 잠재력이 있음을 시사 — 시계열 데이터 부족 문제에 대한 실질적 해법 방향 제시.
- Fine-tuning 실험에서 Chronos-T5(Small)이 파인튜닝 후 zero-shot 상태의 대형 Chronos 모델들보다도 우수했다는 점은, 사전학습 규모보다 태스크별 적응이 더 큰 성능 이득을 줄 수 있음을 시사하며, 향후 더 큰 모델의 파인튜닝 잠재력에 대한 기대로 이어짐.
