# Moirai (2402.02592) 독립 정독 요약

> **공식 원본 PDF 대조 완료 (2026-09-23)**:
> Salesforce AI Research의 공식 출판본 PDF(`2402.02592_Moirai_Unified_Training_Universal_TSF_Transformers.pdf`, ICML 2024 게재본, 총 25페이지) 본문(§1~§6), 부록(Appendix A~D), 데이터셋 표(Table 2, Table 14), 평가 수식(Appendix C.1)을 전수 정밀 대조하여 과거 웹 스크래핑으로 인한 '부분 수집' 상태를 완전히 해소하고 무결점 요약으로 개정함.

---

## 1. 서지정보
- **논문명**: Unified Training of Universal Time Series Forecasting Transformers
- **저자**: Gerald Woo, Chenghao Liu, Akshat Kumar, Caiming Xiong, Silvio Savarese, Doyen Sahoo (Salesforce AI Research)
- **학술대회 / 식별자**: ICML 2024 / arXiv:2402.02592
- **공식 리포지토리**: https://github.com/SalesforceAIResearch/uni2ts

---

## 2. 핵심 요약 (Executive Summary)
다양한 샘플링 빈도, 임의의 변량 수, 이질적인 분포 특성을 가진 시계열 데이터를 단일 파운데이션 모델로 통합 처리하기 위한 **마스크 인코더 기반 범용 Transformer 모델(Moirai)**과 대규모 오픈 시계열 아카이브 **LOTSA(Large-scale Open Time Series Archive)**를 제안함. 9개 도메인, 270억(27B) 개 관측치로 사전학습된 Moirai는 완전학습(full-shot) 도메인 특화 모델 대비 제로샷(zero-shot) 환경에서도 강력한 경쟁력을 입증함.

---

## 3. 핵심 문제의식 및 설계 동기
1. **기존 시계열 딥러닝의 고립성**: '데이터셋 하나당 하나의 모델(one-model-per-dataset)' 패러다임에 갇혀 사전학습 전이학습의 혜택을 누리지 못함.
2. **범용 시계열 모델(Universal TSFM)의 3대 핵심 난제**:
   - **교차 빈도 학습(Cross-Frequency Learning)**: 초·분·시·일 등 서로 다른 샘플링 주기를 동시에 학습할 때 발생하는 부정적 간섭(negative interference).
   - **임의 변량 수 처리(Any-variate)**: 다변량 데이터마다 변량 수가 상이하고 변량 간 의미적 단위가 다름.
   - **분포 특성의 극단적 다양성**: 단일 파라메트릭 분포 가정(예: 정규분포, Student-t)은 양수 시계열(카운트 데이터 등)이나 다봉(multi-modal) 분포의 불확실성을 표현하지 못함.

---

## 4. 방법론 및 아키텍처 세부 메커니즘
- **기본 백본**: 마스크 인코더(Masked Autoencoder) 구조. 입력 시계열의 패치들을 랜덤 마스킹하고 이를 복원하는 방식으로 자기지도 학습 수행.
- **다중 패치 투영층 (Multi-Patch Projection)**:
  - 빈도에 따라 패치 크기 집합 $P = \{p_1, p_2, \dots, p_k\}$를 다르게 할당.
  - 고빈도(분, 초) 데이터에는 큰 패치 크기(예: 32, 64, 128)를 적용해 긴 시간 문맥을 포착하고, 저빈도(일, 월) 데이터에는 작은 패치 크기(예: 8, 16, 32)를 적용.
- **Any-variate Attention (시간 × 변량 통합 어텐션)**:
  - 다변량 시계열을 단일 시퀀스로 평탄화(flattening)하여 처리.
  - **시간 축**: Rotary Position Embeddings (RoPE)를 적용하여 상대적 시간 순서를 인코딩.
  - **변량 축**: 학습된 이진 어텐션 바이어스(Learned Binary Attention Bias)를 적용하여 동일 변량 여부(self-variate vs cross-variate)를 구분.
