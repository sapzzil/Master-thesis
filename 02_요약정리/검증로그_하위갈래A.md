# 검증로그 — 하위갈래 A (TSFM 아키텍처와 확률 출력 방식)

> 검증일: 2026-08-15
> 검증 대상: `02_요약정리/하위갈래A_TSFM아키텍처_확률출력.md`
> 검증자: 독립 검증 에이전트(원 요약 작성자와 별개)
> 검증 방식: `01_자료원문/` 로컬 원문 대조 + 부족분 웹 재조회(arXiv HTML / ar5iv / HuggingFace 공식 모델·데이터셋 카드)
> **원칙**: 원문에서 직접 읽은 문장만 근거로 인정. 추론은 "추론"으로 명시. 확인 못 한 것은 "확인 불가"로 남김.

---

## 0. 총평 (먼저 결론)

**핵심 결론(=5단계 모델 선정에 직결되는 주장)은 유지된다.** 즉 "TimesFM 1.0과 TTM은 점 예측만 지원하여
CRPS 계산 대상이 아니고, 나머지 모델은 분위수/샘플/파라메트릭 분포 중 하나로 확률 출력을 지원한다"는
결론은 원문 대조로 **재확인되었다**. TTM은 심지어 제3자(Moirai 1.0 논문 Table 1)가 "Probabilistic
Forecasting: ✗"로 명시적으로 분류하고 있어 교차 근거까지 확보되었다.

**그러나 "금융 데이터 사전학습 포함 여부" 축에서 중대한 오류가 발견되었다.** 요약이 "명시적으로 금융
데이터 미포함"이라고 단정한 Moirai 2.0과 Toto가, 실제로는 **금융/경제 도메인을 포함한 코퍼스(LOTSA)를
직간접적으로 학습에 사용**하고 있다. Moirai 1.0 원문 Table 2는 LOTSA의 9개 도메인 중 하나로
**Econ/Fin(23개 데이터셋, 24,919,596 관측치, 0.10%)**을 명시하고 있다. 이 오류는 요약 §종합소견 3)의
논증("대부분의 TSFM이 금융을 분포 외로 접한다")을 **부분적으로 무효화**하므로 반드시 수정해야 한다.

또한 **환각 의심 1건(Chronos-2 "기본값은 결정론적")**, **사실오류 1건(Chronos 샘플 수 100~200개)**,
**검증 방법 서술의 허위 1건(TTM 정규식 매치 0건)**이 확인되었다.

---

## 1. 검증한 주장 목록과 판정

### 1-1. 확률 출력 형태 (모델별 핵심 주장)

