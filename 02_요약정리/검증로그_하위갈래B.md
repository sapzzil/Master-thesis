# 검증로그 — 하위갈래 B (확률예측 평가론)

> 검증일: 2026-08-15
> 검증 대상: `02_요약정리/하위갈래B_확률예측_평가론.md`
> 대조 원문(로컬 사본):
> - `01_자료원문/GneitingRaftery2007_JASA_ScoringRules.md` (이하 **GR07**)
> - `01_자료원문/GneitingBalabdaouiRaftery2007_JRSSB_CalibrationSharpness.md` (이하 **GBR07**)
> - `01_자료원문/2606.03184_FinStressTS_Synthetic_Benchmark.md` (이하 **FinStressTS**)
> 검증자: 요약 작성자와 독립된 별도 에이전트. 원문 텍스트에 존재하지 않는 내용은 "원문에 없음"으로 명시함.
>
> **페이지 번호 판정 방법**: 두 원문 사본 모두 러닝 헤드(예: `370 Journal of the American Statistical Association, March 2007`, `Probability Forecasts 253`)가 각 페이지 시작 지점에 그대로 추출되어 있어, 헤드 사이 구간으로 페이지를 확정했다. 아래 "실제 페이지"는 이 기준이다.

---

## 0. 총평 (먼저 읽을 것)

- **핵심 인용 근거(“computational finance 변동성 예측” 문장)는 원문에 실재한다.** 문장 자체는 요약과 한 글자도 다르지 않다. 다만 **페이지가 p.371이 아니라 p.370**이며, 대상 지표는 **interval score**(CRPS 아님)이다. 요약 본문은 이 점을 이미 정확히 서술하고 있으므로 인용 자체는 안전하다.
- **중대 오류 1건 발견**: 요약 §4.2의 인용문 `"This scoring rule assesses both calibration and sharpness, by combining width and coverage."` 는 **원문에 존재하지 않는 문장**이다(원문 표현이 다름). 게다가 출처를 §6.3(p.371–373)로 적었으나 실제로는 **§8.3(p.374)** 의 전혀 다른 사례연구다. 반드시 수정 필요.
- **중대 오류 2건 발견**: 요약 §1.3과 「확인 불가 항목 1」이 “원문은 식 (21)의 절대오차 기댓값 형태만 명시”라고 단정했으나, **GR07 §6.4 식 (48)·(49)가 분위수 점수/Brier 점수의 적분으로 CRPS를 구성하는 방식을 명시**하고 있고, **식 (41)이 곧 pinball(tick/check) loss** 로 원문에 등장한다. “원문에 없다”는 서술은 부정확.
- **누락 다수**: Diebold–Mariano 계열 검정, CRPS의 Brier 적분 분해(GBR07 식 (14))·prediction error curve, GBR07 Table 4(평균 폭)·Table 5(LogS/CRPS 순위), GR07 §8.2의 “CRPS가 로그점수보다 극단값에 덜 민감” 문장, GR07 §10의 두 번째 computational finance 문장, 다변량 CRPS(§6.4). 특히 앞의 세 개는 우리 논문 주장의 **가장 강한 직접 증거**인데 요약에 빠져 있다.
- **페이지 표기 오차가 전반적으로 ±1 수준으로 산재**. 인용 신뢰도에 직접 영향을 주므로 일괄 교정 권고.

---

## 1. CRPS 정의·수식 대조

### 1-1. 식 (20) 정의 — **정확**
요약 §1.1 (p.367). 원문 그대로:

> "The continuous ranked probability score (CRPS) is defined as
> CRPS(F, x) = − ∫_{−∞}^{∞} (F(y) − 1{y ≥ x})² dy (20)
> and corresponds to the integral of the Brier scores for the associated binary probability forecasts at all real-valued thresholds (Matheson and Winkler 1976; Hersbach 2000)."
> — GR07, §4.2, 실제 p.367 ✔ (요약 표기와 일치)

**판정: 정확.** 수식·부호(음수 orientation)·Brier 적분 해석 모두 일치.

### 1-2. 식 (21) 폐형식 — **정확**
> "However, the integral often can be evaluated in closed form. By lemma 2.2 of Baringhaus and Franz (2004) or identity (17) of Székely and Rizzo (2005),
> CRPS(F, x) = ½ E_F|X − X′| − E_F|X − x|, (21)
> where X and X′ are independent copies of a random variable with distribution function F and finite first moment."
> — GR07 p.367

**판정: 정확.** 단, 요약은 `X, X'는 분포 F를 따르는 독립적인 두 확률변수`라고만 적고 **"and finite first moment"** 조건을 이 지점에서 누락했다(§2.4에서 별도로 언급하긴 함). 식 (21) 자체의 성립 조건이므로 §1.2에 병기 권고.

### 1-3. 정규분포 폐형식 — **정확**
원문:
> "CRPS(N(µ,σ²), x) = σ [ 1/√π − 2ϕ((x−µ)/σ) − (x−µ)/σ (2Φ((x−µ)/σ) − 1) ]" — GR07 p.367

**판정: 정확.** 요약의 전개와 동일.

### 1-4. O(n log n) 문장 — **정확(단, 배치 위치가 오해 소지)**
원문 그대로:
> "If the predictive distribution takes the form of a sample of size n, then the right side of (20) can be evaluated in terms of the respective order statistics in a total of O(n log n) operations (Hersbach 2000, sec. 4.b)." — GR07 p.367

**판정: 인용문은 정확.** 다만 원문은 **"the right side of (20)"**(적분형)이라고 명시하는데, 요약은 이 문장을 §1.2 "폐형식 (21)" 항목 아래에 넣어 마치 (21)의 계산복잡도인 것처럼 읽힌다. 원문 문언대로 (20) 기준임을 밝힐 것.

### 1-5. 음의 orientation — **정확**
> "It is typically used in negative orientation, say CRPS∗(F, x) = −CRPS(F, x). The representation (21) then can be written as CRPS∗(F, x) = E_F|X − x| − ½ E_F|X − X′|, which sheds new light on the score. In negative orientation, the CRPS can be reported in the same unit as the observations, and it generalizes the absolute error to which it reduces if F is a deterministic forecast—that is, a point measure." — GR07 p.367

**판정: 정확.** 요약이 `"reports in the same unit as the observations, and generalizes the absolute error to which it reduces if F is a deterministic forecast"` 로 축약 인용했는데, 원문은 `can be reported`이다. **직접 인용 부호 안의 어형이 원문과 다르므로** 논문에 큰따옴표로 옮길 때는 원문 어형을 쓸 것.

### 1-6. Energy Score 특수사례 — **정확**
> "This generalizes the CRPS, to which (22) reduces when β = 1 and m = 1, by allowing for an index β ∈ (0, 2) and applying to distributional forecasts of a vector-valued quantity in R^m." — GR07 §4.3, 실제 p.367

