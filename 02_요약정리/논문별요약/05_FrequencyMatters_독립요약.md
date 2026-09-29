# Frequency Matters: When Time Series Foundation Models Fail Under Spectral Shift — 독립 요약

> **공식 원본 PDF 대조 완료 (2026-09-23)**:
> King AI Labs 및 Microsoft Gaming 저자들의 공식 원본 PDF(`2511.05619_Frequency_Matters_TSFM_Spectral_Shift.pdf`, 총 10페이지) 본문(§1~§4), 부록(Appendix A~F), Table 1(PEP 벤치마크), Table 2(합성 회귀 MSE/MAE 6종), Table 3(합성 분류 Acc/AUC 4종)을 전수 대조하여 정밀 검증을 완료함.

---

## 1. 서지정보
- **제목**: Frequency Matters: When Time Series Foundation Models Fail Under Spectral Shift
- **arXiv ID**: 2511.05619
- **저자**: Tianze Wang, Sofiane Ennadir, John Pertoft, Gabriela Zarzar Gandler, Lele Cao, Zineb Senane, Styliani Katsarou, Sahar Asadi, Axel Karlsson, Oleg Smirnov (King AI Labs, Microsoft Gaming)
- **자료 형태**: 본문 5페이지 + 부록 A~F 총 10페이지 (공식 PDF 완본 보유)

---

## 2. 한 줄 요약
모바일 게임(Candy Crush Saga) 플레이어 참여도 예측(PEP)이라는 대규모 산업 과제에서 시계열 파운데이션 모델(TSFM, MOMENT)이 도메인 특화 모델(PatchTST, XGBoost, TabNet)보다 크게 뒤처짐을 보이고, 그 핵심 원인을 사전학습 데이터와 다운스트림 데이터 간의 지배 주파수 불일치인 **"스펙트럼 이동(Spectral Shift)"**으로 지목한 뒤, 통제된 합성 주파수 실험(Seen vs Unseen 대역)으로 TSFM 표현력 붕괴를 실증한 논문.

---

## 3. 핵심 문제의식 및 동기
- **공개 벤치마크와 산업 현장의 괴리**: TSFM이 표준 공개 벤치마크에서는 뛰어난 성능을 보이나, 산업 현장(불규칙 주기, 다양한 리듬을 갖는 텔레메트리)에서는 실질적 효과가 검증되지 않음.
- **핵심 가설**: 텍스트 LLM과 달리 시계열 데이터는 도메인 간 공통 언어 구조를 공유하지 않으며, 표본추출률(sampling rate), 해상도, 시간 역학(주기성)에 극도로 민감함. TSFM은 일반화 가능한 표현을 학습하기보다 사전학습에 포함된 특정 주파수 대역의 패턴을 "암기(memorization)"했을 가능성이 높음.

---

## 4. 방법론 및 실험 설계

### (1) 산업 사례: Player Engagement Prediction (PEP)
- **데이터**: Candy Crush Saga에서 추출한 다변량 시계열(MTS). 226일간 824,208개 샘플, 약 40,000명 플레이어, 32개 피처, 최대 512 타임스텝.
- **평가 프로토콜**:
  - `player-holdout`: 미지의 플레이어에 대한 평가.
  - `temporal-holdout`: 미래 28일 구간에 대한 제로샷(temporal zero-shot) 평가.
- **비교 모델**: PatchTST (파인튜닝된 트랜스포머), XGBoost, TabNet (정형 베이스라인), MOMENT-small (동결 인코더 + 선형 프로빙).

### (2) 스펙트럼 이동 통제 합성 실험 (Section 3.1 & 부록 C)
1. 사전학습 시계열 $x(t)$에 FFT를 적용해 상위 5개 지배 주파수 대역 $[f_{\text{low}}, f_{\text{high}}]$ 추출.
2. **Seen 대역**: $[f_{\text{low}}, f_{\text{high}}]$ 범위 내에서 균일 샘플링한 사인파의 합 + 가산 잡음.
3. **Unseen 대역**: $[f_{\text{low}}+\delta, f_{\text{high}}+\delta]$ (사전학습 대역과 겹치지 않는 미학습 주파수 대역).
4. 백본(MOMENT)은 완전히 동결(frozen)하고 선형 헤드만 학습시켜 인코더 표현의 질을 측정.

---

## 5. 핵심 실증 결과 (공식 PDF 전수 검증)

### (1) 산업 PEP 벤치마크 결과 (Table 1, p.3)
| Model | Accuracy (Player) ↑ | Accuracy (Temporal) ↑ | AUC (Player) ↑ | AUC (Temporal) ↑ | MSE (Player) ↓ | MSE (Temporal) ↓ | MAE (Player) ↓ | MAE (Temporal) ↓ |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **PatchTST** | **0.939** | **0.921** | **0.982** | **0.975** | **0.518** | **0.711** | **0.489** | **0.586** |
| **XGBoost** | 0.841 | 0.801 | 0.915 | 0.883 | 1.200 | 1.310 | 0.780 | 0.850 |
| **TabNet** | 0.836 | 0.795 | 0.911 | 0.852 | 1.304 | 2.140 | 0.852 | 1.169 |
| **MOMENT-small** | 0.758 | 0.701 | 0.791 | 0.749 | 2.250 | 2.854 | 1.151 | 1.324 |
- **결과 해석**: TSFM(MOMENT)은 도메인 특화 모델(PatchTST)뿐 아니라 단순 정형 트리 모델(XGBoost) 대비 모든 지표에서 최하위를 기록함.