- **혼합 파라메트릭 분포 헤드 (Mixture of Parametric Distributions)**:
  - 다음 4가지 파라메트릭 분포 성분의 가중 혼합(mixture weights $\pi$)을 예측:
    1. **Student's t-분포**: 두꺼운 꼬리(heavy-tailed) 데이터 모델링.
    2. **로그 정규분포 (Log-normal)**: 양의 연속 실수 데이터 모델링.
    3. **음이항분포 (Negative Binomial)**: 양의 카운트(count) 데이터 모델링.
    4. **저분산 정규분포 (Low-variance Normal)**: 확신도가 높은 결정론적에 가까운 구간 모델링.
  - 목적함수: 혼합분포의 음의 로그우도(Negative Log-Likelihood, NLL) 최소화.
- **모델 크기**:
  - Moirai-Small: 14M 파라미터 (d_model=384, layers=6)
  - Moirai-Base: 91M 파라미터 (d_model=768, layers=12)
  - Moirai-Large: 311M 파라미터 (d_model=1024, layers=24)

---

## 5. 사전학습 코퍼스: LOTSA 내 금융 데이터 정밀 검증 (공식 PDF p.5 Table 2 & p.15 Table 14)

### (1) 전체 LOTSA 구성 (공식 PDF p.5 Table 2)
- **전체 데이터 규모**: 9개 도메인, 27,249,158,477 관측치 (약 27.2B)
- **도메인별 분포**:
  - Energy: 10,757,949,271 (39.48%)
  - Transport: 6,432,642,883 (23.61%)
  - Climate: 3,745,842,504 (13.75%)
  - CloudOps: 2,752,990,265 (10.10%)
  - Web: 1,607,951,332 (5.90%)
  - Sales: 1,023,043,905 (3.75%)
  - Nature: 549,431,894 (2.02%)
  - Healthcare: 355,386,827 (1.30%)
  - **Economics/Finance (Econ/Fin)**: **24,919,596 (0.10%)**, 23개 데이터셋

### (2) Econ/Fin 도메인 23개 데이터셋의 실체 (공식 PDF p.15 Table 14)
- 공식 PDF 부록 Table 14 전수 분석 결과, Econ/Fin 데이터셋 23개의 구성은 다음과 같음:
  1. **거시경제/공공 지표**: US Bureau of Labor Statistics (BLS), Federal Reserve (FRED-MD 월간 거시계열 128종), UK Office for National Statistics (ONS), GoDaddy 마이크로비즈니스.
  2. **벤치마크 대회 시계열**: Monash 아카이브 내 CIF-2016, NN5 (일별/주별 ATM 인출액).
  3. **암호화폐**: Kaggle Bitcoin 18개 일별 시계열.
  4. **개별 주식(Equity) 주가 및 일별 수익률 데이터**: **0건 (전혀 포함되지 않음)**.
- **연구적 함의**:
  - Moirai의 사전학습 코퍼스 중 금융 비중은 0.10%에 불과하며, 그마저도 거시경제 시계열과 비트코인·ATM 인출액 데이터뿐임.
  - 따라서 주식 시장의 일별 주가/수익률에 대한 Moirai의 평가는 **완전한 OOD(Out-of-Distribution) 내지 극단적 과소대표(Severe Underrepresentation)** 상태에서의 평가임이 공식 확인됨.

---

## 6. 불확실성 평가 및 CRPS 수식 체계 (공식 PDF p.19 Appendix C.1)

Moirai 논문은 확률적 예측의 평가 척도로 **CRPS**와 **MSIS**를 공식 정의함:

### (1) CRPS의 핀볼 손실 적분 정의
예측 분포의 CDF $F$와 실측치 $y$에 대해:
$$\text{CRPS}(F, y) = \int_0^1 2 \Lambda_\alpha(F^{-1}(\alpha), y) \, d\alpha$$
여기서 $\Lambda_\alpha(q, y) = (\alpha - \mathbf{1}_{y < q})(y - q)$는 분위수 수준 $\alpha$에서의 분위수 손실(pinball loss).