**판정: 정확.**

### 1-7. **pinball loss / 분위수 적분 표현 — 요약의 "원문에 없음" 판정이 부정확 (신규확인)**

요약 §1.3 및 「확인 불가 항목 1」은 "원문은 식 (21)의 절대오차 기댓값 형태만 명시"라고 했으나, GR07 원문에는 다음이 **모두 존재**한다.

(a) **pinball loss가 원문에 명시적으로 등장** (§6.1, 실제 p.370):
> "If s(x) = x and h(x) = −αx, then we obtain the scoring rule
> S(r; x) = (x − r)(1{x ≤ r} − α), (41)
> which has been proposed by Koenker and Machado (1999), Taylor (1999), Giacomini and Komunjer (2005), Theis (2005, p. 232), and Friederichs and Hense (2006) for measuring in-sample goodness of fit and out-of-sample forecast performance in meteorological and financial applications. In negative orientation, the econometric literature refers to the scoring rule (41) as the tick or check loss function."

(b) **분위수 점수의 적분으로 예측분포용 점수를 구성하는 일반형** (§6.4, 실제 p.371):
> "Specifically, if S_α denotes a proper scoring rule for the quantile at level α and ν is a Borel measure on (0, 1), then the scoring rule
> S(F, x) = ∫₀¹ S_α(F⁻¹(α); x) ν(dα) (48)
> is proper, subject to regularity and integrability constraints."

(c) **CRPS를 Brier 점수의 Lebesgue 적분으로 명시** (§6.4, p.371):
> "S(F, x) = ∫_{−∞}^{∞} S(F(y), 1{x ≤ y}) ν(dy) (49) is proper... The CRPS (20) corresponds to the special case in (49) in which S is the quadratic or Brier score and ν is the Lebesgue measure. If S is the Brier score and ν is a sum of point measures, then the ranked probability score (Epstein 1969) emerges."

(d) **다변량 CRPS** (§6.4, p.371):
> "A multivariate analog of the CRPS can be defined as CRPS(F, x) = −∫_{R^m} (F(y) − 1{x ≤ y})² ν(dy). This is a weighted integral of the Brier scores at all m-variate thresholds."

**판정: 부정확(요약의 부정 서술이 과함) + 신규확인.**
정확한 사실관계는: 원문은 **"CRPS = 2∫₀¹ Λ_α dα" 라는 그 정확한 등식을 명시하지는 않지만**, ① pinball loss 자체(식 41), ② 분위수 점수를 α에 대해 적분해 분포용 proper score를 만드는 일반 구성(식 48), ③ CRPS = Brier 점수의 임계값 적분(식 49)을 모두 담고 있다. 즉 “분위수-CRPS 등가성의 재료”는 원문 안에 있다. 요약처럼 “원문은 (21)만 명시”라고 쓰면 심사에서 반박당할 수 있다.

### 1-8. GBR07의 CRPS 정의 — **요약에서 완전 누락 (신규확인)**
GBR07 §3.4(실제 p.256)는 **양(penalty) orientation** 으로 CRPS를 별도 정의한다:
> "crps(F, x) = ∫_{−∞}^{∞} {F(y) − 1(y ≥ x)}² dy (12)"
> "crps(F, x) = E_F|X − x| − ½ E_F|X − X′|, (13) where X and X′ are independent copies of a random variable with CDF F and finite first moment. The representation (13) is particularly convenient when F is represented by a sample, possibly based on Markov chain Monte Carlo output or forecast ensembles (Gschlößl and Czado, 2005)."

**의의**: “샘플로 표현된 F에 (13)이 특히 편리하다”는 문장은 **TSFM이 샘플 궤적을 출력하는 우리 설정에 그대로 대응하는 1차 근거**다. 요약 §6-셋째의 주장을 뒷받침하는 가장 직접적인 문장인데 빠져 있다. 추가 권고.

---

## 2. Proper Scoring Rule 이론 대조

| 요약 항목 | 판정 | 근거 |
|---|---|---|
| §2.1 "Suppose... strictly proper / proper" 인용 | **내용 정확 / 페이지 오류** | 원문 해당 문단은 GR07 **p.359**(러닝헤드 `359` 직전). 요약은 p.360으로 표기. |
| §2.1 식 (1) "S is proper relative to P if S(Q,Q) ≥ S(P,Q) for all P,Q ∈ P. (1) It is strictly proper relative to P if (1) holds with equality if and only if P = Q, thereby encouraging honest quotes by the forecaster." | **정확 / 페이지 오류** | 실제 **p.360**. 요약은 p.361로 표기. |
| §2.2 "In terms of elicitation, the role of scoring rules is to encourage the assessor to make careful assessments and to be honest" | **정확 / 페이지 오류** | 실제 **p.359**. 요약은 p.360. 원문은 뒤에 `(Garthwaite, Kadane, and O'Hagan 2005)` 출처 표기가 붙음. |
| §2.2 optimum score estimator, `arg maxθ Sn(θ) → θ0 as n → ∞`, MLE는 특수사례, M-estimation의 특수사례 | **정확** | GR07 p.360 및 §9.1 p.374–375에서 반복. |
| §2.3 Theorem 1 / 식 (5)(6)(7), strictly proper ↔ strictly convex, divergence d(P,Q)=S(Q,Q)−S(P,Q) | **정확** | GR07 p.361. `"The divergence function is nonnegative, and if S is strictly proper, then d(P,Q) is strictly positive, unless P = Q."` |
| §2.4 "The CRPS is proper relative to the class P and strictly proper relative to the subclass P₁ of the Borel probability measures that have finite first moment." | **정확(축자 일치)** | GR07 p.367. |
| §2.4 해석: "무한분산·두꺼운 꼬리라도 1차 모멘트만 유한하면 strict propriety 유지" | **논리적으로 타당하나 경고 필요** | 원문은 조건만 진술. **1차 모멘트가 발산하는 경우(예: α-stable α≤1, Cauchy)는 strict propriety도, 식 (21)의 표현도 성립하지 않음**을 반드시 병기할 것. 합성 데이터에서 자유도 ν≤1 student-t를 쓰면 실제로 위반된다. |
| §2.5 interval score 식 (43) | **수식 정확 / 페이지 오류(§ 표기는 정확)** | 실제 **p.370**(요약은 p.371). 원문: `S^int_α(l, u; x) = (u − l) + (2/α)(l − x)1{x < l} + (2/α)(x − u)1{x > u}. (43)` |
| §2.5 "원문은 이 지표가 proper함을 증명하고(Corollary 1의 특수사례)" | **정확** | 원문: "Putting α₁ = α/2, α₂ = 1 − α/2, s₁(x) = s₂(x) = 2x/α, and h(x) = −2x/α in (42), and reversing the sign of the scoring rule, yields the negatively oriented interval score". 또 "Hamill and Wilks (1995, p. 622) ... noted that 'a strategy for gaming [. . . ] was not obvious,' thereby conjecturing propriety, which is confirmed by the foregoing." |