| # | 검증 대상 주장 | 판정 | 원문 근거 |
|---|---|---|---|
| A1 | TimesFM 1.0은 점 예측만, 확률출력은 Future Work | **정확** | `2310.10688_...md` L215 (A.1 Limitations and Future Work): "*Probabilistic Forecasting.* It should be straightforward to train with probabilistic loss functions in our framework... however, being one of the first works of building a single foundation model for forecasting, **this was not our main focus and is left to future explorations.**" — 요약 인용문과 **축자 일치**. **추가 근거(요약이 놓친 더 강한 근거)**: 같은 논문 L85 §4 Loss Function: "**In this work, we focus on point forecasting.** Therefore we can use a point forecasting loss during training like Mean Squared Error (MSE)." |
| A2 | Chronos = 샘플 경로(토큰 자기회귀 샘플링) | **정확** | `2403.07815_...md` L111: "CHRONOS models are probabilistic by design and multiple realizations of the future can be obtained by autoregressively sampling from the predicted distribution... **These sample paths come in the form of token IDs that need to be mapped back to real values**" — 축자 일치 |
| A3 | Chronos-Bolt = T5 인코더-디코더, 패치 인코딩, 직접 다단계 분위수 예측 | **정확**(단, 1차자료 아님) | HuggingFace `amazon/chronos-bolt-base` 모델카드: "It is based on the **T5 encoder-decoder architecture**... It **chunks the historical time series context into patches**... The decoder then uses these representations to **directly generate quantile forecasts across multiple future steps—a method known as direct multi-step forecasting**." 별도 arXiv 논문 부재도 재확인(모델카드가 인용하는 논문은 2403.07815 및 T5 1910.10683뿐) |
| A4 | Chronos-2 = 명시적 Quantile Head, 21개 분위수(0.01~0.99), quantile regression objective | **정확** | `2510.15821_...md` L265-267 "#### Quantile Head. ... produce the **direct multi-step quantile forecast**"; L269 "Chronos-2 predicts a set of **21 quantiles Q={0.01,0.05,0.1,…,0.9,0.95,0.99}**"; L278 "The model is trained using **the quantile regression objective**" — 모두 축자 일치 |
| A5 | Moirai 1.0 = 혼합 파라메트릭 분포(Student-t / log-normal / negative binomial / low variance normal) | **정확** | arXiv HTML 재조회(ar5iv 2402.02592) §3.1.3: "we propose to use a **mixture of parametric distributions**... we specifically propose to use the following mixture components: i) a **Student's t-distribution**..., ii) a **negative binomial distribution** for positive count data, iii) a **log-normal distribution**..., and iv) a **low variance normal distribution** for high confidence predictions." 및 §1 (로컬 `2402.02592_...md` L43) "we overcome the issue of requiring flexible predictive distributions **with a mixture of parametric distributions**" — 축자 일치 |
| A6 | Moirai-MoE = Moirai와 동일한 혼합분포 출력 | **대체로 정확(단, 표현 과소)** | `2410.10469_...md` L121 §3.3: "our goal is formulated as forecasting the predictive distribution of the next token p(x_{t+1}|φ) by predicting **the mixture distribution parameters** φ̂ (Woo et al., 2024)... The following **negative log-likelihood** is minimized during training" — 축자 일치. 상세는 아래 1-3 D5 참조 |
| A7 | Moirai 2.0 = 분위수 전면 교체, 9개 분위수, CRPS와 직접 정렬 | **정확** | `2511.11698_...md` L14 초록: "Moirai 2.0 replaces masked-encoder training, multi-patch inputs, and **mixture-distribution outputs with a simpler decoder-only architecture, single patch, and quantile loss.**" / L40 §2: "it outputs quantile forecasts, **directly aligned with the CRPS metric through optimization with the quantile (pinball) loss**" / L30: "We set the quantile levels as **{0.1, 0.2, ..., 0.9}**" — 모두 축자 일치 |
| A8 | TTM = 점 예측만, 확률출력 없음 | **결론은 정확 / 근거 서술은 부정확** | 로컬 사본은 §3.1 도입부까지만(부분 확보)이라 "논문 전체 검색" 불가. **웹 재조회(arXiv HTML v8)**로 확인: §3.1 "We pre-train the TTM with **mean squared error (MSE) loss** calculated over the forecast horizon: L = ‖Y − Ŷ‖²₂" / §3.2 "The fine-tuning also optimizes the forecasting objective with **MSE loss**" / §2.1 "**Forecast head** consists of a **linear head** designed to produce the forecast output". **교차 근거**: Moirai 1.0 논문 Table 1이 TTM을 "Probabilistic Forecasting: **✗**"로 분류. 근거 서술 문제는 아래 D3 참조 |
| A9 | Lag-Llama = Student-t 분포 헤드(3개 파라미터) + 자기회귀 샘플 경로 | **정확** | `2310.08278_...md` L81 §4.3: "we adopt **a Student's t-distribution** (Student, 1908) and output **the three parameters** corresponding to this distribution, namely its **degrees of freedom, mean, and scale**" / L77 §4.2: "we can obtain **many simulated trajectories** of the future... **From these empirical samples**, we can calculate the uncertainty intervals" / L121: 원문 Table 1이 실제로 CRPS를 보고 — 모두 축자 일치 |
| A10 | Toto = Student-T 혼합모델(SMM) 헤드, k=16, 최소 100(LSF 200) 샘플, 원문은 CRPS 미보고 | **정확** | `2407.07874_...md` L140 §3.4: "we use a **Student-T mixture model (SMM)**, a robust generalization of GMMs... that has previously shown promise for modeling **heavy-tailed financial time series**" / L142 "we draw samples from the mixture distribution at each timestamp... This allows us to produce prediction intervals at any quantile" / L198 "with a **minimum of 100 samples**" / L202 LSF "took the median of **200 samples**" / L346 설정표 "**Student-T Mixture Model Components 16**". CRPS 미보고도 재확인(전문 대상 "CRPS" 검색 결과 0건, 보고 지표는 MAE/MSE/sMAPE/sMdAPE) |
| A11 | Sundial = flow-matching(TimeFlow Loss) 생성 샘플링, 파라메트릭 가정·이산 토큰화 없음, ODE 풀이 | **정확** | `2502.00816_...md` L16 초록: "we propose a **TimeFlow Loss based on flow-matching**, which facilitates native pre-training of Transformers on continuous-valued time series **without discrete tokenization**. Conditioned on arbitrary-length time series, our models are pre-trained **without specifying any prior distribution** and can **generate multiple probable predictions**, achieving more flexibility... than using parametric densities." / L180 Algorithm 1 Line 4: `ŷᵢ ← ŷᵢ + FM-Net(ŷᵢ, kΔt, hᵢ)·Δt` (Euler ODE 적분) / L186 "we repeat this procedure using different initial noises and estimate statistics such as the **median and quantiles** from a set of generated predictions" |
| A12 | TimesFM 2.5 = 옵션형 연속 분위수 헤드(`use_continuous_quantile_head=True`) | **대체로 정확(수치 2건 오류)** | HuggingFace `google/timesfm-2.5-200m-pytorch` 공식 모델카드 코드 예시에 `use_continuous_quantile_head=True`, `fix_quantile_crossing=True` 존재 확인. 다만 출력 형태 기술 오류는 D6 참조 |

### 1-2. CRPS 계산 가능 여부 결론 (가장 엄격 검증 대상)

