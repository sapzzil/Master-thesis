# 검증로그 — 하위갈래 C (금융 stylized facts와 생성모형)

- 검증 대상: `02_요약정리/하위갈래C_금융stylizedfacts_생성모형.md`
- 대조 원문: `01_자료원문/2606.03184_FinStressTS_Synthetic_Benchmark.md` (611행, Appendix A.1~A.6 및 References [1]-[60] 포함 완전본)
- 검증일: 2026-08-15
- 검증자: 독립 교차검증 에이전트 (요약 작성자와 별개)
- 검증 방법: (a) 원문 전문 대조, (b) GitHub 저장소 실제 fetch, (c) 서지정보 WebSearch 재확인

---

## 0. 총평 (먼저 읽을 것)

**GitHub 코드 근거는 환각이 아니다 — 실제로 확인됨.** 요약이 근거로 든 저장소, 파일 경로, 클래스명, 파라미터명, 5-레벨 수치가 모두 실물과 일치했다. 이 항목은 "확인 완료"로 종결한다.

다만 **원문 프로즈 인용 관련해서 3건의 실질적 오류**(Engle 페이지 번호, Section 2.3 인용 위치 주장, Limitations 인용 왜곡)와 **레벨 파라미터 서술의 불완전성 6건**(변화하는 파라미터를 1개만 적었으나 실제로는 2~3개가 동시에 변함)이 발견되었다. 특히 Case 5 Level 3 누락은 실질적 의미가 큰 오류다.

또한 요약 서두의 "확인 방법 및 한계" 문단 전체가 **현재 상태와 불일치**한다(아래 §1).

---

## 1. 가장 중요 — GitHub 코드 근거의 실재성 검증

요약 21행은 정확한 수식·파라미터의 출처를 논문 Appendix A가 아니라 저자 GitHub 저장소로 명시했다. 이를 직접 fetch로 검증했다.

| 요약의 주장 | 검증 결과 | 근거 |
|---|---|---|
| 저장소 `github.com/jiazeee/FinStressTS` 존재 | **실재 확인** (public, MIT, Python 100%, 8 commits, star 3) | `https://github.com/jiazeee/FinStressTS` fetch 성공 |
| 패키지/CLI 코드명이 `finprobts` | **실재 확인** | README: "The Python package and CLI are named `finprobts`" |
| 6개 케이스명 `case1_garch`/`case2_har`/`case3_heavy_tail`/`case4_regime`/`case5_hawkes`/`case6_zip_panel` | **6개 전부 실재 확인** | README 표 + `presets.py`의 `CASE_PRESETS` 키 |
| `finprobts/synthetic/presets.py` | **실재 확인, 전문 확보** | `raw.githubusercontent.com/.../finprobts/synthetic/presets.py` fetch 성공 |
| `finprobts/simulators/garch.py` | **실재 확인, 전문 확보** (`GARCHSimulator` 클래스) | raw fetch 성공 |
| `finprobts/simulators/har.py`, `heavy_tail.py`, `regime_switching.py`, `hawkes.py`, `zero_inflated.py` | **5개 전부 실재 확인** (경로 및 클래스명까지 일치) | `finprobts/synthetic/generator.py`의 `_make_simulator()` import 문에서 직접 확인: `HARSimulator`, `HeavyTailSimulator`, `MarketRegimePanelSimulator`, `MarketHawkesPanelSimulator`, `MarketZIPPanelSimulator` |
| "GARCHSimulator, HARSimulator 등" 클래스명 | **정확** | garch.py 전문에서 `class GARCHSimulator(BaseSimulator)` 확인 |

**결론: 환각 위험 없음.** 요약 작성자는 실제로 저장소를 열람했다고 판단된다. 파일 경로 6개와 클래스명이 우연히 맞을 확률은 사실상 0이며, 아래 §3의 5-레벨 수치 30개가 전부 일치한 것이 결정적 증거다.

**추가로 이 경로 선택이 정당했음을 확인함**: 논문 §3.3 마지막 문장이 "Complete parameter specifications for all 30 environments are provided in the accompanying repository."라고 명시한다. 즉 **레벨별 수치는 논문 본문·Appendix A 어디에도 없고, 저장소가 유일한 1차 출처다.** 요약의 판단은 옳았다.