---

## 3. ★핵심 검증★ "computational finance 변동성 예측" 근거 문장

### 3-1. 판정: **정확 — 원문에 실재. 축자 일치.**

원문 문장(GR07 §6.2 Interval Score 마지막 문장, 실제 **p.370**, 사본 파일 1244–1245행):

> "In the case α = ½, Hamill and Wilks (1995, p. 622) used a scoring rule that is equivalent to the interval score. They noted that "a strategy for gaming [. . . ] was not obvious," thereby conjecturing propriety, which is confirmed by the foregoing. **We anticipate novel applications, particularly for the evaluation of volatility forecasts in computational finance.**"

**맥락 정리 (엄밀히):**
1. 이 문장의 주어 "novel applications"가 가리키는 대상은 **interval score(식 43)** 이다. CRPS가 아니다.
2. 문장은 §6.2의 **마지막 문장**으로, 바로 앞에서 Hamill & Wilks(1995)가 propriety를 추측만 했던 것을 본 논문이 확정했다는 서술이 온다. 즉 "우리가 propriety를 확립했으니 새 응용을 기대한다"는 흐름.
3. 바로 다음이 §6.3 "Case Study: Interval Forecasts for a Conditionally Heteroscedastic Process"(조건부 이분산 bilinear process) — 즉 **저자들은 이 문장 직후에 곧바로 변동성(이분산) 맥락 사례연구를 배치**했다. 인용 시 이 배치를 근거로 들면 설득력이 강해진다.
4. 요약 §2.5의 서술("interval score를 명시적으로 제안한 대목")은 **정확하다.** CRPS로 오귀속하지 않았다. 다만 상위 작업지시서의 표현("CRPS류 지표를 computational finance에 제안")은 원문 근거를 넘어서므로, 논문 본문에서 그렇게 쓰면 안 된다.
5. **페이지는 p.371이 아니라 p.370.**

### 3-2. 신규확인: **같은 논문에 두 번째 computational finance 문장이 있다 (요약에 없음)**

GR07 §10 Avenues for Future Work (실제 p.376):
> "Proper scoring rules form key tools within the broader framework of diagnostic forecast evaluation (Murphy and Winkler 1992; Gneiting et al. 2006), and in addition to hydrometeorological and biomedical uses, **we see a wealth of potential applications in computational finance.**"

**의의**: 이 문장은 interval score가 아니라 **proper scoring rule 전반**(따라서 CRPS 포함)에 대한 것이다. 우리 논문이 "CRPS를 금융 시계열 평가에 쓰는 것"의 근거로 인용하려면 **§6.2 문장보다 이 §10 문장이 논리적으로 더 적합**하다. 두 문장을 함께 인용하는 것이 가장 안전하다.

### 3-3. 신규확인: 금융 관련 부수 근거 3건 (요약에 없음)

- GR07 §1 첫 문단(p.359): "probabilistic forecasting has become routine in such applications as weather and climate prediction (Palmer 2002; Gneiting and Raftery 2005), **computational finance (Duffie and Pan 1997)**, and macroeconomic forecasting".
- GR07 §6 도입부(실제 p.369): "the forecaster might quote predictive quantiles, such as **value at risk in financial applications** (Duffie and Pan 1997) or prediction intervals (Christoffersen 1998) only."
- GBR07 §1(p.243): "**the rapidly growing area of financial risk management is dedicated to probabilistic forecasts of portfolio values** (Duffie and Pan, 1997)."

---

## 4. PIT / 캘리브레이션 대조 (GBR07)

| 요약 항목 | 판정 | 비고 |
|---|---|---|
| §3.1 PIT 정의 `p_t = F_t(x_t)` 식 (2) | **정확 / 페이지 오류** | 실제 **p.244**(요약 p.245). |
| §3.1 "The literature usually refers to Rosenblatt (1952), although the PIT can be traced back at least to Pearson (1933)." | **정확(축자)** | GBR07 §3.1, 실제 p.251. |
| §3.1 "If the forecasts are ideal and F_t is continuous, then p_t has a uniform distribution. Hence, the uniformity of the PIT is a necessary condition for the forecaster to be ideal." | **정확(축자, 뒷부분 생략)** | 원문은 이어서 ", and checks for its uniformity have formed a corner-stone of forecast evaluation." GBR07 실제 **p.244**. |
| §3.2 Hamill(2001) 반례 인용 | **정확(축자) / 페이지 오류** | 원문: "Hamill (2001) gave a thought-provoking example of a forecaster for whom the histogram of the PIT values is essentially uniform, even though every single probabilistic forecast is biased." 실제 **p.244**(요약 p.245–246). |
| §3.2 "the ideal forecaster is preferred by all users, regardless of the respective loss function. Nevertheless, the PIT cannot distinguish between the ideal forecaster and her competitors." | **정확(축자)** | GBR07 실제 p.245. 원문은 앞에 "As Diebold et al. (1998) pointed out," 가 붙는다. |
| §3.2 "4종 예측자 전부 PIT 히스토그램이 essentially uniform" | **정확** | "Fig. 1 shows that the PIT histograms for the four forecasters are essentially uniform." (p.245) / "Fig. 1 employs 20 bins" (p.252). Table 1에 4 예측자 정의 확인. |
| §3.3 3가지 캘리브레이션 + strongly calibrated 정의 인용 | **정확(축자) / 페이지 오류** | Definition 1(d), 실제 **p.247**(요약 "§2, p.250 부근"). |
| §3.3 "marginal calibration = 장기 예측분포와 관측 기후치 일치" | **정확** | "marginal calibration can be interpreted in terms of the equality of observed and forecast climatology." (p.247) |
| §3.4 히스토그램 형태별 해석 인용 | **정확(축자) / 페이지 오류** | 원문: "Hump-shaped histograms indicate overdispersed predictive distributions with prediction intervals that are too wide on average. U-shaped histograms often correspond to predictive distributions that are too narrow. Triangle-shaped histograms are seen when the predictive distributions are biased." 실제 **p.253**(요약 p.252). |
| §3.4 "10 or 20 histogram bins generally seem adequate" | **정확(축자)** | 실제 p.252 ✔ |
| §3.5 rank histogram / Talagrand diagram | **정확(축자) / 페이지 오류** | "To obtain a verification rank histogram, find the rank of the observation when pooled within the ordered ensemble values and plot the histogram of the ranks. If we identify the predictive distribution with the empirical CDF of the ensemble values, this technique is seen to be analogous to plotting a PIT histogram." 실제 **p.253**(요약 p.252). 원문은 제안자로 Anderson(1996), Hamill & Colucci(1997), Talagrand et al.(1997)을 명시. |
| §3.6 PIT 자기상관 (k−1)-dependent | **정확** | "The PITs for ideal k-step-ahead forecasts are at most k − 1 dependent, and this assumption can be checked empirically, by plotting the sample autocorrelation functions for the PIT values and their moments (Diebold et al., 1998)." p.253. Fig.4–6 사례 ✔ |

