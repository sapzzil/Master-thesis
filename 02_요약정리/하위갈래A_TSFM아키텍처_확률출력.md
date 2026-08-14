# 하위갈래 A — TSFM 아키텍처와 확률 출력 방식

> 작성일: 2026-08-12 (2단계 자료조사, 진행상황.md의 "남은 위험 1건" 확인 작업)
> 목적: TimesFM·Chronos·Moirai 계열·TTM·Lag-Llama·Toto·Sundial이 각각 어떤 형태로
> 확률적 예측을 출력하는지 원문 대조로 확정하고, CRPS 계산 전제를 모델별로 정리.
> **원칙**: 원문에서 직접 확인한 내용만 기재. 확인 못 한 부분은 "확인 불가"로 명시.

## 검증 방법
- arXiv HTML판(`arxiv.org/html/...`)을 직접 fetch하여 원문 문장을 대조.
- 다음 모델은 원문 HTML을 직접 읽고 확인: **TimesFM(1.0), Chronos, Moirai(1.0), Moirai-MoE,
  Moirai 2.0, Chronos-2, TTM, Lag-Llama, Toto**.
- **Sundial**은 원문 HTML을 일부만(서론~예비지식) 확인. Fetch 응답이 도구 제한으로 잘려
  TimeFlow Loss의 정의·추론 방식은 확인했으나, 학습 데이터(TimeBench) 구성에 금융 도메인이
  포함되는지는 **확인하지 못함**.
- **TimesFM 2.5의 quantile head**와 **Chronos-Bolt**는 원 저자 그룹이 arXiv 논문을 별도로
  내지 않고 GitHub/HuggingFace 모델 카드·블로그로만 공개한 것으로 확인됨(웹서치로 다수 소스
  교차 확인, 그러나 arXiv 원문 형태의 1차 자료는 아님 — 아래 표에 출처 구분 명시).

---

## 모델별 표

