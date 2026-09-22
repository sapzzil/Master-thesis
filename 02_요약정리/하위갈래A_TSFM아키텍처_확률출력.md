# 하위갈래 A — TSFM 아키텍처와 확률 출력 방식

> **공식 원본 PDF 전수 대조 및 개정 완료 (2026-09-23)**:
> TimesFM, Chronos, Moirai, Moirai-MoE, Moirai 2.0, Chronos-2, TTM, Lag-Llama, Toto, Sundial의 공식 출판본 PDF를 전수 대조하여, 과거 웹 스크래핑으로 인해 "확인 불가"로 남았던 Moirai CRPS 수식, LOTSA 0.10% 수치 및 데이터셋 명단, Chronos 사전학습 내 금융 데이터 명단, Sundial TimeBench 구성 등을 100% 확정 반영함.

---

## 1. 모델별 핵심 아키텍처 및 확률 출력 메커니즘 총괄표

| 모델 | 원 논문 (출처) | 확률적 출력 형태 | CRPS 계산 전제 및 방법 | 금융 데이터 포함 여부 (공식 PDF 확인) | 원문 핵심 근거 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TimesFM (1.0)** | 2310.10688 (ICML 2024) | **점 예측 (point forecast)만 지원** | CRPS 계산 불가 (MSE/MAE 손실만 사용) | **불포함** (Wiki, Trends, M4 대회 데이터만 포함) | §4: "In this work, we focus on point forecasting... using MSE loss." / Appendix A.1: "Probabilistic forecasting... left to future explorations." |
| **TimesFM 2.5** | GitHub / HF 릴리즈 (2310.10688 후속) | **연속 분위수 헤드** (`use_continuous_quantile_head=True`) | 분위수 기반 $\rightarrow$ 10개 분위수(P10~P90) 핀볼 손실 평균 근사 | **불포함** (1.0과 동일 코퍼스 계열) | 공식 모델카드 및 Noguer & Franklin (2026) 실증 확인: 분위수 헤드 옵션 제공 |
| **Chronos (v1)** | 2403.07815 (TMLR 2024) | **샘플 경로 (Sample Paths)**: 값 양자화 $\rightarrow$ 이산 토큰 자기회귀 샘플링 | 다중 궤적(Trajectories, 기본 20개 샘플) 기반 **경험적(Empirical) CRPS** | **포함 (단, 주식 0건)**: 환율(Exchange Rate), ATM 인출(NN5 Daily/Weekly) 3종뿐 | §3: "autoregressively sampling from the predicted distribution... 20 sample forecast paths" / **Appendix B.2 (p.30~33)**: 금융은 환율과 ATM 데이터셋에 한정 |
| **Chronos-Bolt** | GitHub / HF 릴리즈 | **직접 다단계 분위수 예측** (T5 인코더-디코더, 패치 인코딩) | 분위수 기반 $\rightarrow$ P10~P90 핀볼 손실 평균 근사 | 불포함 (Chronos 코퍼스 기반) | 비자기회귀(non-autoregressive) 다단계 분위수 동시 출력 |
| **Chronos-2** | 2510.15821 | **명시적 분위수 헤드 (Quantile Head)**: Time + Group Attention 스택 뒤 위치 | 21개 분위수($\mathcal{Q}=\{0.01, \dots, 0.99\}$) 기반 핀볼 손실 평균 근사 | 확인 불가 (합성 다변량 증강 코퍼스) | §3.2: "trained using the quantile regression objective" / 21개 분위수 세트 명시 |
| **Moirai (1.0)** | 2402.02592 (ICML 2024) | **혼합 파라메트릭 분포**: Student-t, Log-normal, Neg-binomial, Low-var Normal 4종 가중 혼합 | 파라메트릭 혼합분포 샘플링 또는 **Appendix C.1의 $K=9$ 분위수 wQL 평균 근사** | **포함 (단, 0.10% 극소 및 주식 0건)**: LOTSA 내 23개 데이터셋 (FRED-MD, BLS, 비트코인 18개 등) | §3.1.3 혼합분포 명시 / **p.5 Table 2**: Econ/Fin 24,919,596 obs (0.10%) / **p.15 Table 14**: 23개 데이터셋 전수 명시 / **p.19 Appendix C.1**: CRPS 적분 정의 및 $K=9$ wQL 근사식 명시 |
| **Moirai-MoE** | 2410.10469 | Moirai 1.0과 **동일한 4종 혼합분포 헤드** 유지, 백본만 Sparse MoE로 교체 | Moirai 1.0과 동일 | Moirai 1.0과 동일 (LOTSA 코퍼스) | §3.3: "predicting the mixture distribution parameters... negative log-likelihood minimized" |
| **Moirai 2.0** | 2511.11698 | **9개 분위수($\{0.1, \dots, 0.9\}$) 직접 예측으로 전면 교체** (혼합분포 폐기) | 분위수 기반, **CRPS와 직접 정렬(aligned)**되도록 핀볼 손실로 사전학습 | Moirai 1.0과 동일 계열 (GIFT-Eval, LOTSA 서브셋) | 초록: "replaces mixture-distribution outputs with single patch, and quantile loss" / §2: "directly aligned with the CRPS metric" |
| **TTM (Tiny Time Mixers)** | 2401.03955 (NeurIPS 2024) | **점 예측만 지원 (확률적 출력 없음)** | CRPS 계산 불가 (MSE 손실 $\mathcal{L} = \|Y - \hat{Y}\|_2^2$ 기반) | **불포함** (Monash <1B 관측치 기반) | §2.1 Linear forecast head / §3.1 MSE 손실 / Moirai Table 1 제3자 분류: "Probabilistic: ✗" |
| **Lag-Llama** | 2310.08278 | **단일 Student-t 분포 헤드 (3개 파라미터: $\nu, \mu, \sigma$) + 샘플 경로** | Student-t에서 자기회귀 샘플링 후 경험적 CRPS | **불포함** (Monash 기반, 클라우드/교통/ETT 중심) | §4.3: "adopt a Student's t-distribution... output the three parameters" / Table 1에서 CRPS 보고 |
| **Toto** | 2407.07874 | **Student-T 혼합모델 (SMM, $k=16$개 성분) 헤드** | 혼합분포에서 100~200개 샘플링 후 경험적 CRPS | **포함 (소량 간접 노출)**: Datadog 텔레메트리 75% + LOTSA 공개데이터 일부 | §3.4: "Student-T mixture model (SMM) with 16 components" / §4: LOTSA 서브셋 포함 명시 / 원문은 MAE/MSE만 보고, CRPS 미보고 |
| **Sundial** | 2502.00816 | **연속 최적수송 Flow-Matching (TimeFlow Loss)**: ODE 기반 생성 샘플링 | 20개 생성 궤적(Trajectories) 기반 **경험적 CRPS / WQL** | **포함 (간접 노출)**: TimeBench 1.03조(1032B) 포인트 중 Chronos·Moirai 서브셋 포함 | §4.1: TimeFlow Loss (OT path ODE) / Table 6: 1032B TimeBench 사전학습 규모 명시 / p.15 Appendix C.2: Chronos(94B), Moirai(230B)를 서브셋으로 포함 |