### 4-1. 신규확인 — 요약이 빠뜨린 PIT 관련 도구
> "Smith (1985), Frühwirth-Schnatter (1996) and Berkowitz (2001) proposed an assessment of independence based on the transformed PIT values Φ⁻¹(p_t), which are Gaussian under the assumption of ideal forecasts. This further transformation has obvious advantages when formal tests of independence are employed and seems to make little difference otherwise." (GBR07 p.253)

→ 우리 연구가 **다중 horizon PIT 독립성을 형식 검정**하려면 이 Φ⁻¹ 변환(Berkowitz 2001) 경로가 원문이 권하는 방법이다. 요약 §3.6에 추가 권고.

또한 원문은 형식적 균등성 검정에 대해 경고한다:
> "Formal tests of uniformity can be employed... However, the use of formal tests is often hindered by complex dependence structures, particularly in cases in which the PIT values are spatially aggregated." (p.253)

---

## 5. 구간 커버리지 대조

### 5-1. §4.1 Table 3 인용 — **정확**
> "Fig. 1 employs 20 bins and shows the PIT histograms for the various forecasters in our initial simulation study. The histograms are essentially uniform. Table 3 shows the empirical coverage of the associated central 50% and 90% prediction intervals. This information is redundant, since the empirical coverage can be read off the PIT histogram, as the area under the 10 and 18 central bins respectively." — GBR07 p.252

Table 3 수치 대조: Ideal 51.2 / 90.0, Climatological 51.3 / 90.7, Unfocused 50.1 / 90.1, Hamill's 50.9 / 89.5. **요약의 표와 완전 일치. 판정: 정확.**

### 5-2. **신규확인 — 요약 §4.1 주장을 결정적으로 뒷받침하는 Table 4가 누락됨**

요약 §4.1은 "커버리지가 명목값에 가까워도 예측이 좋다는 보장은 없음(sharpness 없이는 무의미)"이라고 주장하는데, **그 증거인 원문 Table 4를 인용하지 않았다.** 원문 Table 4(GBR07 p.255, "Average width of central prediction intervals"):

| 예측자 | 50% 평균 폭 | 90% 평균 폭 |
|---|---|---|
| Ideal | 1.35 | 3.29 |
| Climatological | 1.91 | 4.65 |
| Unfocused | 1.52 | 3.68 |
| Hamill's | 1.49 | 3.62 |

원문 서술:
> "Table 4 shows the average width of the central 50% and 90% prediction intervals for the forecasters in our initial simulation study. The ideal forecaster is the sharpest, followed by Hamill's, the unfocused and the climatological forecaster." (§3.3, p.255)

→ **커버리지는 4종 모두 명목값 근처(Table 3)인데 폭은 최대 41% 차이(1.35 vs 1.91)** 라는 것이 "커버리지 단독으로는 구분 불가, sharpness가 구분한다"의 정량적 증거다. 요약 §4.1·§6-첫째에 반드시 추가할 것.

### 5-3. **신규확인 — Table 5(LogS/CRPS)가 누락됨. 우리 논문의 핵심 근거.**

GBR07 Table 5 (p.257, "Average logarithmic score LogS and continuous ranked probability score CRPS in the simulation study"):

| 예측자 | LogS | CRPS |
|---|---|---|
| Ideal | 1.41 | 0.56 |
| Climatological | 1.75 | 0.78 |
| Unfocused | 1.53 | 0.63 |
| Hamill's | 1.52 | 0.61 |

원문:
> "As expected, both scoring rules rank the ideal forecaster highest, followed by Hamill's, the unfocused and the climatological forecaster." (p.256)

→ **"PIT는 4종을 구분하지 못하지만(Fig.1) CRPS는 정확히 구분한다(Table 5)"** 가 원문 안에서 이미 실증된 것이다. 요약 §6-첫째의 "CRPS를 1차 스칼라 랭킹 지표로" 주장에 대한 가장 직접적인 근거인데 요약에 전혀 없다. **최우선 추가 권고.**

### 5-4. ★중대 오류★ §4.2 인용문 — **부정확 (원문에 없는 문장 + 출처 오귀속)**

요약 §4.2는 다음과 같이 적었다:
> 원문은 커버리지 단독이 아니라 interval score(식 (43))와 함께 봐야 한다고 강조: "This scoring rule assesses both calibration and sharpness, **by combining width and coverage**." 사례연구(조건부 이분산 과정, ensemble inflation factor r을 조정하며…) — (출처: 원문 §6.3 사례연구, p.371-373)

**원문 실제 문장 (GR07 §8.3, 실제 p.374):**
> "We assessed the interval forecasts in their dependence on the inflation factor r in two ways: by computing the empirical coverage of the prediction intervals and by computing s_α(r) = ... (58), where S^int_α denotes the negatively oriented interval score (43). **This scoring rule assesses both calibration and sharpness, by rewarding narrow prediction intervals and penalizing intervals missed by the observation.** Figure 4(a) shows the empirical coverage of the interval forecasts. **Clearly, the coverage increases with r. For α = .50 and α = .10, the nominal coverage was obtained at r = 1.78 and r = 2.11, which confirms the underdispersive character of the ensemble.** Figure 4(b) shows the interval score (58) as a function of the inflation factor r. For α = .50 and α = .10, the score was optimized at r = 1.56 and r = 1.72."

**오류 3중 정리:**
1. **인용문 조작**: `by combining width and coverage` 는 원문에 없다. 원문은 `by rewarding narrow prediction intervals and penalizing intervals missed by the observation`. (유사 표현 `addresses width as well as coverage`는 **Abstract**와 §9.3 맥락에 존재하지만, 이 문장에 붙어 있지 않다.)
2. **절(section) 오귀속**: §6.3이 아니라 **§8.3 (Case Study: Probabilistic Forecasts of Sea-Level Pressure over the North American Pacific Northwest)** 이다.
3. **사례연구 내용 혼동**: 요약이 "§6.3 조건부 이분산 과정 + inflation factor r"이라고 합쳐 썼는데, 이는 **서로 다른 두 사례연구**다.
   - **§6.3 (p.371)**: 정상 bilinear process X_{t+1} = ½X_t + ½X_t ε_t + ε_t 의 1-step 95% 구간 I, J, K 비교. **inflation factor 없음.** Table 2 결과: I 커버리지 95.01% / 폭 4.00 / interval score **4.77**, J 95.08% / 5.45 / 8.04, K 94.98% / 폭 **3.79(가장 좁음)** / 5.32. 원문: "The interval forecasts I, J, and K all showed close to nominal coverage, with the prediction interval K being sharpest on average. Nevertheless, the classical prediction interval I performed best in terms of the interval score."
   - **§8.3 (p.374)**: 5-member 기상 앙상블 + inflation factor r. Fig.4.