### 1-1. 다만 요약 서두 "확인 방법 및 한계"(5행)는 현재 사실과 불일치 — **수정 필요**

요약은 "arXiv fetch가 응답 크기 제한으로 Section 6 중반까지만 확보되고, References 목록과 Appendix A는 직접 읽지 못했다"고 적었다. 그러나 `01_자료원문`의 원문 파일은 **수집 상태 "완전"이며 Appendix A.1~A.6 전문과 References [1]-[60] 전체를 포함**하고 있다(원문 파일 6행, 306~607행). 요약 43행의 "확인 못함(명시)" 항목도 마찬가지로 무효다.

→ 대조 결과 Appendix A의 수식과 요약의 서술은 아래 §2에서 보듯 대체로 일치하므로 내용상 손실은 없으나, **한계 문단은 삭제 또는 "원문 완전본으로 사후 검증 완료"로 갱신해야 한다.**

---

## 2. 6개 메커니즘 — 논문 Appendix A 수식 대조

| # | 항목 | 판정 | 상세 |
|---|---|---|---|
| 1 | GARCH 수식 | **정확** | 요약 "σ²_t = ω + a·ε²_{t−1} + b·σ²_{t−1}" ↔ 논문 Eq.(9)(11). 팩터/개별기업 분리 구현, ω=(1−α−β)σ̄² (Eq.10,12), ρ=α+β (Eq.13), κ share 분해 — 전부 일치. 코드 docstring도 동일. |
| 1 | 이질성 구현 | **정확·보강** | 요약 `idio_sigma_log` ↔ 논문 Eq.(12) σ̄²_{u,i}=σ̄²_u·exp(σ_log ξ_i − ½σ_log²), E[σ̄²_{u,i}]=σ̄²_u 보존. 코드 garch.py에서 동일 확인. |
| 2 | HAR 수식 | **정확** | 요약 σ²_t = c + b1·u²_{t-1} + b5·mean(5) + b22·mean(22) ↔ 논문 Eq.(15). 논문은 L_{5,t}=min(5,t), L_{22,t}=min(22,t)이고 평균에 lag 1 포함, ε>0 floor — 요약이 이 디테일은 생략(경미). |
| 2 | s/lam 역산 | **정확** | 요약 "b22=lam·s, 나머지를 b1/b5에 균등배분" ↔ 논문 Eq.(19) b22=λs, b1=b5=(1−λ)s/2. 코드 `generator._har_coeffs_from_s_lambda()`도 `rem=(1−lam)*s; return rem/2, rem/2, b22`로 완전 일치. |
| 2 | c_idio / gamma | **정확** | 논문 Eq.(17) c_u=c_idio, c_f=γ·c_idio. 코드 `cfg["c_factor"] = cfg["gamma"] * cfg["c_idio"]` 일치. |
| 3 | Student-t 표준화 | **정확** | 요약 "표준화된 Student-t 충격(ν), ν>2 제약" ↔ 논문 Eq.(23) z ~ √((ν−2)/ν)·t_ν, ν>2. |
| 3 | 이상치 비피드백 | **정확** | 요약 "이상치는 변동성 재귀에 피드백되지 않도록 설계(`u_base`만 재귀에 사용)" ↔ 논문 Eq.(25) 직후 "The GARCH recursion depends only on u^base_{i,t}". **정확히 일치, 좋은 포착.** |
| 3 | outlier_scale 의미 | **경미한 불명확** | 논문 Eq.(24): o_{i,t} = s_{i,t}·c_out·**σ_{u,i,t}** — 즉 당시 조건부 표준편차에 곱하는 배율. 요약은 "오염 시 충격 배율"로만 적어 무엇에 곱하는지 불명확. 보강 권장. |
| 4 | 블록 마르코프 | **정확** | 요약 "블록 단위 고정 후 3상태(Up/Stable/Down) 블록마르코프" ↔ 논문 Eq.(26) b(t)=⌈t/B⌉, Π row-stochastic, s_t=s_{b(t)}. "원 Hamilton 모형의 시점별 전환 대신 블록 마르코프로 변형"이라는 요약의 해석도 논문 Appendix A.4 문구("To model structural breaks rather than rapid switching")와 부합. |
| 4 | 패널식 | **정확** | 요약 y_{i,t}=a_i·μ_{s_t}+φ·y_{i,t-1}+b_i·σ_{s_t}·ε_{i,t} ↔ 논문 Eq.(27) 완전 일치. |
| 4 | a_i, b_i 분포 | **미언급(누락)** | 논문 Eq.(28) a_i, b_i ~ LN(−½τ², τ²)로 E=1. 요약에 없음. 코드 `mu_scale_logsigma=0.10`, `sig_scale_logsigma=0.10`이 이 τ. 보강 권장. |
| 5 | Hawkes 재귀 | **정확** | 요약 λ_t = μ + exp(−β)(λ_{t−1}−μ) + α·N_{t−1}, N_t~Poisson(λ_t) ↔ 논문 Eq.(29) δ=exp(−β). 일치. (논문은 Poisson(max{λ_t, ε}) — floor 생략은 경미) |
| 5 | 안정성 조건 | **정확** | 요약 "α < 1−exp(−β) (branching ratio <1)" ↔ 논문 Eq.(30)(31) br_disc=α/(1−exp(−β))<1. 일치. |
| 5 | 점프 크기 | **정확** | 요약 "부호+로그정규 크기" ↔ 논문 Eq.(32)(33) J_t=Σ s_{t,k}A_{t,k}, A~LogNormal(m_log, s_log²), m_log=log(ā)−½s_log² (E[A]=ā). `jump_mean_abs`=ā, `jump_sigma_log`=s_log 대응 정확. |
| 5 | γ_i 노출 | **경미한 부정확** | 요약 "개별기업에 노출 γ_i로 전파". 논문 A.5는 "baseline exposures use γ_i ≡ γ_mean"(동질). 코드 `gamma_logsigma: 0.0` → 실제로 Case 5는 **전 기업 동일 노출**. Case 6만 이질(γ_i~N). 구분 필요. |
| 6 | ZIP 정의 | **정확** | 요약 P(N=0)=π+(1−π)e^{−λ} ↔ 논문 Eq.(34)(35). E[N_t]=(1−π)λ는 요약 미언급(경미). |
| 6 | γ_i 이질성 | **미언급** | 논문 Eq.(37) γ_i ~ N(γ_mean, γ_std²). 코드 `gamma_mean=1.0, gamma_std=0.2` 확인. |
| 공통 | 팩터 골격 | **정확·보강됨** | 요약 §2의 r_{i,t}=α_i+β_i'f_t+u_{i,t} ↔ 논문 Eq.(7). 점프 케이스는 Eq.(8) y_{i,t}=α_i+φy_{i,t-1}+β_i'f_t+ε_{i,t}+γ_i J_t 이고 **Case 5·6에서 f_t ≡ 0**. 요약 §3 둘째 소견("Regime/Hawkes/ZIP는 공통 잠재과정을 패널에 노출")은 논문·코드 양쪽에서 확증됨(presets에 `n_factors: 0`). |

