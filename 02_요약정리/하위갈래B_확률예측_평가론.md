# 하위갈래 B — 확률예측 평가론 (CRPS · Proper Scoring Rules · PIT · 캘리브레이션)

> 작성일: 2026-08-12
> 원문 직접 확인 완료. 확인 불가 항목은 명시.
> 핵심 문헌 2편의 원문 PDF를 직접 fetch하여 대조:
> 1. Gneiting, T. & Raftery, A. E. (2007). "Strictly Proper Scoring Rules, Prediction, and Estimation." *Journal of the American Statistical Association*, 102(477), 359–378. DOI: 10.1198/016214506000001437.
>    원문: https://sites.stat.washington.edu/raftery/Research/PDF/Gneiting2007jasa.pdf (저자 홈페이지 공개 PDF, JASA 정식본과 동일 페이지 번호 359–378 확인)
> 2. Gneiting, T., Balabdaoui, F. & Raftery, A. E. (2007). "Probabilistic Forecasts, Calibration and Sharpness." *Journal of the Royal Statistical Society: Series B*, 69(2), 243–268.
>    원문: https://sites.stat.washington.edu/raftery/Research/PDF/Gneiting2007jrssb.pdf (저자 홈페이지 공개 PDF)
> (HAL 미러 hal-00363242는 접근 차단(Anubis anti-bot)으로 대신 저자 홈페이지 원문 사용)

---

## 1. CRPS (Continuous Ranked Probability Score)

### 1.1 정의 (Gneiting & Raftery 2007, JASA, 식 (20), p.367)

예측 CDF를 F, 실현값을 x라 할 때,

> CRPS(F, x) = −∫_{−∞}^{∞} (F(y) − 𝟙{y ≥ x})² dy  (원문 식 (20))

원문은 이를 "corresponds to the integral of the Brier scores for the associated binary probability forecasts at all real-valued thresholds (Matheson and Winkler 1976; Hersbach 2000)"라고 설명 — 즉 모든 실수 임계값에서의 Brier Score를 적분한 것.

### 1.2 계산 가능한 폐형식 (closed-form) — 원문 식 (21), p.367

> "the integral often can be evaluated in closed form. By lemma 2.2 of Baringhaus and Franz (2004) or identity (17) of Székely and Rizzo (2005),"
> CRPS(F, x) = ½ E_F|X − X'| − E_F|X − x|  (식 (21))

여기서 X, X'는 분포 F를 따르는 독립적인 두 확률변수. 이는 **샘플 기반 추정**(예: TSFM이 확률적 궤적 샘플을 다수 출력하는 경우)에 직접 적용 가능한 형태 — 샘플 집합으로 E|X−X'|와 E|X−x|를 경험적으로 근사하면 됨.

정규분포 예측인 경우 폐형식(원문 p.367):
> CRPS(N(μ,σ²), x) = σ [ 1/√π − 2φ((x−μ)/σ) − (x−μ)/σ · (2Φ((x−μ)/σ) − 1) ]
(φ, Φ는 표준정규 pdf/cdf)

**샘플 기반 계산 복잡도**: "If the predictive distribution takes the form of a sample of size n, then the right side of (20) can be evaluated in terms of the respective order statistics in a total of O(n log n) operations (Hersbach 2000, sec. 4.b)." — 순서통계량 이용 시 O(n log n).

**부호(orientation) 관례**: 원문은 CRPS를 "positively oriented" 점수 체계 안에서 음(−) 부호로 정의하지만, "typically used in negative orientation, say CRPS*(F,x) = −CRPS(F,x)" 이라고 명시(p.367). 음의 orientation에서:
> CRPS*(F, x) = E_F|X − x| − ½ E_F|X − X'|
이 형태는 "reports in the same unit as the observations, and generalizes the absolute error to which it reduces if F is a deterministic forecast" — 점 예측의 MAE를 확률 예측으로 일반화한 지표라는 뜻. **실무에서 낮을수록 좋은 지표로 쓰이는 CRPS는 이 negative-orientation 버전**이다.

### 1.3 분위수 기반(quantile-based) 정의 — pinball loss 적분