| # | 주장 | 판정 | 근거 및 비고 |
|---|---|---|---|
| B1 | "TimesFM 1.0과 TTM은 점 예측만 지원하므로 애초에 CRPS를 계산할 대상이 없다" | **정확 — 결론 유지** | A1/A8 근거. TimesFM 1.0은 §4에서 "we focus on point forecasting", 학습 손실 MSE. TTM은 사전학습·미세조정 모두 MSE, 출력은 linear forecast head. Moirai Table 1의 제3자 분류(TTM: Probabilistic ✗)로 교차 확인 |
| B2 | 분위수 직접 출력형(Chronos-Bolt, Chronos-2, Moirai 2.0, TimesFM 2.5)은 pinball loss 평균으로 CRPS 근사 | **정확** | Moirai 2.0이 스스로 "directly aligned with the CRPS metric through optimization with the quantile (pinball) loss"라고 명시(L40). Chronos 논문도 WQL과 CRPS의 관계를 명시: "the **WQL is related to the continuous ranked probability score (CRPS**, Gneiting & Raftery (2007))"(`2403.07815` L187) |
| B3 | 파라메트릭/혼합분포형(Moirai 1.0·MoE, Lag-Llama, Toto)은 샘플링 후 경험적 CRPS | **정확** | A5/A6/A9/A10 근거. Moirai 계열은 NLL 학습, Lag-Llama·Toto는 샘플에서 분위수 산출 |
| B4 | 이산 토큰 샘플 경로형(Chronos 1세대)은 다중 궤적에서 경험적 CRPS | **정확** | A2 근거 + `2403.07815` L187: "For methods requiring sampling, we estimated the quantiles using **20 sample forecast paths**" |
| B5 | 학습-평가 목적함수 정합성 차이를 통제변수로 다뤄야 한다 | **정확(논지 타당)** | Moirai 2.0(pinball=CRPS 정합) vs Moirai 1.0/Lag-Llama/Toto(NLL) vs Chronos(cross-entropy). 원문 근거로 뒷받침됨 |
| B6 | **"TimesFM은 CRPS 불가"** (버전 미지정 시) | **주의 필요 — 서술 보완 권고** | TimesFM **1.0**은 불가하나 **2.5**는 분위수 헤드 보유. 2026년 시점에 실제로 돌릴 체크포인트는 2.5이므로, 논문 본문에서 "TimesFM"을 버전 없이 "점 예측 전용"으로 분류하면 심사에서 반박당할 수 있음. **반드시 버전 명기 필요** |

### 1-3. 발견된 부정확·과장·환각 (D 항목)