---

## 3. 5-레벨 파라미터 수치 — `presets.py` 실물 대조

논문에는 이 수치가 없으므로 GitHub `presets.py` 전문과 1:1 대조했다.

### Case 1 GARCH — 수치는 전부 정확, 그러나 **"~만 조절" 서술이 부정확**

| Level | presets.py 실제값 | 요약 서술 | 판정 |
|---|---|---|---|
| 1 `baseline_balanced` | rho_f=0.80, rho_u=0.80, idio_sigma_log=0.10, sigma2_bar_factor=0.02 | "ρ_f=ρ_u=0.80" | 정확 |
| 2 `factor_persistent` | rho_f=**0.95**, rho_u=**0.75**, sigma2_bar_factor=**0.03** | "팩터 지속성↑, ρ_f=0.95" | 값 정확, **동시 변화 2개 누락** |
| 3 `idio_persistent` | rho_f=**0.75**, rho_u=**0.95**, sigma2_bar_factor=**0.015** | "개별잔차 지속성↑, ρ_u=0.95" | 값 정확, **동시 변화 2개 누락** |
| 4 `high_heterogeneity` | idio_sigma_log=**0.60** (나머지 L1과 동일) | "이질성↑, idio_sigma_log=0.60" | **완전 정확** |
| 5 `low_common_snr` | rho_f=rho_u=**0.85**, sigma2_bar_factor=**0.005** | "공통 신호 대비 잡음비↓, sigma2_bar_factor=0.005" | 값 정확, ρ 변화 누락 |