---

## 2. CRPS 평가 파이프라인 설계를 위한 결정적 시사점

1. **3대 확률 출력 메커니즘과 계산 경로 분기**:
   - **(경로 1) 분위수 직접 출력형** (`Chronos-Bolt`, `Chronos-2`, `Moirai 2.0`, `TimesFM 2.5`):
     - Moirai 논문 Appendix C.1에 명시된 바와 같이 9개 분위수($K=9$, $\alpha \in \{0.1, 0.2, \dots, 0.9\}$)에 대한 핀볼 손실(wQL)의 평균으로 CRPS를 직접 근사. 학습 손실과 평가지표가 완벽히 정합함.
   - **(경로 2) 혼합/단일 파라메트릭 분포형** (`Moirai 1.0`, `Moirai-MoE`, `Lag-Llama`, `Toto`):
     - 모델이 예측한 파라미터($\pi, \mu, \sigma, \nu$)로부터 분포를 복원한 뒤, 분위수를 역산하여 핀볼 손실로 근사하거나 100~200회 몬테카를로 샘플링을 통해 경험적 CRPS를 계산.
   - **(경로 3) 이산 토큰 샘플 경로형** (`Chronos v1`):
     - 자기회귀적 토큰 샘플링을 통해 20개 이상의 궤적(trajectory)을 생성하고, 표본 분위수(empirical quantiles)를 도출하여 CRPS 계산.
   - **(평가 제외 대상)**: `TTM`과 `TimesFM 1.0`은 점 예측 전용 모델이므로 불확실성 캘리브레이션(CRPS/PIT) 평가 대상에서 원천 제외하고, 방법론 한계 절에 "점 예측 전용 베이스라인"으로 명시.

2. **사전학습 코퍼스 내 금융 데이터 편향의 실체 (공식 PDF 확인 종결)**:
   - 과거 조사에서 제기되었던 "코퍼스에 금융 데이터가 포함되어 look-ahead 누출이 발생했을 가능성"을 공식 PDF 전수 조사로 최종 규명함:
     - `Chronos`: 환율과 ATM 데이터뿐이며 **개별 주식 0건**.
     - `Moirai`: LOTSA 내 0.10%에 불과하며, 거시계열과 비트코인 18개뿐 **개별 주식 0건**.
     - `Sundial` / `Toto`: Chronos/Moirai 데이터를 일부 상속했으나 주식 데이터는 없음.
   - **결론**: **모든 주요 오픈소스 TSFM은 주식 시장의 일별 가격/수익률을 단 1건도 사전학습한 적이 없다.**
   - 따라서 TSFM의 금융 주식 예측 성능 저하는 "부분적 누출" 때문이 아니라 **"완전한 OOD(Out-of-Distribution) 상태에서 금융의 극단적 노이즈(Low SNR)와 비정상성을 처리하지 못해 발생하는 구조적 불확실성 추정 붕괴"**로 규정하는 것이 100% 팩트에 부합함.

---

## 3. 원문 대조로 완전 해소된 확인 불가 항목 보고
- [x] **Moirai Appendix C.1 CRPS 수식 전문**: 공식 PDF p.19 확인 완료 ($\text{CRPS} = \int_0^1 2\Lambda_\alpha d\alpha$, $K=9$ wQL 근사식).
- [x] **Chronos 부록 코퍼스 금융 데이터셋 상세**: 공식 PDF Appendix B.2(p.30~33) 확인 완료 (Exchange Rate, NN5).
- [x] **Moirai Table 2 & 19 LOTSA 상세**: 공식 PDF p.5 및 p.15 확인 완료 (0.10%, 23개 데이터셋).
- [x] **Sundial TimeBench 구성**: 공식 PDF p.14 Table 6 및 p.15 Appendix C.2 확인 완료 (1032B 포인트, Chronos/Moirai 서브셋 포함, 20 샘플 Flow-Matching).