| # | 위치 | 판정 | 상세 |
|---|---|---|---|
| **D1** | Moirai 2.0 행 "금융데이터 포함여부: **명시적으로 금융 데이터 미포함** ... **§4 Pretraining Datasets 전체를 읽고 금융 데이터 부재 확인**" | **부정확 (중대)** | `2511.11698_...md` §4(L141~159) 전문을 다시 읽었다. §4는 **도메인을 열거하지 않으며, 금융이 없다고 말한 적이 없다.** 오히려 L147이 "**GIFT-Eval Pretrain is a subset of LOTSA introduced by Woo et al. [34]**"라고 명시한다. 그리고 Moirai 1.0(LOTSA) 원문 Table 2는 LOTSA의 9개 도메인 중 하나로 **Econ/Fin**을 열거한다(아래 D2). 또한 Chronos-Mixup도 "non-leaking subset of **Chronos data**"에서 생성되는데(L151), Chronos 코퍼스에는 finance가 포함된다(A2 근거의 L159). 즉 **Moirai 2.0의 사전학습 코퍼스에는 금융/경제 시계열이 (비중은 작지만) 포함되어 있다.** "명시적 미포함"은 원문에 없는 단정이며, 요약이 스스로 세운 "확인한 것만 기재" 원칙에 위배 |
| **D2** | Moirai 1.0 행 "금융데이터 포함여부: **확인 불가**(LOTSA 27B 관측치, 9개 도메인이라고만 명시)" | **해소 가능했던 항목을 놓침 (신규확인)** | arXiv HTML 재조회 결과 **Table 2: Key statistics of LOTSA by domain**가 9개 도메인을 전부 열거한다: Energy / Transport / Climate / CloudOps / Web / Sales / Nature / **Econ/Fin** / Healthcare. **Econ/Fin = 23개 데이터셋, 24,919,596 관측치, 전체의 0.10%.** (참고: 공식 HF 데이터셋 `Salesforce/lotsa_data` subset 목록에도 `bitcoin_with_missing`, `fred_md`, `cif_2016_6/12`, `m1/m3/m4` 계열, `godaddy` 등 금융·경제 계열이 실재) |
| **D3** | TTM 행 "논문 **전체**(본문+참고문헌)에 quantile, probabilist 관련 언급이 **전무**함(직접 검색 확인)" / "정규식 검색 결과 **매치 0건(참고문헌 포함)**" | **부정확 (검증 방법 서술 자체가 사실이 아님)** | ① 로컬 사본은 "수집 상태: **부분** (…서론~3.1 도입부까지만 확보)"으로 명시되어 있어 애초에 전문 검색이 불가능했다. ② 웹 재조회한 arXiv HTML v8 기준으로도 매치는 **0건이 아니다**: 참고문헌 [28] Salinas et al. "DeepAR: **Probabilistic** forecasting with autoregressive recurrent networks"가 매치된다. ③ **결론(TTM=점 예측)은 옳지만, 제시된 검증 근거가 재현되지 않으므로 근거를 교체해야 한다.** 올바른 근거는 §3.1의 MSE 손실 수식과 §2.1의 linear forecast head, 그리고 Moirai Table 1의 제3자 분류 |
| **D4** | Chronos-2 행 "**기본값은 결정론적(median만)**" | **환각 의심 (근거 없음)** | 로컬 전문 대상 `deterministic`, `default` 검색 **0건**. Chronos-2는 §3.2에서 항상 21개 분위수를 출력하는 quantile head 구조로 기술되며, "기본값이 결정론적"이라는 서술의 출처를 원문에서 찾을 수 없다. **삭제하거나 출처를 명시해야 한다** |
| **D5** | Moirai-MoE 행 "**백본만** sparse MoE로 교체, 출력 헤드·손실함수는 불변" | **부분 부정확(과소 서술)** | 예측분포 계열(mixture)과 손실(NLL)이 불변인 것은 맞다. 그러나 `2410.10469_...md` L62는 "rather than using **multi heuristic-defined input/output projection layers**..., Moirai-MoE utilizes a **single input/output projection layer**"라고 명시하고, 같은 문장이 "adopts a **decoder-only training objective**"(masked-encoder → decoder-only)도 명시한다. 즉 **출력 프로젝션 층의 구성과 학습 패러다임이 바뀌었다.** "백본만"은 오해를 부름 |
| **D6** | TimesFM 2.5 행 "**약 30M 파라미터 추가 모듈**", "P10~P90 등 **10개 분위수** 출력" | **수치 2건 부정확** | ① HF 공식 모델카드에는 quantile head의 파라미터 수(30M) 언급이 **없다**. 출처 미상 수치이므로 삭제 또는 출처 명시 필요. ② 모델카드 코드 예시의 주석은 `quantile_forecast.shape # (2, 12, 10): **mean, then 10th to 90th quantiles**` 이다. 즉 10개 채널은 **평균 1개 + 분위수 9개(P10~P90)** 이며, "10개 분위수"가 아니다. CRPS 근사 시 분위수 채널만 골라내야 하므로 **구현 단계에서 실질적 영향이 있는 오류** |
| **D7** | 종합소견 2) "샘플 개수(Toto는 최소 100~200개, **Lag-Llama·Chronos도 유사한 수준**)" | **부정확 (사실오류)** | `2403.07815_...md` L187: "For methods requiring sampling, we estimated the quantiles using **20 sample forecast paths**." Chronos 원 논문의 샘플 수는 **20개**로, Toto의 100~200과 한 자릿수 차이가 난다. 몬테카를로 분산 통제를 논하는 문단에서 이 오류는 논지 자체를 약화시킨다. Lag-Llama의 샘플 수는 원문에서 **확인 불가**(수치 미기재) |
| **D8** | Toto 행 "**명시적으로 금융 데이터 학습에 사용 안 함**(75% Datadog + LOTSA 공개데이터 + 5% 합성)" | **부정확** | `2407.07874_...md` L158: "roughly three-quarters are anonymous observability metrics from the Datadog platform. **The remaining points come from the LOTSA dataset [15]**". LOTSA에는 Econ/Fin 도메인 23개 데이터셋이 포함된다(D2). 따라서 Toto도 **소량이지만 금융/경제 시계열을 학습에 사용했다.** "명시적으로 사용 안 함"은 틀림. (SMM 설계 근거로 금융 선행연구를 인용했을 뿐 학습에는 안 썼다는 요약의 구분 자체는 논리적으로 타당하나, 사실 판정이 틀렸다) |
| **D9** | TimesFM 1.0 행 "금융데이터 포함여부: 확인 불가(**코퍼스 도메인 상세 미기재**)" | **부정확(근거 서술)** | `2310.10688_...md` **Table 1 (Composition of TimesFM pretraining dataset)** 이 코퍼스를 데이터셋 단위로 **전부 명시**한다(Synthetic / Electricity / Traffic / Weather / Favorita Sales / LibCity / **M4 전 granularity** / Wiki 4종 / Trends 4종). "상세 미기재"는 사실과 다르다. 다만 **"finance" 라벨은 없고**, M4에 Finance 카테고리 계열이 포함되는지는 원문이 언급하지 않으므로 **금융 포함 여부 자체는 여전히 확인 불가**. 판정은 유지하되 사유를 고쳐야 함 |
| **D10** | Sundial 행 원문 근거 표기 | **출처 등급 오기** | ① "We propose TimeFlow Loss to predict next-patch's distribution, allowing Transformers to be trained without discrete tokenization and make probable predictions."는 **직접 인용이 아니라 요약자의 패러프레이즈**다. 실제 초록은 "To predict the next-patch's distribution, we propose a TimeFlow Loss based on flow-matching, which facilitates native pre-training of Transformers on continuous-valued time series without discrete tokenization." ② 요약이 "**웹서치 교차확인(비1차자료)**"로 강등해 표기한 "can generate multiple probable predictions... more flexibility... than using parametric densities"는 **논문 초록 원문에 그대로 존재하는 1차 자료**다(L16). 출처 등급을 올려야 함 |
| **D11** | Moirai 1.0 행 "Appendix B.2 **목차**에 …확인" | **근거 등급 과소** | 혼합 성분 4종은 **본문 §3.1.3에 완전한 문장으로** 기술되어 있다(A5 인용). 목차 수준 근거가 아니라 본문 근거로 격상 가능 |
| **D12** | Moirai 2.0 "자기회귀적 다중분위수 디코딩(autoregressive multi-quantile decoding)" | **경미 (용어 표기)** | 원문 표현은 초록 "**recursive** multi-quantile decoding", Figure 1 캡션 "**autoregressive multi-step** quantile decoding", Table 2 "Autoreg. quantile dec." 이다. 인용부호를 쓰려면 원문 표현 중 하나를 그대로 써야 함 |