파라미터명 `rho_f`, `rho_u`, `alpha_share_f`, `alpha_share_u`, `sigma2_bar_factor`, `sigma2_bar_idio`, `idio_sigma_log` — **7개 전부 실재 확인.**

> **중요**: Level 2/3은 한 쪽 ρ를 올리는 동시에 다른 쪽 ρ를 0.80→0.75로 **내리고** sigma2_bar_factor까지 바꾼다. 논문 §3.3이 주장하는 "ceteris paribus"는 **엄밀하게는 성립하지 않는다.** 이는 요약 §3 둘째 소견(공유 골격 교란)을 실증적으로 강화하는 신규 발견이므로 본문에 반영할 가치가 있다.

### Case 2 HAR — **5개 레벨 전부 완전 정확**

L1 s=0.60/lam=0.40/c_idio=2e-4/gamma=1.00 · L2 s=**0.90** · L3 lam=**0.70** · L4 c_idio=**1e-3**(요약 "5배" — 2e-4→1e-3, 정확) · L5 gamma=**4.00**. 각 레벨이 정확히 1개 파라미터만 변경(진짜 ceteris paribus). 요약 서술과 완전 일치.

> **신규확인(논문 내부 모순)**: 논문 Table 2/3은 Case 2 Level 5를 **"Low SNR"**로 라벨링하나, 코드상 L5는 gamma=4.0 즉 **팩터 기준분산을 4배로 올려 공통 신호를 강화**하는 설정이다. 요약은 코드 기준으로 "팩터 변동성 배율↑"이라 적어 코드에는 충실하지만, 논문 라벨과 어긋난다. 인용 시 이 불일치를 각주로 처리할 것을 권장.

### Case 3 Heavy-tail — 수치 정확, 부수 변화 일부 누락

| Level | presets.py 실제값 | 요약 | 판정 |
|---|---|---|---|
| 1 | nu=8, pi_outlier=0.00, outlier_scale=6, rho_v=0.90 | "ν=8, 오염없음" | 정확 |
| 2 | nu=**3**, pi=0.00 | "극단꼬리, ν=3" | 완전 정확 |
| 3 | nu=8, pi=**0.02** | "빈번한 이상치, π=0.02" | 완전 정확 |
| 4 | nu=8, pi=**0.005**, outlier_scale=**12** | "대형 이상치, scale=12" | 값 정확, **pi 0→0.005 누락** |
| 5 | nu=**3**, pi=**0.02**, scale=**12** | "최악조합, ν=3 & π=0.02 & scale=12" | **완전 정확** |

파라미터명 `nu`, `pi_outlier`, `outlier_scale` 실재 확인. **요약 누락**: `rho_v=0.90`(GARCH 지속성)이 5개 레벨 전부 고정값으로 존재 — 우리 연구가 재파라미터화할 때 반드시 인지해야 할 값이므로 추가 권장.

### Case 4 Regime — **전부 정확**