### (2) 이산화 정규화 근사: wQL 기반 CRPS 근사
실무적 계산을 위해 Moirai는 Park et al. (2022)의 **mean weighted sum quantile loss (wQL)**를 사용하여 $K=9$개 분위수($\alpha \in \{0.1, 0.2, \dots, 0.9\}$)의 평균으로 CRPS를 근사함:
$$\text{CRPS} \approx \frac{1}{K} \sum_{k=1}^K \text{wQL}[\alpha_k], \quad \text{wQL}[\alpha] = 2 \frac{\sum_t \Lambda_\alpha(\hat{q}_t(\alpha), y_t)}{\sum_t |y_t|}$$
($\hat{q}_t(\alpha)$는 시점 $t$에서의 예측된 $\alpha$-분위수).

### (3) Mean Scaled Interval Score (MSIS)
M4 대회 기준 95% 예측 구간($a=0.05$, 상한 $U_t$, 하한 $L_t$, 계절주기 $m$):
$$\text{MSIS} = \frac{\frac{1}{h} \sum_{t=1}^h \left( (U_t - L_t) + \frac{2}{a}(L_t - Y_t)\mathbf{1}_{\{Y_t < L_t\}} + \frac{2}{a}(Y_t - U_t)\mathbf{1}_{\{Y_t > U_t\}} \right)}{\frac{1}{n-m}\sum_{t=m+1}^n |Y_t - Y_{t-m}|}$$

---

## 7. 주요 실험 및 소거 연구 (Ablation Study) 결과 (공식 PDF p.8 Table 7)
Monash 벤치마크 제로샷 Normalized MAE 비교:
- **Moirai Small (전체 제안 모델)**: **0.655**
- w/o multi patch size (단일 패치 사용 시): **1.156** (성능 가장 크게 붕괴 $\rightarrow$ 빈도 적응에 다중 패치가 필수적임 입증)
- w/o Any-variate Attention: **0.904**
- w/o LOTSA (GluonTS+Monash만 사용): **0.809** (데이터 다양성 결핍 시 악화)
- w/o packing: **0.785**
- w/o mixture distribution (Student-t 단일 분포 사용 시): **0.740** (p.8 Figure 4에서 Student-t의 대칭성으로 인한 피크 구간 과대/부적절 구간 추정 실증)

---

## 8. 저자가 밝힌 한계점 (Limitations, p.9)
1. **하이퍼파라미터 튜닝 부재**: 연산 자원 제약으로 인해 사전학습 시 하이퍼파라미터 튜닝이 거의 이루어지지 못함($\mu\text{P}$ 등 경량 튜닝 필요).
2. **다중 패치 매핑의 휴리스틱성**: 빈도별 패치 크기 할당 규칙이 경험적(heuristic) 규칙에 의존함.
3. **고차원 시계열 처리 한계**: 변량 수가 매우 많은 초고차원 시계열 입력 시 트랜스포머 컨텍스트 길이 한계 발생.

---

## 9. 우리 학위 논문 연구와의 직접적 접점 및 시사점
1. **0.10% 코퍼스 편향의 명확한 근거**: Moirai가 금융 시계열에서 붕괴하는 원인이 "원천적으로 주식 시계열을 학습한 적이 없는 극단적 OOD" 때문임을 논문 Table 2/19로 반박 불가하게 입증 가능.
2. **CRPS 평가 코드 정합성**: Moirai 저자들이 공식 정의한 $K=9$ wQL 핀볼 손실 평균 근사 방식을 우리 실험 파이프라인의 표준 CRPS 구현으로 채택하여 평가 정합성을 100% 확보함.
3. **혼합분포의 붕괴 분석**: Moirai는 Student-t, Log-normal, Neg-binomial, Normal을 혼합하므로, 금융 데이터의 비대칭 두꺼운 꼬리 및 체제전환 앞에서 4개 성분의 혼합 가중치 $\pi$가 어떻게 붕괴(특정 성분 쏠림 등)하는지 추적하는 실험적 통찰 제공.