**교정 제안**: §6.3은 "세 구간 모두 커버리지 95% 근처 + K가 가장 좁은데도 interval score는 I가 최선" → **"좁은 구간 + 명목 커버리지"가 좋은 예측을 뜻하지 않는다**는 우리 논문 주장에 오히려 §8.3보다 강력한 근거다. 두 사례를 분리해서 각각 정확히 인용할 것.

### 5-5. 신규확인 — 커버리지/구간 관련 추가 원문 근거 (요약에 없음)

- GR07 Abstract: "...and propose the intuitively appealing **interval score as a utility function in interval estimation that addresses width as well as coverage.**" ← 요약이 쓰고 싶어했던 취지의 문장은 **여기**에 있다.
- GR07 §9.3 (p.376): Casella, Hwang, Robert(1993) 인용 "the question of measuring optimality ... of a set estimator against a loss criterion combining size and coverage does not yet have a satisfactory answer." 및 "we contend that a meaningful comparison of interval estimators requires either equal coverage or equal width."
  → **"커버리지만으로 비교하면 안 된다"의 가장 명시적인 원문 근거는 §6.3/§8.3이 아니라 §9.3의 이 문장**이다.
- GBR07 Table 6 (p.259, 실증 사례): Persistence 50.9/89.2, Autoregressive 55.6/90.4, RST 51.2/88.4 — 실데이터에서도 커버리지가 비슷하나 CRPS 순위는 RST≫AR≫PS.

---

## 6. 캘리브레이션 진단법 종합 (요약 §5) 대조

### 6-1. §5 결론부 인용 — **내용 정확 / 페이지 오류 / 편집 개입 표시 필요**

원문(GBR07 §5 Discussion, 실제 **p.264**; 요약은 p.266으로 표기):
> "Our own applied work on probabilistic forecasting has benefited immensely from these tools, as documented in Section 4 and in the partial applications in Gneiting et al. (2004), Raftery et al. (2005) and Gneiting et al. (2005). ... **If we were to reduce our conclusions to a single recommendation, we would close with a call for the assessment of sharpness, particularly when the goal is that of ranking. Previous comparative studies of the predictive performance of probabilistic forecasts have focused on calibration.**"

**판정: 인용문 정확**(요약이 넣은 `[only]`는 원문에 없는 편집 삽입 — 대괄호로 표기했으므로 형식상 허용이나, 논문 본문에서는 삭제 권고). **페이지는 p.264.**

원문은 이어서 근거 문헌을 열거하며, 그중 **금융 사례**가 있다:
> "...Garratt et al. (2003) assessed macroeconomic forecast models and **Bauwens et al. (2004) studied the predictive performance of financial duration models. In each of these works, the assessment was based on the predictive performance of the associated point forecasts, and on the uniformity of the PIT values. We contend that comparative studies of these types call for routine assessments of sharpness, in the form of sharpness diagrams and through the use of proper scoring rules.**"

→ **"금융 분야 선행연구조차 point accuracy + PIT 균등성만 봤고 sharpness를 안 봤다"는 저자들의 명시적 지적**. 우리 논문의 "선행연구 4편 전부 CRPS·캘리브레이션 축 공백" 주장과 정확히 같은 구조의 비판이므로, 원저자 권위로 인용 가능. **요약에 없음 — 추가 강력 권고.**

### 6-2. §5 도구 세트 4종 — **정확**
원문 §5(p.264): "we proposed the use of marginal calibration plots, sharpness diagrams and proper scoring rules" + PIT histogram. 요약의 4항목 열거는 원문과 부합.
단, **sharpness diagram의 정의**를 요약은 "예측분포의 폭(농도) 그 자체를 시각화"라고만 했는데 원문은 더 구체적이다:
> "The average width then is insufficient to characterize sharpness, and we follow Bremnes (2004) in proposing **box plots** as a more instructive graphical device. We refer to this type of display as a sharpness diagram." (§3.3, p.255)
→ **조건부 이분산이 있으면 평균 폭만으로는 부족하고 박스플롯이 필요**하다는 것. 금융(변동성 군집) 데이터를 다루는 우리 연구에 직접 해당. 추가 권고.

### 6-3. 신규확인 — **CRPS의 Brier 분해 (식 14) 및 prediction error curve 누락**
GBR07 §3.4 (p.256):
> "CRPS = (1/T) Σ_{t=1}^{T} crps(F_t, x_t) = ∫_{−∞}^{∞} BS(y) dy, (14) where BS(y) = (1/T) Σ_{t=1}^{T} {F_t(y) − 1(x_t ≤ y)}² denotes the Brier (1950) score for probability forecasts of the binary event at the threshold value y ∈ R. Like all proper scoring rules for binary probability forecasts, the Brier score allows for the distinction of a calibration component and a refinement component (Murphy, 1972; DeGroot and Fienberg, 1983; Dawid, 1986). **Candille and Talagrand (2005) discussed calibration–sharpness decompositions of the continuous ranked probability score.**"
> "Fig. 3 plots the Brier score for the associated binary forecasts in dependence on the threshold value... This type of display was proposed by Gerds (2002), section 2.3, and Schumacher et al. (2003), who called the graphs **prediction error curves**." (p.256)

**의의**: 우리 연구는 "TSFM의 캘리브레이션이 **어느 값 영역(꼬리 vs 중심)에서** 붕괴하는가"를 봐야 한다. 식 (14)의 임계값별 Brier 곡선은 **CRPS를 임계값 축으로 분해하는 원문 제공 도구**이며, 두꺼운 꼬리 진단에 이상적이다. 게다가 Candille & Talagrand(2005)의 CRPS calibration–sharpness 분해는 요약 §6-첫째의 "CRPS 하나로 요약"을 더 정교하게 만드는 후속 문헌이다. **요약에 전혀 없음 — 추가 권고.**

### 6-4. 신규확인 — **GR07 §8.2: CRPS가 로그점수보다 극단값에 강건 (금융 데이터에 결정적)**
GR07 §8.2 (실제 p.374):
> "It is interesting to observe that the logarithmic score gave the highest maximizing value of r. The logarithmic score is strictly proper but involves a harsh penalty for low probability events and thus is highly sensitive to extreme cases. ... **In our experience, the CRPS is less sensitive to extreme cases or outliers and provides an attractive alternative.**"
(GBR07 §3.4 p.256도 동일 취지: "This scoring rule [logarithmic score] is proper and has many desirable properties (Roulston and Smith, 2002), but **it lacks robustness** (Selten, 1998; Gneiting and Raftery, 2006). The continuous ranked probability score ... **provides a more robust alternative.**")