### 1-4. 자료 무결성 관련 발견 (요약 파일 밖의 문제)

| # | 대상 | 문제 |
|---|---|---|
| E1 | `01_자료원문/2510.15821_Chronos-2_...md` | 헤더가 "수집 상태: HTML 전문 자동 수집 (web_fetch, **잘림 없이 전체 저장됨**)"이라고 기재되어 있으나, 실제 파일은 **331줄 §4.1 중간에서 절단**되어 있다. Appendix A(Table 6, 학습 데이터셋 전체 목록)는 미확보. **헤더 표기를 "부분"으로 정정 필요** |
| E2 | `01_자료원문/2402.02592_Moirai_...md` | 수집 상태 "부분(§3 Problem Formulation 도입부까지)"이 정확. 요약이 근거로 든 §3.1.3 혼합분포, Appendix B.2, Appendix C.1은 **이 로컬 사본에 존재하지 않는다.** 이번 검증에서는 웹 재조회로 §3.1.3과 Table 2를 확보했으나, **로컬 사본 갱신 권장** |
| E3 | `01_자료원문/2401.03955_Tiny_Time_Mixers_TTM.md` | 수집 상태 "부분(§3.1 도입부까지)". 요약의 "논문 전체 검색" 주장과 모순(D3). **로컬 사본 갱신 권장** |

---

## 2. 새로 해소된 "확인 불가" 항목

| 원 요약의 미확인 항목 | 해소 여부 | 내용 |
|---|---|---|
| **5. Sundial §4.2 TimeBench 구성** | **해소** (놀랍게도 로컬 사본에 이미 있었음 — `2502.00816_...md` L188-194) | "TimeBench... comprises **over a trillion time points** from various sources... Several datasets originate from research teams (**Woo et al. 2024 [=Moirai/LOTSA]; Ansari et al. 2024 [=Chronos]; Liu et al. 2024b,c [=Timer/Timer-XL]**)... a small portion (**0.05%**) is generated synthetically... following **KernelSynth**... We also leverage substantial **meteorological data (ERA5)**". → **금융 도메인은 명시적으로 열거되지 않으나, 구성 요소인 LOTSA와 Chronos 코퍼스가 각각 Econ/Fin과 finance를 포함하므로 금융 시계열이 간접적으로 포함된다(추론, 근거는 D2 및 A2).** 세부 통계(Appendix A Table 4)는 여전히 미확보 |
| **1. TimesFM 2.5 quantile head 근거** | **부분 해소** | Google 공식 HF 모델카드에서 `use_continuous_quantile_head=True`, `fix_quantile_crossing=True`, 출력 shape `(B, H, 10)` = "mean, then 10th to 90th quantiles" 확인. **별도 arXiv 논문이 없다는 판정은 유지**(모델카드가 인용하는 유일한 논문은 2310.10688). 파라미터 수·학습 방식은 여전히 확인 불가 |
| **6. Moirai / Moirai-MoE / Toto의 금융 데이터 비중** | **해소** | LOTSA Table 2: **Econ/Fin 23개 데이터셋 / 24,919,596 obs / 0.10%**. Moirai 1.0 = LOTSA 학습. Moirai-MoE = "trained ... on **LOTSA**"(`2410.10469` L140). Toto = 나머지 25%가 **LOTSA**(`2407.07874` L158). **세 모델 모두 금융/경제 시계열을 소량 학습했다** |
| **(신규) Moirai 2.0의 금융 데이터** | **해소(요약의 정반대 결론)** | GIFT-Eval Pretrain = "a **subset of LOTSA**"(`2511.11698` L147), Chronos-Mixup = Chronos 데이터 기반(L151). → **금융 포함(비중 미상)**. D1 참조 |
| **(신규) TimesFM 2.5의 사전학습 코퍼스** | **신규확인** | HF 모델카드: **GiftEvalPretrain** + Wikimedia Pageviews(cutoff 2023-11) + Google Trends(cutoff 2022 EoY) + 합성/증강 데이터. **1.0과 코퍼스가 다르며, GiftEvalPretrain ⊂ LOTSA이므로 금융 데이터가 포함된다.** look-ahead 누출 평가 시 TimesFM 1.0과 2.5를 분리해서 다뤄야 함 |
| **(신규) Lag-Llama의 도메인 구성** | **부분 해소** | `2310.08278` L105: "27 time series datasets from several sources across **six different semantically grouped domains** such as energy, transportation, **economics**, nature, air quality and cloud operations". → **"economics" 도메인 포함**. 다만 L109가 "domain은 단지 라벨"이라고 단서를 달았고, 개별 데이터셋 목록(Appendix A)은 로컬 사본에 요약 형태로만 있어 finance 특정 여부는 확인 불가. 참고로 평가용 unseen 데이터셋에는 **EXCHANGE**(환율)가 포함됨(L121) |
| **(신규) Chronos의 실제 샘플 수** | **신규확인** | 20개 sample paths (`2403.07815` L187). D7 참조 |
| **(신규) Chronos의 WQL–CRPS 관계 근거** | **신규확인** | "the **WQL is related to the CRPS** (Gneiting & Raftery (2007))... we compute the WQL on **9 uniformly-spaced quantile levels {0.1,...,0.9}**"(L187). 우리 논문의 CRPS 근사 절차를 정당화할 때 인용 가능한 1차 근거 |
| **(신규) TTM 점예측 판정의 제3자 교차근거** | **신규확인** | Moirai 1.0 논문 Table 1이 TTM을 "Any-variate(Zero-shot) ✗ / **Probabilistic Forecasting ✗** / Flexible Distribution −"로 분류. 같은 표에서 Lag-Llama는 "Probabilistic ✓ / Flexible Distribution ✗"로 분류(Student-t 단일 분포와 정합) |