| 모델 | arXiv ID (원 논문) | 확률적 출력 형태 | CRPS 계산 전제 | 금융데이터 포함여부 | 원문 근거 |
|---|---|---|---|---|---|
| **TimesFM (1.0)** | 2310.10688 (ICML 2024) | **점 예측(point forecast)만.** 확률적 출력은 본 논문의 범위 밖 | 해당 없음(점 예측 → CRPS 계산 불가, MSE/MAE만 가능) | 확인 불가(코퍼스 도메인 상세 미기재) | "*Probabilistic Forecasting.* It should be straightforward to train with probabilistic loss functions in our framework... **this was not our main focus and is left to future explorations.**" (원문 결론부 Future Work) — 분위수 헤드는 "쉽게 추가할 수 있다"는 제안 수준으로만 언급, 실제 학습·평가 안 함 |
| **TimesFM 2.5** | 원 논문은 1.0과 동일(2310.10688); 2.5 자체의 별도 arXiv 논문 **확인 불가** | 옵션형 **연속 분위수 헤드**(약 30M 파라미터 추가 모듈) — `use_continuous_quantile_head=True` 시 P10~P90 등 10개 분위수 출력 | 분위수 기반 → pinball loss 평균으로 CRPS 근사 가능 | 확인 불가 | 1차 자료(arXiv) 아님. GitHub `google-research/timesfm` 리포·HuggingFace 모델카드·MarkTechPost 등 2차 소스로만 확인(2026-08 기준). **원문 논문 부재로 표에는 참고용으로만 기재, 인용 시 주의 필요** |
| **Chronos** | 2403.07815 (TMLR 2024) | **샘플 경로(sample paths)**. 값을 스케일링·양자화해 토큰화 → 범주형 분포에서 자기회귀적으로 토큰을 샘플링 → 다중 궤적(trajectory) 생성 | 샘플 기반 → **경험적(empirical) CRPS**: 샘플들의 경험분포로 CRPS 추정, 혹은 샘플에서 분위수 추출 후 pinball loss 평균 | 확인됨(사전학습 코퍼스 도메인 나열에 "finance" 명시). 단, 비중은 미기재 | "CHRONOS models are probabilistic by design and multiple realizations of the future can be obtained by autoregressively sampling from the predicted distribution... These sample paths come in the form of token IDs that need to be mapped back to real values" / 코퍼스 설명: "...spanning various application domains including energy, transport, healthcare, retail, web, weather, **finance**, and..." |
| **Chronos-Bolt** | 별도 arXiv 논문 **확인 불가**(원 Chronos 논문 2403.07815의 후속 릴리즈로 GitHub/HF에서만 문서화) | **직접 다단계 분위수 예측(direct multi-step quantile forecast)**. T5 인코더-디코더 구조, 패치 단위 인코딩 후 디코더가 자기회귀 없이 한 번에 여러 미래 시점의 분위수(0.1~0.9)를 직접 출력 | 분위수 기반 → pinball loss 평균으로 CRPS 근사 | 확인 불가(원문 부재로 코퍼스 상세 확인 못 함) | 1차 자료(arXiv) 아님. AWS 블로그·HuggingFace `amazon/chronos-bolt-*` 모델카드로만 교차 확인. **인용 시 주의** |
| **Chronos-2** | 2510.15821 | **명시적 분위수 헤드(Quantile Head)**. Time Attention + Group Attention 트랜스포머 스택 뒤에 분위수 헤드가 위치, 사전학습 시 사용한 21개 분위수 레벨(0.01~0.99) 중 부분집합 출력 가능 | 분위수 기반 → pinball loss 평균으로 CRPS 근사(사전학습이 quantile regression objective로 이미 이 손실 사용) | 확인 불가(원문에서 finance 도메인 특정 언급 못 찾음. 합성 데이터로 다변량 구조를 부여하는 학습이라 원천 데이터 도메인은 불명확) | 목차에 "Quantile Head" 절 존재 확인, "The model is trained using **the quantile regression objective**" (§3.2) 직접 확인. ~~"기본값은 결정론적(median만)"~~ **[3단계 검증에서 삭제] 원문 전체 검색 결과 "deterministic"/"default" 관련 매치 0건 — 근거 없는 서술이었음** |
| **Moirai (1.0)** | 2402.02592 (ICML 2024) | **혼합 파라메트릭 분포(mixture of parametric distributions)**: Student-t, Log-normal, Negative binomial, 저분산 정규분포의 가중 혼합. 모델이 혼합분포의 파라미터를 직접 출력 | 파라메트릭 혼합분포 → 혼합분포에서 샘플링(논문 원문에 CRPS 평가 전용 부록 C.1 "Continuous Ranked Probability Score" 존재, 다만 세부 수식은 이번 조사에서 페이지 분량 제한으로 완독 못 함) | **[3단계 검증에서 정정] 포함됨 — LOTSA 9개 도메인 중 Econ/Fin 포함(Table 2: 23개 데이터셋, 24,919,596 관측치, 전체의 0.10%). 비중은 극소하지만 "미확인"이 아니라 "포함되어 있으나 극소 비중"이 정확한 서술** | "we overcome the issue of requiring flexible predictive distributions **with a mixture of parametric distributions**." (§1) / Appendix B.2 목차에 "Student's t-distribution / Log-normal distribution / Negative binomial distribution / Low variance normal distribution" 확인 / Table 2 도메인 목록에 Econ/Fin 확인 |
| **Moirai-MoE** | 2410.10469 | Moirai(1.0)과 **동일한 혼합분포 출력 헤드를 그대로 사용**. 백본만 sparse MoE로 교체, 출력 헤드·손실함수는 불변 | Moirai(1.0)과 동일 | 확인 불가 | "our goal is formulated as forecasting the predictive distribution of the next token $p(x_{t+1}\vert\phi)$ by predicting **the mixture distribution parameters** $\hat\phi$ (Woo et al., 2024)" — 원 Moirai 논문을 직접 인용하며 동일 방식임을 명시 (§3.3) |
| **Moirai 2.0** | 2511.11698 | **분위수 예측으로 전면 교체**. Moirai 1.0의 혼합분포 출력을 폐기하고 9개 분위수(0.1~0.9, pinball/quantile loss)를 디코더-only 구조로 직접 예측. "자기회귀적 다중분위수 디코딩(autoregressive multi-quantile decoding)" 방식으로 긴 호라이즌에서도 불확실성 유지 | 분위수 기반, **CRPS와 직접 정렬되도록 설계됨** ("directly aligned with the CRPS metric through optimization with the quantile (pinball) loss") | **[3단계 검증에서 정정, 원 서술 오류] "금융 데이터 미포함"은 틀림.** §4는 사전학습 데이터셋 도메인을 나열하지 않으며 금융 부재를 말한 적이 없음. 오히려 "GIFT-Eval Pretrain is a subset of LOTSA"라고 명시하는데, LOTSA는 Moirai 1.0에서 확인된 대로 Econ/Fin을 포함함 → Moirai 2.0도 금융 데이터에 노출됐을 가능성이 높음(과소대표+누출 위험 쪽으로 재해석 필요) | 초록 원문: "Compared to Moirai 1.0, Moirai 2.0 replaces masked-encoder training, multi-patch inputs, and **mixture-distribution outputs with a simpler decoder-only architecture, single patch, and quantile loss.**" / §4 "GIFT-Eval Pretrain is a subset of LOTSA" 확인 |
| **TTM (Tiny Time Mixers)** | 2401.03955 (NeurIPS 2024) | **점 예측만. 확률적 출력 없음.** 본문(§2.1 아키텍처, §3.1 손실함수)에 "quantile"/"probabilist" 관련 언급 없음. 손실함수는 `L = ‖Y − Ŷ‖²₂`(§3.1), 회귀 헤드는 선형(linear) 결정론적 헤드(§2.1) | 해당 없음(점 예측 → CRPS 계산 불가) | 확인 불가 | 로컬 사본은 §3.1까지만 확보되어 본문 전체 검색은 불가했으나, 확보된 범위(아키텍처+손실함수 정의) 내에서 확률적 출력 관련 서술 없음 확인. **[3단계 검증에서 정정]** 참고문헌 [28] DeepAR 논문 제목에 "Probabilistic"이 포함되지만 이는 인용된 타 논문 제목일 뿐 TTM 자체의 출력 방식과 무관 — "참고문헌 포함 매치 0건"이라는 표현은 부정확했으므로 삭제. 결론(점 예측 전용) 자체는 유지 |
| **Lag-Llama** | 2310.08278 | **파라메트릭 분포 헤드 + 샘플 경로**. 디코더 마지막 층이 분포 헤드(distribution head)로, Student's t-분포의 3개 파라미터(자유도·평균·스케일)를 직접 출력. 추론 시 자기회귀적으로 여러 궤적을 샘플링 | 파라메트릭 분포에서 샘플링 → 경험적 CRPS(원문 Table 1이 실제로 "CRPS of Lag-Llama zero-shot..."을 보고) | 확인 불가(원문에 금융 도메인 특정 언급 없음. Azure/Borg/Alibaba 클라우드, 항공질, ETT 등 도메인만 명시) | "For our experiments, we adopt **a Student's t-distribution** (Student, 1908) and output the three parameters corresponding to this distribution, namely its degrees of freedom, mean, and scale" (§4.3) / "we can obtain many simulated trajectories of the future... From these empirical samples, we can calculate the uncertainty intervals" (§4.2) |
| **Toto** | 2407.07874 (Technical Report) | **Student-T 혼합모델(SMM, Student-T Mixture Model) 헤드**. k=16개 Student-t 성분의 가중 혼합. 추론 시 혼합분포에서 자기회귀적으로 샘플링(최소 100개, LSF 벤치마크는 200개) | 혼합분포 샘플 기반 → 경험적 CRPS 가능(단, **원문 자체는 CRPS를 보고하지 않고 MAE/MSE, sMAPE/sMdAPE만 사용** — 확률적 헤드를 갖췄지만 논문에서 확률적 지표 평가는 하지 않음) | **[3단계 검증에서 정정, 원 서술 오류] "금융 데이터 학습에 사용 안 함"은 틀림.** §4에 "the remaining points come from the LOTSA dataset"라고 명시 — LOTSA는 Econ/Fin 도메인을 포함하므로 Toto도 금융 데이터에 소량 노출됐을 가능성이 있음(75% Datadog 관측성 지표 + LOTSA 공개데이터 + 5% 합성 구성 중 LOTSA 부분). SMM 설계 근거로도 "이전에 두꺼운 꼬리를 가진 **금융 시계열** 모델링에 가능성을 보인 방법"이라고 선행연구를 인용 | "we use a **Student-T mixture model (SMM)**, a robust generalization of GMMs... that has previously shown promise for modeling **heavy-tailed financial time series**" (§3.4) / "the remaining points come from the **LOTSA dataset**" (§4) |
| **Sundial** | 2502.00816 | **생성적(flow-matching) 샘플링**. "TimeFlow Loss"라는 flow-matching 기반 손실로 다음 패치의 분포를 사전분포 가정 없이 학습, 추론 시 ODE를 풀어 다중의 그럴듯한 미래(sample)를 생성. 파라메트릭 분포 가정도, 이산 토큰화도 없음 | 생성 샘플 기반 → 경험적 CRPS(논문이 "probabilistic forecasting benchmarks"에서 SOTA라고 주장하나, 이번 조사에서는 도구 제한으로 정량적 CRPS 수치까지는 미확인) | **확인 불가.** 원문 fetch가 서론~예비지식(Flow-Matching 정의)까지만 완료되고 §4.2 TimeBench(학습데이터 구성) 절은 읽지 못함 | "We propose TimeFlow Loss to predict next-patch's distribution, allowing Transformers to be trained **without discrete tokenization** and make **probable predictions**." (Abstract 근처) / 웹서치 교차확인(비1차자료): "can generate multiple probable predictions... more flexibility... than using parametric densities" |