**의의**: 우리 논문이 **왜 NLL/log score가 아니라 CRPS를 주지표로 삼는가**에 대한, 두 논문 모두에 있는 1차 근거. 두꺼운 꼬리 합성 데이터에서 log score는 발산 위험이 있으므로 방법론 정당화에 필수. **요약에 없음 — 추가 강력 권고.**

또한 GR07 §8.2는 improper score의 위험을 실증한다: linear score와 probability score는 r = .05, r = .02에서 최대화되어 "suggesting ignorable forecast uncertainty and essentially deterministic forecasts... However, they are improper, and their use may result in misguided scientific inferences". → **"부적절한 지표를 쓰면 모델이 불확실성을 0으로 보고하도록 유도된다"** 는 TSFM 과신 논의와 직결.

---

## 7. Diebold–Mariano 검정 및 점수차 유의성 — **요약에 완전 누락 (신규확인)**

작업지시서가 지목한 항목. **두 원문 모두에 언급이 있다.**

**(a) GBR07 §4.4 (실제 p.263) — 실제 사용법까지 제시:**
> "We report the scores month by month, which allows for an assessment of seasonal effects and **straightforward tests of the null hypothesis of no difference in predictive performance.** For instance, the RST method showed lower CRPS than the autoregressive technique in each month during the evaluation period. Under the null hypothesis of equal predictive performance this happens with probability (1/2)⁷ = 1/128 only. Similarly, ... **Various other tests can be employed, but care needs to be taken to avoid dependences in the forecast differentials.** Here, the results for distinct months can be considered independent for all practical purposes. **Diebold and Mariano (1995) gave a thoughtful discussion of these issues, and we refer to their work for a comprehensive account of tests of predictive performance.**"

**(b) GR07 §10 (실제 p.376):**
> "**Diebold and Mariano (1995), Hamill (1999), Briggs (2005), Briggs and Ruppert (2005), and Jolliffe (2006) have developed formal tests of forecast performance, skill, and value.** This is a promising avenue for future work..."

**(c) GBR07 §1 (p.243):** 계량경제 문헌 갈래로 "Diebold and Mariano, 1995; Christoffersen, 1998; Diebold et al., 1998; Corradi and Swanson, 2006" 열거.

**판정: 요약 누락(신규확인).**
**의의**: 우리 연구가 여러 TSFM의 CRPS를 비교해 "어느 모델이 더 낫다"고 주장하려면 **점수 차의 유의성 검정**이 필요하고, 그 표준 근거가 DM 검정이다. 또한 GBR07이 명시한 **"forecast differentials의 종속성을 피하도록 주의"** 는 시계열 다중 horizon 평가에서 반드시 다뤄야 할 이슈다(우리 설계에서 horizon 간 중첩 윈도우 사용 시 직격). 요약 §6에 4번째 층으로 추가 권고.

---

## 8. FinStressTS 대조

**전제 확인**: 요약 파일 `하위갈래B_확률예측_평가론.md`에는 **FinStressTS에 대한 언급이 단 한 줄도 없다.** 따라서 "요약이 FinStressTS를 잘못 옮겼다"는 판정은 성립하지 않으며, 아래는 전부 **신규확인 / 누락** 항목이다.

### 8-1. FinStressTS의 CRPS 정의 (식 4) — GR07과 부호 orientation 반대
> "$\mathrm{CRPS}(F,y)=\int_{\mathbb{R}}\big(F(z)-\mathbf{1}\{y\leq z\}\big)^{2}\,dz. \tag{4}$"
> "CRPS is a proper scoring rule and is minimized in expectation when the predictive distribution matches the data-generating distribution."

→ GR07 식 (20)은 음수(positively oriented), FinStressTS 식 (4)는 양수(penalty). **GBR07 식 (12)와 같은 관례.** 지시함수도 `1{y ≤ z}`로 GR07의 `1{y ≥ x}`와 표기 방향이 다르나 수학적으로 동치. 우리 논문에서 부호 관례를 명시하지 않으면 혼선.

### 8-2. FinStressTS의 샘플 기반 추정량 (식 5) — **GR07 식 (21)과 계수가 다름 (중요)**
> "$\widehat{\mathrm{CRPS}}(F,y)=\frac{1}{S}\sum_{s=1}^{S}|x^{(s)}-y|-\frac{1}{2S^{2}}\sum_{s=1}^{S}\sum_{s'=1}^{S}|x^{(s)}-x^{(s')}|. \tag{5}$"

**대조 결과**: 이론식은 E|X−x| − ½E|X−X′| 이고, 여기서 E|X−X′|의 **불편(unbiased) 추정량은 1/(S(S−1))·Σ_{s≠s'}** 이다. FinStressTS는 **1/S²로 대각항(s=s')까지 포함**하는 **편향(biased) 추정량**을 쓴다(대각항은 0이므로 실질적으로 (S−1)/S 만큼 축소 → 두 번째 항 과소평가 → **CRPS를 체계적으로 과대평가**, 특히 S가 작을 때). 이는 gluonts/일부 구현의 관례이기도 하다.

**우리 논문 함의**: 샘플 수 S가 모델마다 다르면(예: Chronos 20 샘플 vs 다른 모델 100 샘플) **이 편향이 모델 간 비교를 오염**시킨다. 요약 「확인 불가 항목 3」(gluonts 구현 확인)에 이 쟁점을 명시적으로 추가할 것. 구현 시 S를 모델 간 통일하거나 불편 추정량(1/(S(S−1)))을 쓸 것.

### 8-3. FinStressTS의 다변량 지표 (식 6) — CRPS_sum
> "For multivariate time series, we evaluate calibration on the cross-sectional aggregate, reflecting portfolio-level distributional accuracy. ... $\mathrm{CRPS}_{\text{sum}} = \frac{1}{WH} \sum_{w=1}^{W} \sum_{h=1}^{H} \widehat{\mathrm{CRPS}}(F_{w,h}^{\text{sum}}, y_{w,h}^{\text{sum}})$ (6)"
> "To compare across datasets with different scales, we report a normalized version by dividing CRPS_sum by $\frac{1}{WH}\sum_{w,h}|y^{\text{sum}}_{w,h}|$."

→ **Table 3의 수치는 이 정규화된 CRPS_sum이다** (그래서 대부분 1.0 근처 값). 요약이 Table 3 수치를 인용할 일이 있다면 "raw CRPS"가 아님을 반드시 밝힐 것.
→ CRPS_sum은 요약 §1.4가 언급한 Energy Score와 다른 접근(합산 후 1차원 CRPS)이다. 다변량 확장 논의 시 둘을 구분할 것.