---

## 3. 여전히 남은 "확인 불가" 항목

1. **Moirai 1.0 Appendix C.1 "Continuous Ranked Probability Score" 수식 전문** — 목차 항목 존재는 재확인(`C.1 Evaluation Metrics → Continuous Ranked Probability Score / Mean Scaled Interval Score`). 그러나 arXiv HTML과 ar5iv 모두 fetch가 §3.2 중간에서 절단되어 부록 본문 도달 실패. **PDF 직접 열람 필요.**
2. **Chronos-2 Appendix Table 6(학습 데이터셋 전체 목록)** — 로컬 사본 절단(E1). 금융 데이터 포함 여부는 미확인. 단, §4.1이 "select datasets from the **Chronos** and **GIFT-Eval** pretraining corpora"라고 밝혔고 두 코퍼스 모두 금융을 포함하므로 **포함 가능성이 높음(추론)**.
3. **Sundial Appendix A Table 4(TimeBench 세부 통계)** 및 **Sundial의 정량 CRPS 수치** — 로컬 사본이 §5 Experiments 도입부에서 절단.
4. **TTM Appendix의 사전학습 데이터셋 목록** — Monash + LibCity라는 것만 확인. Monash 아카이브 자체에는 bitcoin/fred_md/cif_2016 등 금융·경제 계열이 존재하나, **TTM이 그중 무엇을 실제로 썼는지는 확인 불가**.
5. **TimesFM 2.5 quantile head의 파라미터 수·학습 손실·학습 방식** — 공식 문서에 기재 없음. 요약의 "약 30M"은 출처 미상.
6. **Chronos-Bolt의 학습 데이터 세부 구성** — 모델카드는 "trained on nearly **100 billion** time series observations"만 명시. 도메인 구성 확인 불가.
7. **Chronos 원 논문 부록의 finance 라벨 데이터셋 구체명** — 로컬 사본이 References 중간에서 절단되어 부록 미확보. **look-ahead 누출 리스크 평가에 직결되므로 우선순위 높음.**
8. **Lag-Llama 추론 시 샘플 개수** — 원문에 수치 미기재.
9. **LOTSA Econ/Fin 23개 데이터셋의 개별 명칭·기간** — 논문 부록 또는 HF 데이터셋 카드에서 추가 확인 필요(공식 HF subset 목록에서 `bitcoin_with_missing`, `fred_md`, `cif_2016_6/12`, `godaddy`, `m1/m3/m4` 계열 등이 후보로 관측되나, 도메인 라벨과의 매핑은 미확인).

---

## 4. 원 요약 파일 수정 제안 (직접 수정하지 않음 — 제안만)

우선순위 순으로 정리한다. **[필수]**는 논문 논증에 직접 영향을 주는 항목.

### [필수-1] Moirai 2.0 행 "금융데이터 포함여부" 칸 전면 교체 (D1)
- **현재**: "**명시적으로 금융 데이터 미포함.** 사전학습 코퍼스 5종: ... 금융 시계열 없음"
- **수정안**: "**금융 포함(비중 미상).** §4는 코퍼스 5종만 열거하고 도메인 구성을 제시하지 않으며, 금융 부재를 명시한 적 없음. 오히려 GIFT-EVAL PRETRAIN을 '**a subset of LOTSA**'로 명시(§4)하고, LOTSA는 Econ/Fin 도메인 23개 데이터셋·24.9M 관측치(0.10%)를 포함(Moirai 1.0 Table 2). Chronos-Mixup도 Chronos 데이터(finance 포함) 기반. **비중은 확인 불가**"
- **원문 근거 칸**도 "§4 전체를 읽고 금융 데이터 부재 확인" → "§4 L147 'GIFT-Eval Pretrain is a subset of LOTSA'; Moirai 1.0 Table 2 Econ/Fin"으로 교체