L1 block_size=50, mu_U/S/D=0.0012/0/−0.0012, sigma_U/S/D=0.010/0.0085/0.016, phi=0.20 · L2 block_size=**10** · L3 mu=**±0.0005**, sigma=0.010/0.0095/0.011(격차 축소) · L4 mu=**±0.0020**, sigma=0.008/0.0075/**0.020**(격차 확대) · L5 phi=**0.60**.
요약의 "Level 1(block=50)→L2(block=10)→L3(μ 격차↓)→L4(μ·σ 격차↑)→L5(phi=0.60↑)" — **5개 전부 일치.** 파라미터명 `mu_U/S/D`, `sigma_U/S/D`, `phi`, `Pi_block` 실재 확인(단 `Pi_block: None`이 기본값 = 시뮬레이터 내부 기본 전이행렬 사용).

### Case 5 Hawkes — **실질적 오류 1건 발견**

| Level | presets.py 실제값 | 요약 | 판정 |
|---|---|---|---|
| 1 | alpha=0.06, beta=1.2, mu=0.05, jump_mean_abs=0.02, jump_sigma_log=0.45 | "약한 군집, α=0.06" | 정확 |
| 2 | alpha=**0.18** | "강한 군집, α=0.18" | **완전 정확** |
| 3 | alpha=**0.25**, beta=**0.4** | "장기기억형 군집, β=0.4↓" | **부정확 — α가 0.06→0.25로 4배 상승하는 것을 누락** |
| 4 | mu=**0.15** | "높은 점프율, μ=0.15" | **완전 정확** |
| 5 | jump_mean_abs=**0.05**, jump_sigma_log=**1.00** | "두꺼운 꼬리 점프, jump_sigma_log=1.00" | 값 정확, jump_mean_abs 0.02→0.05 누락 |

> **Level 3 누락의 심각성**: branching ratio br=α/(1−e^{−β})로 계산하면 L1은 0.06/0.699=**0.086**, L2는 0.18/0.699=**0.258**, L3은 0.25/0.330=**0.758**이다. 즉 **L3이 임계성(criticality)이 가장 높은 설정**이며, "β만 낮춘 장기기억 변형"이 아니라 자기흥분 강도까지 함께 극대화한 레벨이다. 요약대로 인용하면 메커니즘 해석이 왜곡되므로 **반드시 수정 필요.**

파라미터명 `alpha`, `beta`, `mu`, `jump_mean_abs`, `jump_sigma_log` 실재 확인. 고정값 `p_up=0.5`, `gamma_mean=1.0`, `gamma_logsigma=0.0`, `phi=0.1`, `sigma_eps=0.01`, `n_factors=0` 추가 확인.

### Case 6 ZIP — 수치 정확, 부수 변화 1건 누락

| Level | presets.py 실제값 | 요약 | 판정 |
|---|---|---|---|
| 1 | pi=0.70, lam=0.20, jump_mean_abs=0.030, jump_sigma_log=0.60, phi=0.20 | "기준, π=0.70" | 정확 |
| 2 | pi=**0.90** | "희소사건, π=0.90↑" | **완전 정확** |
| 3 | lam=**0.60** | "버스트형 사건, λ=0.60↑" | **완전 정확** |
| 4 | jump_mean_abs=**0.080**, jump_sigma_log=**1.00** | "두꺼운 꼬리 사건, jump_sigma_log=1.00" | 값 정확, jump_mean_abs 누락 |
| 5 | phi=**0.55** | "지속배경, phi=0.55↑" | **완전 정확** |

파라미터명 `pi`, `lam`, `jump_mean_abs`, `jump_sigma_log` 실재 확인. 고정값 `gamma_mean=1.0`, `gamma_std=0.2`, `n_factors=0` 확인.

### 3-1. 신규확인 — T 값 불일치 (요약에 없는 항목)

- 논문 §4.1: "we generate a panel of N=50 series and **T_total = 2,000** steps"
- `presets.py`: 6개 케이스 전부 `"T": 20000` (10배)
- README CLI 예시: `--T 20000 --n-firms 50`
- `GARCHSimulator.__init__` 기본값: `T: int = 2000`

→ **논문 프로즈(2,000)와 공개 코드 프리셋(20,000)이 어긋난다.** N=50과 burn_in=200은 양쪽 일치. 우리 연구가 재현할 때 어느 쪽을 따를지 명시적으로 결정해야 하며, 논문 Table 2/3 수치 재현을 목표한다면 T=2,000이 맞을 가능성이 높다. **요약에 추가 권장.**

### 3-2. 레벨 시나리오 이름 — 논문 Table 2/3과 교차확인

요약이 쓴 레벨 설명을 논문 Table 2의 `Scenario` 열과 대조한 결과, Case 1(Baseline/Factor persistence/Idio persistence/Heterogeneity/Low SNR), Case 3(Heavy tails/Extreme tails/Frequent outliers/Large outliers/Worst-case tails), Case 4(Moderate/Frequent switches/Subtle/Strong/Persistent regimes), Case 5(Moderate/Strong/Long-memory clustering/High jump rate/Heavy-tailed jumps), Case 6(Baseline/Rare/Bursty/Heavy-tailed events/Persistent background) — **총 25개 레벨 라벨이 요약과 일치.** Case 2만 L5에서 §3의 라벨 충돌 존재.

---

## 4. 서지정보 재확인

논문 References [1]-[60] 원문(1차 출처)과 WebSearch 결과를 함께 대조했다.

| 원 논문 | 요약 기재 | 논문 References 원문 | WebSearch | 판정 |
|---|---|---|---|---|
| Engle (1982) | *Econometrica* 50(4), **987–1008** | [19] Econometrica 50, 4 (1982), **987–1007**, doi:10.2307/1912773 (동일 항목 [18]도 987–1007) | Econometric Society 공식 페이지 및 다수 인용이 **987–1007** | **부정확 — 987–1007로 수정** |
| Engle (1982) 제목 표기 | "Heteroscedasticity" (sc) | [19]는 "Heteroskedasticity"(sk), [18]은 "heteroscedasticity"(sc) | 원 Econometrica 제목은 **Heteroscedasticity**(sc) | 요약이 옳음 (논문 자체가 중복 등재하며 표기 혼용) |
| Bollerslev (1986) | *J. Econometrics* 31(3), 307–327, doi 10.1016/0304-4076(86)90063-1 | [7] 동일 | 일치 | **정확** |
| Bollerslev (1987) | *Rev. Econ. Stat.* 69(3), 542–547 | [8] 동일 | 일치 | **정확** |
| Corsi (2009) | *J. Financial Econometrics* 7(2), 174–196, doi 10.1093/jjfinec/nbp001 | [13] 동일 (중복 [14]) | 일치 | **정확** |
| Hamilton (1989) | *Econometrica* 57(2), 357–384 | [25] "Econometrica: Journal of the econometric society (1989), 357–384" (권·호 생략) | 57(2), 357–384 확인 | **정확** |
| Hawkes (1971) | *Biometrika* 58(1), 83–90, doi 10.1093/biomet/58.1.83 | [26] 동일 | 일치 | **정확** |
| Lambert (1992) | *Technometrics* 34(1), 1–14, **doi 10.2307/1269547** | [30] 34, 1 (1992), 1–14, **doi:10.1080/00401706.1992.10485228** | **두 DOI 모두 유효**(JSTOR / Taylor&Francis) | 권·호·페이지 **정확**. DOI만 논문과 다른 계열 — 논문 인용을 따르려면 T&F DOI로 통일 권장 |
| Andersen, Bollerslev, Diebold, Labys (2003) | 요약이 HAR 관련으로 병기 | [3]/[4] *Econometrica* 71(2), 579–625, doi 10.1111/1468-0262.00402 | 일치 | **정확** |
| Bacry, Mastromatteo, Muzy (2015) | "Hawkes processes in finance" 병기 | [6] *Market Microstructure and Liquidity* 1(1), 1550005 | 일치 | **정확** |
| Cont (2001) | 병기 | [11]/[12] *Quantitative Finance* 1(2), 223–236 | 일치 | **정확** |
| Lesmond, Ogden, Trzcinka (1999) | 병기 | [31] *Rev. Financial Studies* 12(5), 1113–1141 | 일치 | **정확** |
| Andersen et al. (2007) "Roughing it up" | 병기 | [2] *REStat* 89(4), 701–720 | 일치 | **정확** |

**서지 판정 요약: 7개 핵심 논문 중 6개 완전 정확, 1개(Engle 페이지) 부정확, 1개(Lambert DOI) 계열 상이.**

---

## 5. 원문 프로즈 인용 정확성 — 오류 2건

### 5-1. 요약 20행 — Section 2.3 인용 위치 주장이 **부정확**

요약은 "Section 2.3에서 (Engle, 1982a; Bollerslev, 1986), (Corsi, 2009a), **(Bollerslev, 1987)**, (Hamilton, 1989), (Hawkes, 1971; Bacry et al., 2015), **(Lambert, 1992)**를 명시"한다고 적었다.

원문 §2.3 실제 인용은 다음이 전부다:
> "volatility clustering and multi-scale persistence **[13, 18]**; heavy tails and regime shifts **[12, 25]**; jump dynamics—both self-exciting **[26]** and zero-inflated **[2]**; latent factor structures **[20, 47]**"

즉 §2.3에는 **Bollerslev(1986)[7]도, Bollerslev(1987)[8]도, Lambert(1992)[30]도 등장하지 않는다.** 특히 zero-inflated 근거로 §2.3이 인용하는 것은 [2] **Andersen, Bollerslev, Diebold (2007)**이지 Lambert가 아니다. Bacry[6]도 §2.3에 없다.

**정확한 위치는 §1 Introduction과 §3.2 Mechanism families다**(양쪽 모두 검증 완료):
- §1: (i) 볼륨클러스터링 **[7, 19]**, (ii) HAR **[13]**, (iii) heavy tail **[11]** + Student-t **[8]**, (iv) regime **[25]**, (v) Hawkes **[26]**, (vi) zero-inflated **[30]**
- §3.2: case1 **[7, 19]**, case2 **[4, 13]**, case3 **[11, 17]**(Cont + **Embrechts et al. 1997** — 요약 미언급), case5 **[6, 26]**, case6 **[30, 31]**

→ 요약 20행을 "§1 Introduction 및 §3.2 Mechanism families에서 확인"으로 **교체 필요**. §2.3만으로는 6개 중 4개(Corsi, Engle, Cont, Hamilton, Hawkes)만 커버된다.

### 5-2. 요약 30행 — Limitations 인용이 **왜곡**

요약은 다음과 같이 인용부호로 적었다:
> 혼합 스트레스는 논문 Limitations(Section 6, 확인됨)에서 **"현재는 6개 메커니즘을 개별적으로만 다루며, 국면전환+두꺼운꼬리+점프의 결합 같은 복합 스트레스 확장은 향후 과제"**라고 명시

원문 §6의 실제 문장은 정반대 뉘앙스다:
> "**While FinStressTS supports compound stresses,** expanding interacting mechanism combinations (e.g., regime shifts with heavy tails and jumps) would further enrich diagnostics."

즉 논문은 **복합 스트레스를 이미 지원한다고 주장**하며, "확장하면 더 좋다"고 덧붙일 뿐이다. §1에서도 "enabling targeted failure-mode analysis under isolated mechanisms **as well as realistic compound stress scenarios**"라고 적는다.

한편 **코드(presets.py)에는 복합 케이스가 전혀 없다** — 30개 환경 전부 단일 메커니즘이다. 따라서 "FinStressTS 자체는 기본적으로 단일축 조작"이라는 요약의 **결론 자체는 코드 기준으로 타당하나, 그 근거로 논문 Limitations를 인용한 것은 잘못**이다.

→ 인용부호를 제거하고 "논문 프로즈는 compound stress 지원을 주장하나, 공개 presets.py의 30개 환경은 모두 단일 메커니즘이므로 실제 배포된 스위트는 단일축이다"로 **재서술 필요**. (이 편이 오히려 우리 연구에 유리한 강한 논거다.)

### 5-3. 검증 통과한 프로즈 인용

- 요약 34행 HAR 각주 인용: 원문 184행에 "Although originally proposed for modeling realized volatility, HAR is applied here as a linear multi-scale autoregressive baseline for mean forecasting on the target series." — **한 글자까지 일치. 정확.** 요약 §3 첫째 소견 전체가 유효.
- 요약 27행 설계원칙 4개(Econometric fidelity / Diagnostic control / Verifiable ground truth / Multivariate panel structure): 원문 §3.1과 **일치**.
- 요약 28행 "ceteris paribus" 및 "Rather than imposing monotonic difficulty": 원문 §3.3과 **일치**.
- 요약 3행 서지(저자 6인, arXiv:2606.03184, KDD '26): 원문 4·22행과 **일치**. DOI 10.1145/3770855.3817578 추가 가능.

---

## 6. 원 요약 파일 수정 제안 (직접 수정하지 않음)

### 필수 (오류 정정)

1. **11행 표 각주 / 19행** — Engle(1982) 페이지 `987–1008` → **`987–1007`**로 정정.
2. **15행 Case 5 Level 3** — "장기기억형 군집, β=0.4↓" → **"장기기억형 + 임계성 극대화: α=0.06→0.25 & β=1.2→0.4 (branching ratio 0.086→0.758)"**로 정정. 현행 서술은 메커니즘 해석을 왜곡함.
3. **20행** — "Section 2.3에서 확인" → **"§1 Introduction 및 §3.2 Mechanism families에서 확인"**으로 교체. §2.3의 zero-inflated 근거는 Lambert가 아니라 Andersen et al.(2007)[2]임을 병기.
4. **30행** — Limitations 인용부호 삭제 후 재서술(위 §5-2). "논문은 compound stress 지원을 주장하나 공개 presets.py의 30개 환경은 전부 단일 메커니즘"이 정확한 사실관계.
5. **5행 및 43행** — "Appendix A·References 미확보" 한계 서술 삭제/갱신. 원문 완전본이 확보되어 있고 대조 완료함.

### 권장 (정확성 보강)

6. **11행 Case 1** — Level 2/3이 한쪽 ρ만 올리는 게 아니라 다른 쪽 ρ를 0.75로 내리고 `sigma2_bar_factor`도 동시 변경한다는 사실 추가. 이는 §3 둘째 소견을 강화하는 실증 근거.
7. **13행 Case 3** — Level 4의 `pi_outlier`가 0→0.005로 함께 변함, 그리고 전 레벨 고정값 `rho_v=0.90`(GARCH 지속성) 존재를 명시.
8. **15·16행 Case 5/6** — Level 5(Case 5) 및 Level 4(Case 6)에서 `jump_mean_abs`도 함께 상승함을 병기.
9. **12행 Case 2** — 논문 Table 2/3의 L5 라벨 "Low SNR"과 코드 `gamma=4.0`(팩터 분산 4배 = 오히려 공통 신호 강화)의 불일치를 각주로 명시.
10. **§2 또는 §3에 신규 항목** — 논문 §4.1의 `T_total=2,000` vs `presets.py`의 `T=20000` 불일치 추가. 재현 시 어느 쪽을 쓸지 결정 필요.
11. **19행** — Lambert(1992) DOI를 논문이 인용한 `10.1080/00401706.1992.10485228`로 통일(또는 두 DOI 병기).
12. **13행 Case 3** — Cont(2001)와 함께 §3.2가 병기하는 **Embrechts, Klüppelberg, Mikosch (1997) *Modelling Extremal Events*** [17] 추가.
13. **14행 Case 4** — 논문 Eq.(28) a_i, b_i ~ LN(−½τ², τ²), E[a_i]=E[b_i]=1 및 코드 대응값 `mu_scale_logsigma=0.10`, `sig_scale_logsigma=0.10` 보강.
14. **15행 Case 5** — γ_i가 Case 5에서는 **동질**(`gamma_logsigma=0.0` → γ_i ≡ γ_mean)이고 Case 6에서만 이질(γ_i~N(1.0, 0.2²))임을 구분.
15. **3행** — DOI 10.1145/3770855.3817578, 저장소 URL https://github.com/jiazeee/FinStressTS 명시.

---

## 7. 확인 불가 항목 (명시)

- **`finprobts/simulators/har.py`, `heavy_tail.py`, `regime_switching.py`, `hawkes.py`, `zero_inflated.py`의 소스 본문**: 파일 존재와 클래스명·생성자 인자명은 `generator.py`의 import·호출부에서 100% 확인했으나, 각 파일의 코드 본문 자체는 열람하지 않음. 따라서 **각 시뮬레이터 내부 구현이 논문 Appendix A 수식과 일치하는지는 Case 1(garch.py)만 직접 검증**했고, Case 2~6은 (a) 논문 Appendix A 수식과 (b) generator.py의 인자 전달 및 `_har_coeffs_from_s_lambda()`를 통한 간접 검증에 그침. 다만 이 간접 근거만으로도 요약의 서술은 전부 뒷받침된다.
- **GitHub API 트리 조회**: `api.github.com` 엔드포인트는 빈 응답을 반환하여 전체 파일 목록을 확보하지 못함. 대신 raw.githubusercontent.com 직접 fetch로 개별 파일을 확인함.
- **Table 3(CRPS)의 일부 셀 정렬**: 원문 파일 266행이 스스로 밝히듯 Case 2 L4, Case 3 L5, Case 4 L2/L3/L4 행의 열 대응이 불명확. 본 검증에서는 사용하지 않았으므로 요약에도 영향 없음. 필요 시 PDF 대조 필요.
- **`Pi_block`의 실제 기본 전이행렬 값**: presets.py에서 `None`이며 `regime_switching.py` 내부 기본값을 열람하지 않아 **확인 불가**. 요약도 값을 명시하지 않았으므로 오류는 아니나, 우리 연구가 국면 전환빈도를 통제하려면 반드시 확인해야 할 항목.
- **논문 Figure 1~3의 실제 이미지**: 원문 수집본이 캡션만 포함. 확인 불가(요약 주장과 무관).