### (2) 합성 회귀 실험 결과 (Table 2, p.4)
MOMENT 동결 백본 + 회귀 헤드 평가 (3회 반복 평균±표준편차):
| 기반 데이터셋 | Test MSE (Seen ✓) | Test MSE (Unseen ✗) | Test MAE (Seen ✓) | Test MAE (Unseen ✗) |
| :--- | :---: | :---: | :---: | :---: |
| **FordA** | **0.333 ± 0.010** | 0.366 ± 0.005 | **0.439 ± 0.005** | 0.457 ± 0.005 |
| **FordB** | **0.333 ± 0.010** | 0.358 ± 0.008 | **0.426 ± 0.005** | 0.456 ± 0.005 |
| **ElectricDevices** | **0.644 ± 0.002** | 0.952 ± 0.003 | **0.559 ± 0.001** | 0.791 ± 0.004 |
| **SmallKitchenAppliances** | **0.691 ± 0.059** | 0.877 ± 0.017 | **0.686 ± 0.031** | 0.752 ± 0.007 |
| **FaultDetectionA** | **0.689 ± 0.001** | 0.942 ± 0.004 | **0.666 ± 0.001** | 0.779 ± 0.001 |
| **FaultDetectionB** | **1.129 ± 0.172** | 2.005 ± 0.266 | **0.875 ± 0.084** | 1.140 ± 0.034 |
- **결과 해석**: 6개 데이터셋 전수에서 Seen 대역의 MSE/MAE가 Unseen 대역보다 일관되게 우수함 (특히 ElectricDevices, FaultDetectionA/B는 오차가 1.5~2배 급증).

### (3) 합성 분류 실험 결과 (Table 3, p.10)
| 기반 데이터셋 | Test Accuracy (Seen ✓) | Test Accuracy (Unseen ✗) | Test AUC (Seen ✓) | Test AUC (Unseen ✗) |
| :--- | :---: | :---: | :---: | :---: |
| **FordA** | **0.837 ± 0.004** | 0.829 ± 0.001 | **0.926 ± 0.002** | 0.901 ± 0.001 |
| **FordB** | 0.826 ± 0.000 | **0.838 ± 0.002** | 0.903 ± 0.002 | **0.926 ± 0.001** |
| **ECG5000** | **0.809 ± 0.020** | 0.591 ± 0.028 | **0.898 ± 0.007** | 0.692 ± 0.007 |
| **SwedishLeaf** | **0.689 ± 0.020** | 0.600 ± 0.040 | **0.796 ± 0.021** | 0.643 ± 0.028 |

---

## 6. 저자가 스스로 밝힌 한계점 (Limitations, Section 3.3)
1. **단일 산업 도메인 및 단일 TSFM 의존**: 모바일 게임 1개 산업과 MOMENT-small 1개 모델에 국한됨.
2. **합성 프로브의 단순성**: 사인파 기반의 주파수 조작은 현실 세계의 불규칙 표본추출, 버스트성(burstiness), 체제전환(regime shifts)을 포착하지 못함.

---

## 7. 우리 학위 논문 연구와의 직접적 접점 및 차별점

| 비교 축 | Frequency Matters (2511.05619) | 우리 연구 |
| :--- | :--- | :--- |
| **타겟 도메인** | 모바일 게임 텔레메트리 (단일) | **금융 주식 시장 (글로벌 + 한국 고난도 시장)** |
| **통제 실험 축** | **단일 축** (주파수/스펙트럴 시프트 1개) | **금융 다축 합성 통제** (변동성 군집, 팻 테일, 체제전환 등 6개/3개 축) |
| **합성 생성기** | 단순 정현파(sinusoidal) 합 + 노이즈 | **계량경제학 DGP** (GARCH, Student-t, Markov-Switching, Hawkes 등) |
| **평가 지표** | 점 예측 MSE/MAE, 분류 Accuracy/AUC | **확률적 불확실성 캘리브레이션 (CRPS, PIT, Empirical Coverage)** |
| **사후 보정** | 없음 (미해결 한계로 남김) | **동결 모델 대상 사후 캘리브레이션 보정 검증** |

- **시사점**: Frequency Matters의 "단순 사인파는 금융의 체제전환과 버스트성을 포착하지 못한다"는 한계 고백은, 우리 연구가 **"계량경제학 기반 다축 합성 통제 실험"**을 도입해야 하는 가장 직접적인 문헌적 당위성이 됨.