### [필수-2] Toto 행 "금융데이터 포함여부" 수정 (D8)
- **현재**: "**명시적으로 금융 데이터 학습에 사용 안 함**"
- **수정안**: "**소량 포함.** 약 75%는 Datadog 관측성 지표이나, **나머지는 LOTSA**('The remaining points come from the LOTSA dataset', §4)이며 LOTSA에 Econ/Fin 도메인이 포함됨. 단 금융은 설계 목표가 아니며 비중 극소로 추정(확인 불가). SMM 설계 근거로 금융 시계열 선행연구를 인용한 것과는 별개 사안"

### [필수-3] Moirai 1.0 행 "금융데이터 포함여부" 확인 불가 → 확인됨 (D2)
- **수정안**: "**확인됨.** LOTSA Table 2가 9개 도메인을 명시: Energy / Transport / Climate / CloudOps / Web / Sales / Nature / **Econ/Fin** / Healthcare. **Econ/Fin = 23개 데이터셋, 24,919,596 관측치, 전체의 0.10%**(관측치 기준으로는 Nature 다음으로 작음)"

### [필수-4] Moirai-MoE 행 금융 확인 불가 → 확인됨
- **수정안**: "**확인됨(Moirai 1.0과 동일).** §4.1이 'trained ... on **LOTSA**'라고 명시하므로 Econ/Fin 0.10% 포함"

### [필수-5] Chronos-2 행에서 "기본값은 결정론적(median만)" 삭제 (D4)
- 원문에 근거가 없다. 삭제하거나, 라이브러리 동작에 근거한 것이라면 "(HF `chronos-forecasting` 라이브러리 기본 호출 기준 — 1차자료 아님)"으로 출처를 강등 표기할 것.

### [필수-6] 종합소견 2)의 Chronos 샘플 수 수정 (D7)
- **현재**: "Toto는 최소 100~200개, Lag-Llama·Chronos도 유사한 수준"
- **수정안**: "**Chronos는 20개**(원문 §5.1: 'we estimated the quantiles using **20 sample forecast paths**'), **Toto는 최소 100개(LSF 벤치마크 200개)**, **Lag-Llama는 원문에 수치 미기재(확인 불가)**. 즉 모델 간 샘플 수가 한 자릿수 배 이상 차이 나므로, 경험적 CRPS의 몬테카를로 분산을 통제하려면 **우리 실험에서 샘플 수를 통일해 재설정하는 것이 필수**이며 원 논문 설정을 그대로 쓰면 안 된다"
- 이 수정은 오히려 요약의 논지를 **강화**한다.

### [필수-7] TimesFM 항목의 버전 분리 강조 (B6)
- 표 아래 또는 종합소견 1)에 다음 취지의 문장 추가 제안: "**단, '점 예측 전용'은 TimesFM 1.0에 한정된 판정이다.** TimesFM 2.5는 연속 분위수 헤드를 옵션으로 제공하므로 CRPS 계산이 가능하다. 본 연구에서 'TimesFM'을 언급할 때는 항상 체크포인트 버전을 명기한다."

### [권장-8] TTM 행의 근거 문장 교체 (D3)
- **현재**: "원문 전체를 대상으로 'quantile|probabilist' 정규식 검색 결과 매치 0건(참고문헌 포함)"
- **수정안**: "§3.1 사전학습 손실이 **MSE**로 명시됨(`L = ‖Y − Ŷ‖²₂`), §3.2 미세조정도 MSE, §2.1 출력부는 '**a linear head** designed to produce the forecast output'. 확률적 헤드·분위수 손실에 대한 기술이 본문에 없음. **교차 근거**: Moirai 1.0 논문 Table 1이 TTM을 'Probabilistic Forecasting ✗'로 분류"
- (기존 문장은 재현되지 않으며, 참고문헌 [28] DeepAR 제목에 'Probabilistic'이 존재한다.)

### [권장-9] TimesFM 2.5 출력 형태 수정 (D6)
- "P10~P90 등 10개 분위수 출력" → "**출력 텐서는 (B, H, 10)이며 첫 채널이 평균, 나머지 9개가 P10~P90 분위수**(HF 모델카드 코드 주석: 'mean, then 10th to 90th quantiles'). CRPS 근사 시 평균 채널을 제외해야 함"
- "약 30M 파라미터 추가 모듈" → 출처 미상이므로 **삭제** 또는 "(파라미터 수는 공식 문서 미기재 — 확인 불가)"로 변경

### [권장-10] Moirai-MoE 행 서술 정밀화 (D5)
- "백본만 sparse MoE로 교체, 출력 헤드·손실함수는 불변" → "**예측분포 계열(mixture)과 손실(NLL)은 불변.** 단 FFN을 MoE로 교체하는 것 외에도, Moirai의 **주파수별 다중 입출력 프로젝션 층을 단일 층으로 통합**하고 **masked-encoder → decoder-only**로 학습 목적을 전환함(§3). 따라서 '백본만 교체'가 아니라 '**출력 분포 계열만 계승**'이 정확한 표현"