WebSearch로 확인된 표준 정의(다수의 2차 문헌에서 일관되게 제시, 원 출처는 Laio & Tamea 2007 및 Gneiting & Ranjan 2011 계열로 추정 — **1차 원문 직접 대조는 이번 조사에서 완료하지 못함, 확인 불가로 표시**):
CRPS(F⁻¹, x) = ∫₀¹ 2·Λ_α(F⁻¹(α), x) dα, 여기서 Λ_α(q,x) = (α − 𝟙{x<q})(x−q)는 분위수(pinball) 손실.
→ **[3단계 검증에서 한정 수정]**: "원문은 식 (21)의 절대오차 기댓값 형태만 명시"라는 서술은 부정확 — 원문에는 **식 (41) pinball(tick/check) loss**, **식 (48) 분위수 점수 적분 일반형**, **식 (49) CRPS = Brier 점수의 Lebesgue 적분**이 모두 존재한다. 다만 위에 제시한 정확한 등식 "CRPS = 2∫Λ_α dα" 그 형태 자체가 원문에 축자적으로 있는 것은 아니다 — 이 한 가지 등식만 "확인 불가"로 한정해야 하며, pinball loss·분위수 적분과 CRPS의 연결 자체는 원문에 풍부하게 존재한다. Gneiting & Raftery는 대신 Section 6에서 **분위수 예측을 위한 proper scoring rule** 일반형(식 (40),(42))과 그 특수사례인 **interval score**(식 (43))를 다룬다 (아래 3절 참조). 분위수-CRPS 등가성을 논문에 인용할 때는 별도로 Laio & Tamea (2007) 또는 Gneiting & Ranjan (2011) "Comparing Density Forecasts Using Threshold- and Quantile-Weighted Scoring Rules"를 직접 대조할 것을 권고.

### 1.4 CRPS의 이론적 위치 — Energy Score의 특수사례 (원문 §4.3, 식 (22), p.367)

CRPS는 원문에서 더 일반적인 **Energy Score** ES(P,x) = ½ E‖X−X'‖^β − E‖X−x‖^β (β∈(0,2))의 β=1, m=1(1차원) 특수사례로 도입된다: "This generalizes the CRPS, to which (22) reduces when β=1 and m=1." 다차원 확률예측(예: 다중 자산 동시 예측)으로 확장할 때 Energy Score가 후속 지표로 논문에 언급할 가치가 있음.

---

## 2. Proper Scoring Rule 이론 (Gneiting & Raftery 2007, JASA)

### 2.1 핵심 정의 (원문 p.360, §1)

> "Suppose... the forecaster's best judgment is the distributional forecast Q. The forecaster has no incentive to predict any P ≠ Q and is encouraged to quote his or her true belief, P = Q, if S(Q,Q) ≥ S(P,Q) with equality if and only if P = Q. A scoring rule with this property is said to be **strictly proper**. If S(Q,Q) ≥ S(P,Q) for all P and Q, then the scoring rule is said to be **proper**."

즉:
- **Proper**: S(Q,Q) ≥ S(P,Q) (모든 P, Q에 대해) — 진짜 믿음을 보고하는 것이 기대 점수를 최대화(또는 동률).
- **Strictly proper**: 위 부등식이 등호 성립 시에만 P=Q — 진짜 믿음 보고가 **유일한** 최적 전략.

원문 §2.1 Definition/식 (1) (p.361): "The scoring rule S is proper relative to P if S(Q,Q) ≥ S(P,Q) for all P,Q ∈ P. (1) It is strictly proper relative to P if (1) holds with equality if and only if P = Q, thereby encouraging honest quotes by the forecaster."

### 2.2 왜 중요한가 — 원문의 두 가지 용도 (p.360)

1. **예측 문제(prediction)**: "In terms of elicitation, the role of scoring rules is to encourage the assessor to make careful assessments and to be honest." → 부적절한(improper) 점수 규칙을 쓰면 예측자가 자신의 진짜 불확실성을 왜곡 보고할 유인이 생김.
2. **추정 문제(estimation)**: "strictly proper scoring rules provide attractive loss and utility functions that can be tailored to the problem at hand." 표본 X₁,...,Xₙ에 파라메트릭 모델 P_θ를 적합할 때, 평균 점수 S_n(θ) = (1/n)Σ S(P_θ, X_i)를 최대화하는 **optimum score estimator** θ̂ₙ = argmax_θ S_n(θ)를 정의할 수 있고, "arg maxθ Sn(θ) → θ0 as n → ∞" (θ₀가 참값이면 일치추정량). 최대우도추정(MLE)은 이 optimum score estimation의 특수사례(로그점수 사용 시)이며, 이는 다시 M-estimation의 특수사례.