---

## 종합 소견 — CRPS 계산 설계에 대한 시사점

**1) 모델군이 최소 3가지 서로 다른 확률 출력 메커니즘으로 나뉘고, 이는 CRPS 계산 코드 경로를 최소 3갈래로 분기시켜야 함을 의미한다.** (i) *분위수 직접 출력형*(Chronos-Bolt, Chronos-2, Moirai 2.0, TimesFM 2.5 quantile head) — pinball loss의 분위수 평균으로 CRPS를 근사하는 것이 표준(`gluonts`의 quantile-based CRPS 근사와 동일 계열). (ii) *파라메트릭 분포/혼합분포형*(Moirai 1.0·Moirai-MoE의 mixture, Lag-Llama의 Student-t, Toto의 SMM) — 분포에서 샘플링한 뒤 경험적 CRPS를 계산하거나, 분포가 닫힌 형태(closed-form)라면 이론적 CRPS 공식을 쓸 수도 있음. (iii) *이산 토큰 샘플 경로형*(Chronos 1세대) — 자기회귀 샘플링으로 얻은 다중 궤적에서 경험적 CRPS. **TTM과 TimesFM 1.0은 점 예측만 지원하므로 애초에 CRPS를 계산할 대상이 없다** — 이 두 모델은 우리 연구의 "캘리브레이션 붕괴" 축에서 제외하거나, 별도로 "확률 출력을 강제로 부여할 수 없는 모델"로 명시적으로 분류해 방법론 한계 섹션에서 다뤄야 한다.

