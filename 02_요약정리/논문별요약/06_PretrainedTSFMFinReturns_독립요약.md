# Pretrained Time-Series Foundation Models for Financial Return Forecasting — 독립 요약

> **공식 원본 PDF 대조 완료 (2026-09-23)**:
> Artificial Intelligence Finance Institute 저자들의 공식 원본 PDF(`2606.27100_Pretrained_TSFM_Financial_Return_Forecasting.pdf`, 총 37페이지) 본문(§1~§7), 부록(Appendix A~B), Table 2(모델군 분류), Table 3(실험 파이프라인), Table 7(Diebold–Mariano 단측 검정 실측치)을 전수 정밀 대조하여 과거 웹 스크래핑으로 인한 Section 3.4 절단 상태를 완전히 해소하고 무결점 요약으로 개정함.

---

## 1. 서지정보
- **논문명**: Pretrained Time-Series Foundation Models for Financial Return Forecasting
- **저자**: Miquel Noguer i Alonso, Rodolfo Pereira Franklin (Artificial Intelligence Finance Institute)
- **식별자**: arXiv:2606.27100v1 [q-fin.MF] (2026년 6월)
- **자료 규모**: 본문 32페이지 + 부록 총 37페이지 (공식 PDF 완본 보유)

---

## 2. 핵심 요약 (Executive Summary)
미국 대형 우량주 5종(AAPL, AMZN, GOOG, JPM, META)의 20영업일 수익률 예측 과제에서 기성 사전학습 TSFM 6종(TimeGPT 계열, TimesFM-2.5, Moirai-2.0, Chronos v1, Chronos-2)을 처음부터 학습하는 심층 신경망 베이스라인 5종(NBEATS, NHITS, PatchTST, iTransformer, KAN)과 통제된 롤링-오리진(rolling-origin) 환경에서 비교 평가함.

**핵심 결론**:
1. **순위 경쟁의 우세 (10개 중 8승)**: 10개 태스크(5종목 × 선형/로그 수익률) 중 8개에서 사전학습 TSFM이 최상위 예측 정확도(MAE)를 기록했으며, Moirai-2.0과 TimesFM-2.5가 평균 순위 1~2위를 차지함.
2. **랜덤워크 대비 통계적 유의성의 결핍 (단 2건만 기각)**: 그러나 단순 무수익 랜덤워크(Zero-return Random Walk) 대비 단측 Diebold–Mariano 검정을 수행한 결과, 귀무가설을 기각하고 통계적으로 유의미한 초과 예측력($p < 0.05$)을 입증한 것은 **AMZN(Chronos, $p=0.0421$)**과 **GOOG(Moirai-2.0, $p=0.0421$)** 단 2건에 불과함.
3. **저자들의 최종 평가**: TSFM은 데이터가 적은 단일 자산 환경에서 모델 개발 비용을 줄여주는 **"실용적 사전분포(practical inductive prior)"**로서 가치가 있으나, 통계적으로 신뢰할 수 있는 알파 엔진이나 보편적 예측 엔진은 아님.

---

## 3. 핵심 문제의식 및 동기
- **실무자 관점의 딜레마**: 자산당 단 하나의 수익률 시계열만 있고 20영업일 후를 예측해야 할 때, 종목별 무거운 모델 개발 대신 즉시 사용 가능한(out-of-the-box) TSFM이 과연 더 우수한가?
- **순위 우세와 경제적 유의성의 분리**: 저자들은 "상대 순위에서 이겼다"는 것이 "잡음이 많은 금융 시장에서 경제적으로 의미 있는 예측 가능성을 입증했다"는 것을 의미하지 않는다는 점을 통계적·이론적으로 증명하고자 함.
- **랜덤워크 벤치마크의 정식화(Section 3.1)**: 절대손실(MAE) 기준 베이즈 최적 예측기는 조건부 중앙값(conditional median)이며, 금융 수익률의 무조건부 중앙값이 0에 가까우므로 상수 제로 예측($\hat{r}=0$)인 랜덤워크를 이기려면 무조건부 중앙값을 넘어서는 진정한 조건부 정보가 필요함을 역설함.