### 2.3 특성화 정리 (Theorem 1, 원문 p.361)

Regular scoring rule S가 클래스 P에 대해 proper일 필요충분조건: convex 실함수 G가 존재하여
> S(P,ω) = G(P) − ∫G*(P,ω)dP(ω) + G*(P,ω)  (식 (5))
G*(P,·)는 G의 P에서의 subtangent. **strictly proper ↔ G가 strictly convex**로 대응. 여기서 G(P) = S(P,P)는 "information measure" 또는 "generalized entropy function"으로 불리며 (식 (6)), 이로부터 파생되는 divergence function d(P,Q) = S(Q,Q) − S(P,Q) (식 (7))는 strictly proper일 때 P≠Q에서 항상 양수.

### 2.4 CRPS는 proper인가 — 원문 명시 (p.367)

> "The CRPS is proper relative to the class P and **strictly proper relative to the subclass P₁ of the Borel probability measures that have finite first moment**."

즉 **1차 모멘트가 유한한 분포 클래스 안에서만 strictly proper** — 무한분산·무거운 꼬리 분포(금융수익률에서 흔함)라도 1차 모멘트만 유한하면 strict propriety는 유지됨. 이는 우리 연구에서 student-t/파레토형 합성 데이터로 진단할 때 이론적 정당성의 근거가 될 수 있음.

### 2.5 구간/분위수 예측을 위한 proper scoring rule — Interval Score (원문 §6.2, 식 (43), p.371)

중심 (1−α)×100% 예측구간 [l,u]에 대한 negatively-oriented interval score:

> S^int_α(l,u;x) = (u−l) + (2/α)(l−x)𝟙{x<l} + (2/α)(x−u)𝟙{x>u}  (식 (43))

해석: 구간이 좁을수록 보상, 관측값이 구간을 벗어나면 α에 반비례하는 크기의 벌점 부과. 원문은 이 지표가 proper함을 증명하고(Corollary 1의 특수사례), 특히 다음 문장이 우리 연구에 직접적으로 관련:

> "We anticipate novel applications, **particularly for the evaluation of volatility forecasts in computational finance.**" (원문 §6.2, **p.370** [3단계 검증에서 정정: p.371 아님])

→ Gneiting & Raftery(2007) 저자들이 **금융 변동성 예측 평가에 interval score를 명시적으로 제안**한 대목. 다만 이 문장이 가리키는 지표는 CRPS가 아니라 **interval score**임을 명확히 할 것(오귀속 주의). 우리 연구(TSFM의 금융 시계열 불확실성 추정 평가)의 방법론적 정당성을 뒷받침하는 직접 인용 가능 문장.

**[3단계 검증에서 신규 확보]** 같은 논문 **§10 결론부(p.376)**에 CRPS를 포함한 proper scoring rule 전반에 대한 두 번째 관련 문장이 있음: "we see a wealth of potential applications **in computational finance**." 이쪽이 오히려 CRPS 인용에는 더 적합한 근거(interval score 한정이 아니라 scoring rule 전반을 가리킴).

---

## 3. PIT (Probability Integral Transform) — Gneiting, Balabdaoui & Raftery (2007), JRSS-B

### 3.1 정의 (원문 §1, p.245 및 §3.1, p.251-252)

예측 CDF F_t, 실현값 x_t가 주어졌을 때,
> p_t = F_t(x_t)   (원문 식 (2))

"The literature usually refers to Rosenblatt (1952), although the PIT can be traced back at least to Pearson (1933)." 원문은 "If the forecasts are ideal and F_t is continuous, then p_t has a uniform distribution. Hence, the uniformity of the PIT is a necessary condition for the forecaster to be ideal."

### 3.2 필요조건이지 충분조건이 아님 — Hamill(2001)의 반례 (원문 §1, p.245-246, 매우 중요)