**2) "동일한 CRPS 수치"라도 모델마다 근사 오차의 근원이 다르다는 점을 실험 설계에 반영해야 한다.** 분위수 직접 출력형은 학습 손실 자체가 pinball loss라서 CRPS와 최적화 목적함수가 정합적인 반면(Moirai 2.0 원문이 "directly aligned with the CRPS metric"이라고 명시), 혼합분포형과 샘플 경로형은 학습 목적함수가 NLL이나 교차엔트로피이고 CRPS는 사후 평가지표일 뿐이다. 즉 붕괴 임계점을 비교할 때 "이 모델은 애초에 CRPS를 잘 내도록 훈련됐고, 저 모델은 아니다"라는 훈련-평가 목적함수 불일치를 통제 변수로 명시하지 않으면, 관찰되는 "붕괴"가 금융 메커니즘 때문인지 훈련-평가 목적함수 미스매치 때문인지 혼동될 위험이 있다. 샘플 개수(Toto는 최소 100~200개, **Chronos는 원문 기준 20개 sample paths**로 훨씬 적음 — [3단계 검증에서 정정])에 따라 경험적 CRPS의 몬테카를로 분산이 달라지므로, 모델 간 비교 시 샘플 수를 통일하거나 최소한 보고해야 한다.

**3) [3단계 검증에서 결론 수정] 금융 데이터는 "배제"가 아니라 "극소 비중으로 이미 포함 + 누출 위험"으로 재해석해야 한다.** 원 조사는 Moirai 2.0·Toto가 금융 데이터를 명시적으로 배제했다고 잘못 판단했으나, 검증 결과 둘 다 LOTSA(Large-scale Open Time Series Archive)의 하위집합을 사전학습에 사용하며, LOTSA는 Moirai 1.0 원문 Table 2가 확인해주듯 Econ/Fin 도메인(23개 데이터셋, 24,919,596 관측치, 전체의 0.10%)을 포함한다. 즉 Chronos뿐 아니라 Moirai 1.0/2.0·Moirai-MoE·Toto 모두 극소 비중이나마 금융 시계열에 노출됐을 가능성이 있다. 이는 (a) look-ahead 누출 리스크가 Chronos뿐 아니라 LOTSA 기반 모델 전반(Moirai 계열, Toto)에도 걸쳐 있다는 뜻이고(진행상황.md 리스크 3번 범위 확대 필요), (b) "완전히 분포 외(OOD)인 금융 도메인에서의 붕괴"라는 원래 프레이밍은 정확하지 않으며, 오히려 "압도적으로 과소대표된(0.1% 수준) 도메인에서의 붕괴"로 연구 동기를 재서술하는 것이 원문에 더 충실하다. TTM·Lag-Llama의 코퍼스 상세는 여전히 확인 불가.