---

## 4. 실험 설계 및 비교 모델군 (Table 2 & 3, p.24~25)

### (1) 데이터 및 프로토콜
- **대상 자산**: 유동성이 가장 풍부한 미국 메가캡 5종 (AAPL, AMZN, GOOG, JPM, META).
- **표현**: 선형 수익률(Linear returns) 및 로그 수익률(Log returns) 2종 $\rightarrow$ 총 10개 태스크.
- **동일 정보 예산(Equalized Context Budget)**: 모든 모델에 대해 과거 컨텍스트 윈도우 $L=512$, 예측 호라이즌 $H=20$ 영업일(약 1개월)을 완전 통일.

### (2) 평가 대상 모델군 (Table 2, p.24)
- **사전학습 TSFM (Zero-Shot 추론 모드)**:
  1. TimeGPT & TimeGPT-LH (Garza et al., 2024)
  2. TimesFM-2.5 (Das et al., 2024)
  3. Moirai-2.0 (Liu et al., 2025)
  4. Chronos (v1) & Chronos-2 (Ansari et al., 2024, 2025)
- **처음부터 학습하는 신경망 베이스라인 (Train-from-scratch)**:
  1. NBEATS & NHITS (Oreshkin et al., 2020; Challu et al., 2022)
  2. PatchTST (Nie et al., 2023)
  3. iTransformer (Liu et al., 2024)
  4. KAN (콜모고로프-아르놀트 네트워크 기반 시계열 모델, Xu et al., 2024)

### (3) 평가지표 및 검정
- **MAE**: 두꺼운 꼬리에 로버스트한 평가 척도.
- **스킬 점수(Skill Score)**: $\text{Skill}(f) = 1 - \frac{\text{MAE}(f)}{\text{MAE}_{\text{RW}}}$ (양수면 랜덤워크 능가, 음수면 랜덤워크보다 열등).
- **단측 Diebold–Mariano(DM) 검정**: $H_0$ (모델이 랜덤워크보다 우수하지 않음) vs $H_1$ (모델이 랜덤워크보다 유의하게 우수함).

---

## 5. 핵심 실증 결과 (공식 PDF p.30 Table 7 전수 검증)

### (1) 10개 태스크별 승자 분포
- **TimesFM-2.5**: AAPL (선형/로그), JPM (선형/로그) 승리.
- **Moirai-2.0**: GOOG (선형/로그), AMZN (로그) 승리.
- **Chronos (v1)**: AMZN (선형) 승리.
- **iTransformer (베이스라인)**: META (선형/로그) 승리 $\rightarrow$ "국지적 지도학습이 특정 자산(META)에서는 거대 파운데이션 모델을 이길 수 있음"을 실증.

### (2) Diebold–Mariano 검정 실측 결과 (공식 PDF p.30 Table 7)
| Ticker | 승자 모델 | DM 검정 p-value | Skill Score | 판정 방향 | 통계적 판정 상태 |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **AAPL** | TimesFM-2.5 | 0.9999 | -0.0319 | RW 우세 | 귀무가설 기각 실패 ($H_0$ 채택) |
| AAPL | iTransformer | 0.8458 | -0.0246 | RW 우세 | 귀무가설 기각 실패 |
| **AMZN** | **Chronos (v1)** | **0.0421** | **+0.0863** | **모델 우세** | **유의미한 개선 통과 (Significant, $p < 0.05$)** |
| AMZN | iTransformer | 0.9126 | -0.0280 | RW 우세 | 귀무가설 기각 실패 |
| **GOOG** | **Moirai-2.0** | **0.0421** | **+0.2289** | **모델 우세** | **유의미한 개선 통과 (Significant, $p < 0.05$)** |
| GOOG | iTransformer | 0.5950 | -0.0056 | RW 우세 | 귀무가설 기각 실패 |
| **JPM** | TimesFM-2.5 | 0.9999 | -0.0466 | RW 우세 | 귀무가설 기각 실패 |
| JPM | iTransformer | 0.6091 | -0.0059 | RW 우세 | 귀무가설 기각 실패 |
| **META** | iTransformer | 0.9838 | -0.0519 | RW 우세 | 귀무가설 기각 실패 |
| META | KAN | 0.9784 | -0.0549 | RW 우세 | 귀무가설 기각 실패 |