### 8-4. FinStressTS Table 3의 신뢰도 — 로컬 사본 자체에 경고가 있음
로컬 사본 파일 자체가 다음을 명시한다:
> "참고: 원문 HTML의 Table 3은 셀 병합/줄바꿈이 텍스트 추출 과정에서 일부 뒤섞여, 몇몇 행(특히 Case 2 L4, Case 3 L5, Case 4 L2/L3/L4)의 열 정렬이 완전히 명확하지 않음."

→ **Table 3의 개별 셀 수치를 우리 논문에 인용하면 안 된다.** 인용이 필요하면 arXiv PDF 재대조 필수. Finding 4의 정성적 서술("DeepAR achieves the best CRPS in 24 of 30 settings")은 본문 문장이므로 상대적으로 안전.

### 8-5. **FinStressTS는 CRPS만 쓰고 PIT·커버리지·interval score를 쓰지 않는다 (우리 논문의 공백 근거)**
파일 전체 grep 결과: `PIT`, `coverage`, `interval score`, `pinball`에 해당하는 지표 정의·보고가 **없다**. 확률예측 평가지표는 CRPS(식 4·5)와 CRPS_sum(식 6)이 전부다. 유일하게 "predictive intervals/calibration"이라는 표현이 §3 Case 3 설명에서 **연구 동기(diagnostic question)** 로만 등장한다:
> "Diagnostic question: do forecasts remain reliable under tail risk, and are predictive intervals/calibration robust when shocks are heavy-tailed or contaminated?"

→ **FinStressTS는 "구간/캘리브레이션을 진단하겠다"고 선언해놓고 실제로는 스칼라 CRPS 하나만 보고한다.** 이는 우리 논문의 차별점(PIT 히스토그램 + 커버리지 + interval score 병행)을 정당화하는 **직접적인 문헌 공백 증거**이며, 동시에 GBR07 §5 Discussion의 비판("assessment was based on point forecasts and PIT uniformity ... call for routine assessments of sharpness")과 정확히 같은 구조다. 강력 활용 권고.

### 8-6. FinStressTS의 CRPS 인용 출처
> "[40] James E Matheson and Robert L Winkler. 1976. Scoring rules for continuous probability distributions. Management science 22, 10 (1976), 1087–1096."

→ FinStressTS는 CRPS를 **Gneiting & Raftery(2007)가 아니라 Matheson & Winkler(1976)** 로 인용한다. GR07 식 (20)도 "(Matheson and Winkler 1976; Hersbach 2000)"을 병기하므로 모순은 없다. 우리 논문은 두 출처를 함께 인용하는 것이 안전.

---

## 9. 원 요약 파일 수정 제안 (직접 수정하지 않음)

### A. 반드시 고쳐야 할 것 (오류)

| # | 위치 | 현재 | 수정안 |
|---|---|---|---|
| A1 | §4.2 | 인용문 `"This scoring rule assesses both calibration and sharpness, by combining width and coverage."` | 원문 문언으로 교체: `"This scoring rule assesses both calibration and sharpness, by rewarding narrow prediction intervals and penalizing intervals missed by the observation."` (GR07 §8.3, p.374) |
| A2 | §4.2 | 출처 `원문 §6.3 사례연구, p.371-373` | `GR07 §8.3, p.374`로 정정. 그리고 §6.3(p.371, bilinear process, Table 2, 구간 I/J/K)과 §8.3(p.374, 기상 앙상블, inflation factor r, Fig.4)을 **별도 항목으로 분리** 서술. |
| A3 | §4.2 | "사례연구(조건부 이분산 과정, ensemble inflation factor r을 조정하며…)" | 두 사례를 섞은 서술. §6.3에는 inflation factor가 없다. 분리 서술. |
| A4 | §1.3 / 확인불가 1 | "원문은 식 (21)의 절대오차 기댓값 형태만 명시" | 부정확. GR07 **식 (41)(pinball/tick loss), 식 (48)(분위수 점수 적분), 식 (49)(Brier 적분 = CRPS)** 가 원문에 존재함을 명시하고, "다만 CRPS = 2∫₀¹Λ_α dα 라는 **그 정확한 형태의 등식**은 원문에 없다"로 한정. |
| A5 | §2.5 | `식 (43), p.371` / `(원문 §6.2, p.371)` | **p.370** |
| A6 | §2.1, §2.2 | p.360 / p.361 | "Suppose... strictly proper" 및 "In terms of elicitation..." → **p.359**. 식 (1) → **p.360**. |
| A7 | §3.1, §3.2 | p.245 / p.245-246 | PIT 식 (2) 및 Hamill 반례 문장 → **p.244** |
| A8 | §3.3 | `§2, p.250 부근` | Definition 1(d) → **p.247** |
| A9 | §3.4, §3.5 | p.252 | 히스토그램 형태 해석 문장과 rank histogram 문장 → **p.253** (단 "10 or 20 bins"와 Table 3 문장은 p.252로 맞음) |
| A10 | §5 | `§5 Discussion, p.266` | **p.264** |
| A11 | §5 | `focused on calibration [only]` | `[only]`는 원문에 없는 삽입. 삭제하거나 각주로 편집 사실 명시. |
| A12 | §1.2 | `"reports in the same unit as the observations..."` | 원문은 `can be reported in the same unit as the observations, and it generalizes the absolute error...`. 직접 인용 시 어형 일치시킬 것. |
| A13 | §1.2 | O(n log n) 인용을 "폐형식 (21)" 항목 아래 배치 | 원문은 "the right side of **(20)**"라고 명시. 항목 위치 조정 또는 단서 추가. |

### B. 추가해야 할 것 (누락 — 우선순위 순)