원문이 강조하는 핵심 함정: "Hamill (2001) gave a thought-provoking example of a forecaster for whom the histogram of the PIT values is essentially uniform, **even though every single probabilistic forecast is biased**." 시뮬레이션 4종 예측자(ideal / climatological / unfocused / Hamill's — 모두 표 1에 정의됨) 전부 PIT 히스토그램이 "essentially uniform"하게 나옴에도 불구하고 climatological·unfocused·Hamill's 예측자는 실제로는 결함이 있는 예측자다. 원문 결론:

> "the ideal forecaster is preferred by all users, regardless of the respective loss function. Nevertheless, **the PIT cannot distinguish between the ideal forecaster and her competitors**."

→ 이 때문에 저자들은 **PIT만으로는 부족**하며 "sharpness를 calibration 제약 하에서 최대화"하는 패러다임(sharpness diagram, marginal calibration plot, proper scoring rule 병행)을 제안함. **우리 연구에서 "캘리브레이션 붕괴"를 PIT 하나로만 판정하면 이 함정에 빠질 위험이 있음 — 반드시 CRPS(sharpness 포함 지표)와 병행해야 함.**

### 3.3 캘리브레이션의 3가지 유형 (원문 §2, p.250 부근)

원문은 probabilistic calibration(PIT 균등성과 본질적으로 동치), exceedance calibration, marginal calibration을 구분하고, 셋 모두 만족하면 "strongly calibrated"라 정의(원문: "The sequence (Ft) is strongly calibrated relative to (Gt) if it is probabilistically calibrated, exceedance calibrated and marginally calibrated."). 이 중 marginal calibration은 "장기 평균 예측분포와 장기 관측분포(기후치)가 일치하는지"를 보는 것으로, PIT 균등성과는 별개의 진단.

### 3.4 PIT 히스토그램 형태별 해석 (원문 §3.1, p.252, 실무적으로 가장 자주 인용되는 문장)

> "Hump-shaped histograms indicate **overdispersed** predictive distributions with prediction intervals that are too wide on average. **U-shaped histograms** often correspond to predictive distributions that are **too narrow**. **Triangle-shaped histograms** are seen when the predictive distributions are **biased**."

- 산 모양(hump) → 과대분산(overdispersion) → 예측구간이 실제보다 넓음
- U자형 → 과소분산(underdispersion) → 예측구간이 실제보다 좁음 (TSFM의 "과신"을 의심할 때 가장 흔히 보게 될 형태로 예상)
- 삼각형(단조증가/감소) → 체계적 편향(bias)

권장 빈 개수: "10 or 20 histogram bins generally seem adequate" (p.252).

### 3.5 앙상블 기반 예측의 PIT 대응물 — Rank Histogram / Talagrand Diagram (원문 §3.1, p.252)

TSFM이 포인트 예측이 아니라 샘플 앙상블(예: Chronos의 다중 샘플 궤적)을 출력하는 경우 적용 가능한 방법: "find the rank of the observation when pooled within the ordered ensemble values and plot the histogram of the ranks... this technique is seen to be **analogous to plotting a PIT histogram**." — CDF를 앙상블의 경험적 CDF로 대체하면 PIT 히스토그램과 동일한 논리로 해석 가능.

### 3.6 자기상관 체크 (시계열 특유의 추가 진단, 원문 §3.1, p.252-253)

시계열 k-step-ahead 예측의 PIT는 최대 (k−1)-dependent이어야 하며, 이는 "PIT 값과 그 모멘트들의 표본자기상관함수(sample autocorrelation function)를 플롯"하여 경험적으로 검증 가능(원문: "this assumption can be checked empirically, by plotting the sample autocorrelation functions for the PIT values and their moments (Diebold et al., 1998)"). 원문 Fig.4–6에서 실제 사례(풍속 예측) 제시. → 우리 연구에서 다중 horizon 예측 시 PIT의 시간적 독립성 검정에 활용 가능.

---

## 4. 구간 커버리지(Interval Coverage)

### 4.1 원문에서의 취급 — PIT 히스토그램에서 직접 도출 가능 (원문 p.252, Table 3)

원문은 커버리지를 별도 지표로 취급하지 않고 **PIT 히스토그램의 부분합**으로부터 얻을 수 있음을 명시:
> "Table 3 shows the empirical coverage of the associated central 50% and 90% prediction intervals. **This information is redundant, since the empirical coverage can be read off the PIT histogram**, as the area under the 10 and 18 central bins respectively [20-bin 히스토그램 기준]."

시뮬레이션 결과 예시(원문 Table 3, 명목 50%/90% 대비 실제 커버리지):
| 예측자 | 50% 구간 실측 커버리지 | 90% 구간 실측 커버리지 |
|---|---|---|
| Ideal | 51.2% | 90.0% |
| Climatological | 51.3% | 90.7% |
| Unfocused | 50.1% | 90.1% |
| Hamill's | 50.9% | 89.5% |

주목할 점: 이 4개 예측자는 품질이 크게 다름(ideal만 진짜 좋음)에도 커버리지 수치가 전부 명목값에 가깝다 — §3.2의 PIT 함정과 동일한 문제가 커버리지 지표에도 적용됨. **커버리지가 명목값에 가까워도 예측이 좋다는 보장은 없음(sharpness 없이는 무의미).**

### 4.2 Interval Score와의 결합 — **[3단계 검증에서 정정]** 두 개의 별개 사례연구를 정확히 구분해야 함

**정정 전 오류**: 원 요약은 인용문 `"...by combining width and coverage"`를 §6.3(p.371-373)에 귀속시켰으나, 이는 **원문에 없는 문장**이었다. 실제 원문 문장은 다음과 같고, 위치도 **§8.3(p.374)**이다:
> "...by rewarding narrow prediction intervals and penalizing intervals missed by the observation" (원문 §8.3, p.374)

두 사례연구는 서로 다르다:
- **§6.3 (p.371-373)**: bilinear process 시뮬레이션 사례. 구간 [l,u]를 조정하며 interval score 거동 관찰.
- **§8.3 (p.374)**: 기상 앙상블 예측 사례. ensemble inflation factor **r**을 조정하며 "Clearly, the coverage increases with r... which confirms the underdispersive character of the ensemble" — 커버리지 미달이 **과소분산(underdispersion)의 직접적 증거**로 해석됨. 이 관찰의 정확한 출처는 §8.3이며 §6.3이 아니다.

원문은 커버리지 단독이 아니라 **interval score(식 (43), 위 2.5절)와 함께** 봐야 한다는 취지는 유지되나, 인용 시 반드시 §8.3을 정확한 출처로 표기할 것.

---

## 5. 캘리브레이션 진단법 종합 (원문 종합, §5 Discussion, p.266)

원문 결론부(§5)의 요지:
> "Our own applied work... has benefited immensely from these tools... If we were to reduce our conclusions to a single recommendation, **we would close with a call for the assessment of sharpness, particularly when the goal is that of ranking.** Previous comparative studies of the predictive performance of probabilistic forecasts have focused on calibration [only]."

즉 저자들의 최종 권고는 **"캘리브레이션만 보지 말고 반드시 sharpness도 함께 평가하라"**. 이유: 캘리브레이션(넓게는 PIT/커버리지)만으로는 "climatological forecaster"(항상 넓은 무정보 예측)처럼 캘리브레이션은 완벽하지만 쓸모없는 예측을 걸러내지 못함 — 반대로 sharp하지만 miscalibrated된 예측(TSFM이 과신하는 상황과 정확히 대응)도 걸러내지 못함.

원문이 제시하는 도구 세트(§3, 정리):
1. PIT 히스토그램 / rank histogram — probabilistic calibration
2. Marginal calibration plot — 장기 예측분포 vs 장기 관측분포(기후치) 일치
3. Sharpness diagram — 예측분포의 폭(농도) 그 자체를 시각화
4. Proper scoring rule (CRPS, interval score 등) — calibration과 sharpness를 하나의 스칼라로 동시에 반영, 랭킹에 사용

---

## 5-보강. [3단계 검증에서 추가] 원 요약에 누락됐던 핵심 근거들

1. **GBR07 Table 5 — "PIT는 구분 못 하지만 CRPS/LogS는 구분한다"의 원문 내 실증.** 4개 예측자(ideal/climatological/unfocused/Hamill's)의 PIT 히스토그램은 전부 균등해 보이지만(§3.2, Hamill 함정), LogS와 CRPS는 이 4개 예측자를 정확히 성능 순으로 순위 매김. 원 요약이 §3.2의 "함정" 이론만 서술하고 이를 뒷받침하는 정량적 표를 누락했음.
2. **GBR07 Table 4 — 커버리지는 명목값에 가까운데 평균 구간 폭은 다름.** 4개 예측자의 커버리지는 모두 명목값 근처(위 4.1절 표와 유사)이지만, 평균 구간 폭은 1.35 vs 1.91처럼 크게 다름 — "커버리지만으로는 sharpness 차이를 못 잡는다"는 §4.1절 주장의 정량 증거.
3. **CRPS가 log score보다 극단값에 더 강건함**(두 논문 모두에서 확인) — 두꺼운 꼬리를 가진 금융 데이터에서 NLL 대신 CRPS를 1차 지표로 쓰는 것을 정당화하는 근거로 직접 인용 가능.
4. **Diebold-Mariano(DM) 검정 언급** — GBR07 §4.4와 GR07 §10 양쪽에서 다뤄짐. "forecast differential의 시계열 종속성에 주의해야 한다"는 경고 포함 — 우리 연구가 다중 horizon 예측을 비교할 때 직접 적용해야 할 경고.
5. **CRPS의 임계값 분해(threshold decomposition, 식 (14)) + Candille & Talagrand의 calibration-sharpness 분해** — CRPS를 특정 임계값 구간별로 분해해 "꼬리에서 붕괴하는지 중심에서 붕괴하는지"를 진단할 수 있는 도구. 우리 연구의 "어느 금융 메커니즘이 어느 부분(꼬리/중심)의 캘리브레이션을 무너뜨리는가"라는 질문에 정확히 대응.
6. **GBR07 §5 — 저자들이 금융 선행연구를 명시적으로 비판.** "Bauwens et al. (2004)을 포함한 기존 연구들이 point accuracy와 PIT 균등성만 검토했다"고 지적하며 sharpness 평가 부재를 명시적으로 비판함. **우리 연구가 메우려는 공백(CRPS·캘리브레이션)을 원저자 권위로 직접 뒷받침하는 문장** — 인용 우선순위 최상위.

## 5-보강2. [3단계 검증에서 신규 발견] FinStressTS의 CRPS 구현에서 발견된 방법론적 결함

`01_자료원문/2606.03184_FinStressTS_Synthetic_Benchmark.md` 대조 결과:
- FinStressTS의 샘플 기반 CRPS 추정량(식 (5))이 **`1/(2S²)`를 사용해 편향 추정량**임을 확인. Gneiting & Raftery 식 (21)의 불편(unbiased) 추정량은 `1/(S(S−1))` 형태여야 함. `1/(2S²)`를 쓰면 E|X−X'| 항을 체계적으로 과소평가해 **CRPS를 과대평가**하며, 모델마다 샘플 수 S가 다르면 비교 자체가 오염됨. **우리 실험에서 CRPS 추정량을 직접 구현할 때 반드시 불편 추정량을 사용해야 함 — 명시적 설계 원칙으로 채택.**
- FinStressTS는 **PIT·구간 커버리지·interval score를 전혀 쓰지 않고 CRPS(및 CRPS_sum) 스칼라만 보고**함. "predictive intervals/calibration이 견고한가"를 연구 동기로 내세우면서도 실제로는 캘리브레이션 진단 도구를 하나도 쓰지 않은 것 — 우리 논문이 "CRPS 스칼라 하나로는 부족하고 PIT+커버리지+interval score를 병행해야 한다"고 주장할 때 FinStressTS를 정확히 반례로 인용할 수 있음(진행상황.md의 차별점 표와 직접 연결).

---

## 6. 종합 소견 — 우리 연구에서 "캘리브레이션 붕괴"를 정량화할 지표 조합 제안

**첫째**, Gneiting-Raftery 프레임워크가 명시적으로 경고하는 함정(§3.2, Hamill 2001 반례)을 피하려면 **PIT 균등성 단독 판정을 캘리브레이션 붕괴의 유일한 증거로 쓰면 안 된다.** PIT가 uniform하게 보여도 예측이 나쁠 수 있다는 것이 원 논문의 핵심 메시지이기 때문이다. 대신 다음 3층 구조를 제안한다: (1) CRPS(negative-orientation, 식 (21) 기반 샘플 추정)를 1차 스칼라 랭킹 지표로 사용 — 이는 calibration과 sharpness를 동시에 반영하는 strictly proper scoring rule이므로 "TSFM이 자기 불확실성을 정확히 아는가"를 하나의 숫자로 요약하기에 이론적으로 가장 방어 가능하다. (2) PIT 히스토그램(20-bin 권장, 원문 p.252)을 진단 도구로 병행하되, U자형/산자형/삼각형 형태 분류(원문 p.252 기준)로 "과소분산/과대분산/편향"을 구분해 어떤 금융 메커니즘(변동성 군집, 두꺼운 꼬리, 체제전환 등)이 어떤 유형의 붕괴를 유발하는지 매핑한다. (3) 명목 대비 실측 구간 커버리지(50%, 90% 등 복수 신뢰수준)를 PIT 히스토그램의 부분합(원문 Table 3 방식)으로 함께 보고하되, 반드시 interval score(식 (43))와 짝지어 "좁은 구간+낮은 커버리지"와 "넓은 구간+높은 커버리지"를 구분한다 — 커버리지 숫자만으로는 sharpness 없이 해석이 무의미하다는 것이 원문의 명시적 경고다.

**둘째**, 파라메트릭 합성 진단이라는 우리 연구의 설계상 강점을 활용해, Gneiting-Raftery가 제안하되 실증하지 못한 지점을 메울 수 있다. 원문은 정규분포·시뮬레이션 예측자 비교에서 PIT 함정을 보였지만, 우리는 금융 특유의 성질(자기상관, 변동성 군집, 두꺼운 꼬리, 체제전환)을 하나씩 독립적으로 조절하며 "어느 축을 켰을 때 CRPS는 나빠지는데 PIT는 여전히 균등해 보이는가"라는 식으로 **원 논문의 이론적 경고를 정량적으로 재현·확장**할 수 있다. 이는 문헌상 공백(진행상황.md에서 이미 확인된 "CRPS·캘리브레이션 축은 4편 선행연구 전부 공백")과도 정확히 맞물린다.

**셋째**, 실무적 계산 이슈로, TSFM(Chronos, TimesFM, Moirai 등)은 대개 분위수 또는 샘플 궤적 형태로 확률 예측을 출력하므로, CRPS는 원문 식 (21)의 E|X−X'| − E|X−x| 형태(샘플 기반, O(n log n))로 계산하는 것이 가장 자연스럽다. 다만 이번 조사에서 "분위수 손실(pinball loss)의 적분으로서의 CRPS 등가식"은 2차 문헌에서는 일관되게 확인되었으나 Gneiting & Raftery (2007) 원문 안에서 그 정확한 형태를 직접 대조하지 못했다 — 방법론 섹션 집필 전 Gneiting & Ranjan (2011) 또는 Laio & Tamea (2007) 원문을 별도로 확인할 것을 권고한다. 또한 `gluonts` 라이브러리(진행상황.md 도구 목록에 이미 포함)가 CRPS를 내장 제공하므로 구현 단계에서는 이를 우선 활용하되, 계산 방식이 원문 식 (21)과 일치하는지(적분 근사 vs 폐형식) 문서를 대조해야 한다.

---

## 확인 불가 / 후속 확인 필요 항목

1. **분위수(pinball loss) 적분으로서의 CRPS 등가식** — 2차 문헌 다수에서 일관 인용되나 Gneiting & Raftery(2007) 원문 내 정확한 위치를 이번 조사에서 대조하지 못함. Gneiting & Ranjan (2011) 원문 확인 필요.
2. **HAL 미러(hal-00363242)** — anti-bot(Anubis) 차단으로 접근 불가. 대신 저자 홈페이지(stat.washington.edu) 공개 PDF로 대체 확인 완료(내용은 JRSS-B 정식본과 동일한 것으로 판단되나, 페이지 매김이 저널 판과 정확히 일치하는지는 별도 대조 필요 — 원문 자체에 "252", "253" 등 저널 페이지 번호가 본문에 포함되어 있어 정식본 사본으로 판단됨).
3. **gluonts의 CRPS 구현 세부사항**(적분 근사 방식, 분위수 기반인지 샘플 기반인지)은 이번 조사 범위 밖 — 5단계 구현 착수 시 별도 확인 필요.