### [권장-11] Sundial 행 출처 등급 정정 (D10) 및 §4.2 확인 불가 해제
- "확인 불가(§4.2 미독)" → "**§4.2 확인 완료.** TimeBench = 1조 시점 이상, 출처는 Moirai(LOTSA)/Chronos/Timer 계열 연구팀 데이터셋 + ERA5 기상 데이터, 합성은 0.05%(KernelSynth). **금융은 명시적으로 열거되지 않으나 LOTSA·Chronos 코퍼스를 포함하므로 간접 포함(추론)**. 세부 통계(Appendix A Table 4)는 여전히 확인 불가"
- 웹서치 비1차자료로 강등 표기된 인용문("can generate multiple probable predictions... more flexibility... than using parametric densities")은 **논문 초록 원문**이므로 1차자료로 격상
- 패러프레이즈를 직접 인용부호로 감싼 문장은 원문 문장으로 교체

### [권장-12] TimesFM 1.0 행 금융 사유 정정 (D9)
- "확인 불가(**코퍼스 도메인 상세 미기재**)" → "확인 불가(**Table 1에 코퍼스가 데이터셋 단위로 전부 명시되어 있으나 'finance' 라벨이 없음.** M4 전 granularity가 포함되어 M4-Finance 계열 유입 가능성은 있으나 원문 미언급)"

### [권장-13] Moirai 1.0 혼합분포 근거 격상 (D11) 및 성분 순서 정정
- "Appendix B.2 목차에 확인" → "**본문 §3.1.3에 4개 성분이 문장으로 명시**(순서: Student's t → negative binomial → log-normal → low variance normal). 상세는 Appendix B.2"

### [권장-14] Moirai 2.0 디코딩 용어 정정 (D12)
- "자기회귀적 다중분위수 디코딩(autoregressive multi-quantile decoding)" → 원문 표현 "**recursive multi-quantile decoding**"(초록) 또는 "**autoregressive multi-step quantile decoding**"(Figure 1 캡션) 중 하나로 통일

### [권장-15] 종합소견 3) 재작성 — 논지 방향 전환
- 현재 3)은 "금융은 대부분 미포함/배제 → 합성 진단·실측 대조 설계가 정당화됨"으로 논증한다. **전제가 무너졌으므로 논지를 다음으로 전환할 것을 제안한다**:
  > "금융 데이터는 대부분의 TSFM 코퍼스에 **포함되어 있으나 극소 비중**이다. LOTSA 기준 Econ/Fin은 23개 데이터셋임에도 관측치로는 **전체의 0.10%**에 불과하고(Energy 59.17%, Transport 17.73%와 대비), Chronos는 finance를 도메인으로 나열하되 비중을 밝히지 않으며, Toto는 75%가 관측성 지표다. 즉 문제는 '금융을 못 봤다(OOD)'가 아니라 '**금융을 봤지만 극소 비중이라 금융 특유의 메커니즘이 사전학습 표현에 반영되지 못했다(under-representation)**'로 재정식화되어야 한다. 이는 (a) look-ahead 누출 리스크가 Chronos·Moirai 계열·Sundial 전반에 (정도 차이는 있으나) 실재함을 뜻하고 — 특히 LOTSA의 `fred_md`, `bitcoin`, `cif_2016` 계열은 공개 벤치마크와 중복될 소지가 있음 — (b) 붕괴의 원인을 '분포 외(OOD)'가 아니라 '**과소대표(under-representation) + 메커니즘 부적합**'으로 설명해야 함을 시사한다. 합성 진단·실측 대조 설계의 정당성은 유지되지만, 그 근거는 '금융 미노출'이 아니라 '**노출량 통제 불가 및 누출 위험**'이어야 한다."
- 이 재작성은 실제로 진행상황.md 리스크 3번(look-ahead 누출)과 더 강하게 연결된다.

### [권장-16] 자료원문 폴더 메타데이터 정정 (E1~E3)
- `2510.15821_Chronos-2_...md` 헤더의 "잘림 없이 전체 저장됨" → "**부분(§4.1 중간 절단, Appendix A Table 6 미확보)**"으로 정정
- `2402.02592_Moirai_...md`, `2401.03955_TTM.md`는 §3.1.3 / Table 2 / §3.1 손실식 등 이번 검증에서 웹으로 확보한 부분을 로컬 사본에 추가 수집 권장

---

## 5. 검증 커버리지 명시

- **로컬 원문으로 대조 완료**: TimesFM 1.0(전문), Chronos(§1-7), Chronos-2(§1-4.1까지 — 이후 절단), Moirai-MoE(§1-5), Moirai 2.0(전문+부록A), Lag-Llama(본문 전체), Toto(전문), Sundial(§1-5 도입부)
- **웹 재조회로 보완 완료**: Moirai 1.0(arXiv/ar5iv HTML — §3.1.3 혼합분포, Table 1 모델비교, Table 2 LOTSA 도메인 통계), TTM(arXiv HTML v8 — §2.1/§3.1/§3.2 손실 및 헤드), TimesFM 2.5(HF 공식 모델카드), Chronos-Bolt(HF 공식 모델카드), LOTSA(HF 공식 데이터셋 카드 subset 목록)
- **도달 실패**: Moirai 1.0 Appendix C.1 본문, Chronos-2 Appendix Table 6, Sundial Appendix A Table 4, Chronos Appendix 코퍼스 목록, TTM Appendix 데이터셋 목록 — 모두 §3에 "확인 불가"로 기재
- 위 범위 밖의 사항에 대해서는 본 로그에서 어떤 판정도 내리지 않았다.