| # | 내용 | 근거 | 왜 필요한가 |
|---|---|---|---|
| B1 | **GBR07 Table 5 (LogS/CRPS로 4 예측자 정확히 순위 매김)** | GBR07 p.256–257 | "PIT는 구분 못 하지만 CRPS는 구분한다"의 원문 내 실증. 요약 §6-첫째의 핵심 주장 근거. |
| B2 | **GBR07 Table 4 (평균 구간 폭)** | GBR07 p.255 | "커버리지 동일 + 폭 최대 41% 차이" → 요약 §4.1 주장의 정량 증거. |
| B3 | **CRPS가 log score보다 극단값에 강건** | GR07 §8.2 p.374 / GBR07 §3.4 p.256 | 두꺼운 꼬리 금융 데이터에서 NLL 대신 CRPS를 주지표로 삼는 1차 근거. |
| B4 | **Diebold–Mariano 및 점수차 검정, forecast differential 종속성 경고** | GBR07 §4.4 p.263 / GR07 §10 p.376 | 다중 TSFM 비교 시 유의성 주장에 필수. 요약에 전무. |
| B5 | **CRPS = ∫BS(y)dy 임계값 분해 (식 14) + prediction error curve + Candille & Talagrand(2005) 분해** | GBR07 §3.4 p.256 | "꼬리 영역에서 붕괴하는가 중심에서 붕괴하는가"를 임계값 축으로 진단. 우리 설계와 최적 적합. |
| B6 | **GR07 §10의 두 번째 computational finance 문장** | GR07 p.376 | proper scoring rule **전반**(CRPS 포함)에 대한 금융 응용 제안. §6.2 문장보다 CRPS 인용에 논리적으로 적합. |
| B7 | **GBR07 §5의 "금융 선행연구조차 point accuracy + PIT만 봤다" 비판** | GBR07 p.264 (Bauwens et al. 2004 언급 포함) | 우리 논문의 "선행연구 공백" 주장을 원저자 권위로 뒷받침. |
| B8 | **GR07 §9.3 "meaningful comparison of interval estimators requires either equal coverage or equal width" + Abstract "addresses width as well as coverage"** | GR07 p.376 / Abstract | "커버리지 단독 비교 금지"의 가장 명시적 원문 문장. §4.2의 잘못된 인용을 대체할 정본. |
| B9 | **GBR07 식 (12)(13) 및 "샘플로 표현된 F에 (13)이 특히 편리"** | GBR07 p.256 | TSFM 샘플 출력 설정과 직결. 요약 §6-셋째의 1차 근거. |
| B10 | **FinStressTS 대조 절 신설** (식 4·5·6, 1/(2S²) 편향, CRPS_sum 정규화, PIT/커버리지 부재, Table 3 추출 불안정) | 8절 참조 | 요약에 FinStressTS가 전혀 없음. 벤치마크 비교 및 공백 주장에 필수. |
| B11 | **Berkowitz(2001) Φ⁻¹(p_t) 변환**, 형식 검정의 한계 경고 | GBR07 p.253 | 요약 §3.6의 PIT 독립성 검정을 실제 수행 가능한 형태로. |
| B12 | **sharpness diagram = 구간 폭의 박스플롯**(평균 폭만으로 불충분, 조건부 이분산 때문) | GBR07 §3.3 p.255 | 변동성 군집 데이터에서 평균 폭이 부적절함을 원저자가 지적. |
| B13 | **GR07 §6.3 Table 2 수치** (I: 95.01%/4.00/4.77, J: 95.08%/5.45/8.04, K: 94.98%/3.79/5.32) | GR07 p.371 | "가장 좁은 구간 K가 interval score에서는 최선이 아니다" — 요약 §6-첫째(3)의 직접 근거. |
| B14 | **GR07 §6.4 다변량 CRPS** | GR07 p.371 | 요약 §1.4는 다변량 확장으로 Energy Score만 언급. 다변량 CRPS와 FinStressTS의 CRPS_sum까지 3자 구분 필요. |
| B15 | **1차 모멘트 발산 시 strict propriety 및 식 (21) 붕괴 경고** | GR07 p.367 조건부 | 요약 §2.4가 heavy-tail을 낙관적으로 서술. 합성 데이터 자유도 설정 시 실제 제약. |
| B16 | **GR07 §8.2 improper score(linear/probability score)가 r→0을 유도** | GR07 p.374 | "부적절한 지표는 모델이 불확실성을 0으로 보고하게 유도" — TSFM 과신 논의와 연결. |

### C. 유지해도 되는 것
요약 §1.1, §1.2(수식), §1.4, §2.1~§2.4, §2.5(수식 및 §6.2 귀속), §3.1~§3.6(내용), §4.1(Table 3 수치), §5(도구 4종)의 **실질 내용은 원문과 부합**한다. 페이지·인용어형만 A항대로 교정하면 된다.

---

## 10. 원문에 없다고 확인된 것 (환각 방지 명시)

1. **"CRPS를 computational finance에 제안"하는 문장은 GR07에 없다.** §6.2 p.370의 문장은 **interval score**에 대한 것이고, §10 p.376의 문장은 **proper scoring rules 전반**에 대한 것이다. CRPS를 콕 집어 금융에 제안한 문장은 존재하지 않는다.
2. **"This scoring rule assesses both calibration and sharpness, by combining width and coverage."** 라는 문장은 GR07·GBR07 어디에도 없다.
3. **"CRPS(F⁻¹, x) = ∫₀¹ 2·Λ_α(F⁻¹(α), x) dα"** 형태의 등식은 GR07에 없다(요약의 판단은 이 점에 한해 옳다). 다만 그 구성 재료(식 41·48·49)는 있다.
4. **"커버리지 단독 판정 금지"** 라는 취지를 한 문장으로 못박은 표현은 두 논문에 **없다**. 가장 가까운 것은 ① GR07 §9.3 "requires either equal coverage or equal width", ② GR07 Abstract "addresses width as well as coverage", ③ GBR07 p.252 "This information is redundant, since the empirical coverage can be read off the PIT histogram", ④ GBR07 §5 p.264 "a call for the assessment of sharpness" 네 가지다. 논문에서는 이 넷을 조합해 우리 문장으로 재구성하고, 각각에 정확한 출처를 달 것.
5. **FinStressTS에는 PIT·구간 커버리지·interval score·pinball loss 지표가 없다.** 확률예측 평가는 CRPS와 CRPS_sum뿐이다.
6. GBR07 사본에 페이지 243–268이 모두 포함되어 있고 본문에 저널 페이지 번호가 그대로 찍혀 있으므로, 요약 「확인 불가 항목 2」의 "정식본 사본으로 판단" 판정은 **타당하다**(검증자도 동일 확인). GR07 사본도 pp.359–376 러닝헤드가 일관되게 확인된다.

---

## 11. 검증하지 못한 항목

1. **원문 PDF 원본과의 대조는 수행하지 않았다.** 로컬 `.md` 사본(웹 fetch된 PDF 텍스트 추출본)만 대조했다. 텍스트 추출 과정에서 수식 기호(Φ, ϕ, ‖·‖, 아래첨자)가 소실된 곳이 다수 있어, 수식 자체는 문맥으로 복원했다. 최종 원고 제출 전 PDF 원본으로 수식과 페이지를 1회 더 대조할 것.
2. **Gneiting & Ranjan (2011), Laio & Tamea (2007)** — 로컬 `01_자료원문/`에 사본 없음. 요약 「확인 불가 항목 1」은 여전히 유효(단 A4대로 서술 수정 후).
3. **gluonts CRPS 구현** — 로컬 자료 없음. 요약 「확인 불가 항목 3」 유효. 8-2절의 1/(2S²) 편향 쟁점을 이 확인 항목에 병합할 것.
4. **FinStressTS Table 3 개별 셀 수치** — 사본 자체의 열 정렬 불안정 경고로 인해 셀 단위 검증 불가.
5. **JASA/JRSS-B 정식 조판본의 페이지 번호** — 본 로그의 페이지 판정은 사본 내 러닝헤드 기준이며 일관성은 확인했으나, 조판본과의 최종 대조는 미수행.