---

## 확인하지 못한 항목 (명시)
1. **TimesFM 2.5의 quantile head 세부 구조 및 학습 방식** — arXiv 1차 논문이 아직 확인되지 않음. GitHub/HF 문서로만 교차 확인.
2. **Chronos-Bolt의 아키텍처 세부 논문** — 별도 arXiv 논문 존재 여부 자체가 불확실. 현재는 원 Chronos 논문(2403.07815)의 실무적 후속 릴리즈로만 취급.
3. **Moirai(1.0) Appendix C.1 CRPS 계산 수식 전문** — 목차 존재는 확인했으나 페이지 분량 제한으로 수식까지는 못 읽음.
4. **Chronos-2, Chronos-2 사전학습 데이터의 금융 도메인 포함 여부** — 그룹어텐션용 합성 다변량 구조화 학습이라 원천 데이터 도메인이 원문에서 불명확.
5. **Sundial의 TimeBench 데이터 구성(§4.2) 및 CRPS 실측치** — 도구 응답 크기 제한으로 서론~예비지식까지만 읽음. 후속 조사 필요.
6. **TTM, Lag-Llama, Moirai, Moirai-MoE, Toto의 사전학습 코퍼스 내 금융 데이터 비중** — 전부 "확인 불가"(원문에 도메인 리스트가 없거나, 있어도 금융 언급이 없었음).

## 후속 조사 제안
- Sundial §4.2(TimeBench) 재조사 — 도구 제한 회피를 위해 섹션별로 나눠 fetch.
- TimesFM 2.5 quantile head가 실제로 별도 기술보고서/논문으로 나왔는지 재확인(2026년 이후 릴리즈 노트 추적).
- Chronos 원 논문의 사전학습 코퍼스 목록(부록)에서 "finance" 라벨이 붙은 구체적 데이터셋명 확인 — look-ahead 누출 리스크 평가에 직결.