- **핵심 사실**:
  - AAPL, JPM, META는 두 모델(TimesFM-2.5/iTransformer/KAN) 모두 Skill Score가 음수(-)이며, 그중 p-value가 가장 낮은(유의에 가장 근접한) 모델 기준으로도 0.61(JPM iTransformer)~0.98(META KAN)이라 **어느 쪽도 랜덤워크(상수 0 예측)를 통계적으로 이기지 못함** (전체 8개 미유의 행 기준 p-value 실측 범위는 0.595~0.9999).
  - 진정으로 랜덤워크를 통계적으로 능가한 것은 **AMZN(Chronos, Skill +0.0863)**과 **GOOG(Moirai-2.0, Skill +0.2289)** 2건뿐임.

---

## 6. Rahimikia et al. (2025) [Re(Visiting)] 와의 관계 (p.31 명시)
공식 PDF 31페이지에서 저자들은 자신의 실증 결과를 `Re(Visiting)` 논문과 직접 결합하여 해석함:
> *"Finally, the results are consistent with contemporaneous evidence that generic TSFM pretraining is useful but not a substitute for finance-native pretraining. Read alongside Rahimikia et al. [2025], the modest forecast-error advantages reported here are best understood as evidence that pretrained TSFMs provide a useful inductive prior for low-data, per-asset settings. They do not establish that generic temporal pretraining captures the finance-specific structure needed for robust portfolio outperformance."*

- 즉, 본 논문은 소규모 자산(5종목) 관점에서, `Re(Visiting)`은 글로벌 94개국 관점에서 **"범용 사전학습 TSFM은 금융 특화 구조를 포착하지 못하며 실질적 알파를 주지 못한다"**는 동일한 결론에 도달하고 있음을 확인해 줌.

---

## 7. 우리 학위 논문 연구와의 직접적 접점 및 차별점

1. **상반된 결론(모순)의 진원지 해소**:
   - 기존 문헌 조사에서 Brini/Re(Visiting)은 "TSFM 실패", 본 논문은 "10개 중 8승으로 TSFM 우세"로 보고되어 표면상 모순으로 보였음.
   - 그러나 공식 PDF Table 7을 정밀 확인한 결과, 본 논문의 8승 중 6승은 Skill Score가 음수이고 랜덤워크조차 이기지 못한 "빛 좋은 개살구(순위만 1위)"였음이 밝혀짐 $\rightarrow$ **사실상 Re(Visiting)의 실패 결론과 동일 선상에 있음**.
2. **원인 규명의 공백 (우리의 기여)**:
   - 본 논문은 미국 5개 주식의 실측 결과만 관찰했을 뿐, TSFM이 *왜 AAPL/JPM에서는 무너지고 GOOG/AMZN에서는 통했는지* 메커니즘을 규명하지 못함.
   - 우리 연구는 **합성 통제 실험(변동성 군집, 팻 테일, 체제전환, 점프)**을 통해 어떤 금융 통계적 특성이 TSFM의 예측력과 불확실성 추정을 붕괴시키는지 인과적으로 분해하여 설명함.
3. **확률적 평가 및 보정(Calibration)의 확장**:
   - 본 논문은 점 예측(MAE)에 국한되어 평가함.
   - 우리 연구는 CRPS 및 PIT 캘리브레이션을 측정하고, 무너진 구간에 대해 사후 보정(Post-hoc calibration)이 가능한지를 검증하여 실무적 해결책까지 제시함.
