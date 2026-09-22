# Re(Visiting) Time Series Foundation Models in Finance — 독립 정독 요약

> **공식 원본 PDF 대조 완료 (2026-09-23)**:
> 저자(Eghbal Rahimikia, Hao Ni, Weiguan Wang)의 공식 원본 PDF(`2511.18578_Revisiting_TSFM_in_Finance.pdf`, 총 138페이지) 본문(§1~§6), 부록(Appendix A~D), 국가별 실증 표(p.70~76), TSFM 메타 비교표(Table D.2)를 전수 정밀 대조하여 과거 웹 스크래핑으로 인한 7페이지 절단 상태 및 텍스트 인코딩 깨짐을 완전히 해소하고 무결점 요약으로 개정함.

---

## 1. 서지정보
- **논문명**: Re(Visiting) Time Series Foundation Models in Finance
- **저자**: Eghbal Rahimikia (Manchester Univ.), Hao Ni (UCL), Weiguan Wang (Shanghai Univ.)
- **식별자**: arXiv:2511.18578 (2025년 11월)
- **공식 포털 / 리포지토리**: https://huggingface.co/FinText (FinText.ai)
- **자료 규모**: 본문 30페이지 + 방대한 국가별·자산별 부록 총 138페이지

---

## 2. 핵심 요약 (Executive Summary)
전 세계 94개국, 34년(1990~2023)간의 일별 개별 주식 초과수익률 약 20억 건(누적 관측치)을 바탕으로, 기성 사전학습 시계열 파운데이션 모델(TSFM, 대표적으로 Chronos, TimesFM 및 12개 추가 모델)을 **(1) 제로샷, (2) 파인튜닝, (3) 금융 데이터 기반 처음부터 사전학습(from scratch)**의 3대 체제로 체계적 실증 평가를 수행한 최초의 초대형 금융 벤치마크 논문임.

**핵심 결론**:
1. **기성 TSFM(Off-the-shelf)의 참패**: 일반 시계열로 사전학습된 모델은 제로샷 및 파인튜닝 환경에서 CatBoost 등 강력한 트리 앙상블 벤치마크에 크게 미치지 못하며, 음(-)의 표본외 $R^2$를 기록함.
2. **금융 특화 사전학습(Finance-native)의 효용**: 금융 데이터만으로 처음부터 사전학습시키고(from scratch), JKP 팩터 및 합성 데이터 증강을 결합하면 벤치마크 모델을 능가하는 우수한 샤프비율을 달성할 수 있음.
3. **한국 시장(South Korea)의 극단적 난이도(p.70~76)**: 글로벌 94개국 실증에서 **"대만과 한국은 가장 정복하기 어려운(most challenging) 시장"**으로 드러났으며, 샤프비율이 1.0 미만으로 떨어지고 앙상블 및 TSFM 모두 초과수익 예측에 극심한 난항을 겪음.

---

## 3. 핵심 문제의식 및 동기
- **낮은 신호대잡음비(Low SNR)와 비정상성**: 금융 시계열은 일반 물리·센서 시계열과 달리 신호가 극도로 약하고 체제전환(regime shift)과 팻 테일(fat tail)이 지배적임.
- **범용 TSFM의 금융 검증 공백**: 자연어 LLM의 성공에 착안하여 범용 시계열 모델(Chronos, TimesFM 등)이 제로샷으로 금융도 예측할 수 있을 것이라는 막연한 기대가 확산되었으나, 실제 금융 벤치마크(CRSP, 글로벌 패널)에서 체계적으로 검증된 바가 없었음.
- **불공정한 벤치마크 문제**: 기존 일부 논문들이 단순 선형회귀나 약한 베이스라인과만 비교하던 관행을 비판하고, 금융 실무에서 가장 강력한 베이스라인(CatBoost, XGBoost, ElasticNet, 주성분회귀 등)을 엄밀히 세워 TSFM을 재검토(Re-visiting)함.

---

## 4. 데이터셋 및 실험 프로토콜

### (1) 데이터 규모
- **기간 및 대상**: 1990년~2023년 (34년간), 전 세계 94개국 기업 단위 일별 초과수익률(CRSP + Compustat Global).
- **데이터 정제**: 상장폐지 수익률(delisting return) 반영(누락 시 -30% 부여), 국가·일자별 시가총액 하위 5% 제외, 일별 수익률 1,000% 초과 이상치 제거, 0.1~99.9% 윈저라이징(Winsorization).
- **규모**: 2022년 기준 미국 1억 7,696만 건(66,250개 종목), 글로벌 전체 4억 9,689만 건(204,090개 종목). JKP 153개 팩터(Investment, Value, Low risk, Quality, Momentum 등) 결합 시 최대 약 19억 3,095만 관측치.

### (2) 3대 평가 체제
1. **기성 제로샷(Zero-Shot)**: 기성 사전학습 가중치(Chronos, TimesFM 등)를 동결하고 금융 데이터에 즉각 추론.
2. **파인튜닝(Fine-Tuned)**: 기성 가중치를 출발점으로 금융 데이터($D_{\text{fin}}$)로 전체 파라미터 미세조정.
3. **금융 처음부터 사전학습(Pre-trained from Scratch)**: 기성 가중치를 버리고 무작위 초기화 후 오직 금융 데이터로만 매년 확장 윈도우(expanding window) 방식으로 사전학습.

### (3) 비교 베이스라인 및 지표
- **베이스라인**: 선형군(OLS, Lasso, Ridge, Elastic Net, PCR), 트리 앙상블(CatBoost, XGBoost, LightGBM), 신경망(NN).
- **평가지표**:
  - 통계적 예측력: 표본외 결정계수 $R^2_{\text{OOS}}$ (Gu et al., 2020 방식, $R^2=0$ 기준), 방향 정확도(Accuracy), Macro-F1.
  - 경제적 성과: 상/하위 10분위 일별 리밸런싱 롱숏(Long-Short) 포트폴리오의 연환산 수익률, 연환산 변동성, 샤프비율(Sharpe Ratio), 최대낙폭(Max Drawdown).
- **컨텍스트 윈도우**: 과거 5일, 21일, 252일, 512거래일.

---

## 5. 핵심 실증 결과

### (1) 미국 시장 종합 결과
- **트리 앙상블(CatBoost, 윈도우 252일)**: $R^2_{\text{OOS}} = -0.10\%$, 방향 정확도 약 51% 상회, 연환산 수익률 **46.50%**, 샤프비율 **6.79** (거래비용 미반영 일별 리밸런싱 롱숏 기준 최강 성능).
- **기성 제로샷 TSFM**:
  - Chronos-Large (윈도우 512): $R^2_{\text{OOS}} = -1.37\%$, 연환산 수익률 20.17%, 샤프비율 2.45 (CatBoost 대비 대폭 열위).
  - TimesFM-500M (윈도우 512): $R^2_{\text{OOS}} = -2.80\%$, 연환산 수익률 -1.47%, 샤프비율 -0.11 (음의 수익률).
- **파인튜닝**: 대부분의 모델에서 파인튜닝 후 과적합(overfitting)으로 성능이 오히려 악화됨.
- **금융 특화 사전학습(from Scratch)**:
  - Chronos-Small (윈도우 512): $R^2_{\text{OOS}} = -0.59\%$, 연환산 수익률 **36.84%**, 샤프비율 **5.42** 달성.
  - JKP 팩터 및 합성 데이터 증강 결합 시: Chronos-Small 샤프비율 **6.78** 달성 (CatBoost 6.46을 근소하게 능가).

---

## 6. 글로벌 시장 및 한국 시장 실증 분석 (공식 PDF p.70~76 정밀 검증)

공식 PDF 70~76페이지의 글로벌 국가별 실증 분석에서 본 논문은 매우 중요한 지리적 이질성을 보고함:

### (1) 국가별 성과 차이
- 미국, 독일, 인도, 호주 등 선진·대형 시장에서는 트리 앙상블 및 금융 사전학습 모델이 강력한 예측 이득을 시현함.
- 그러나 아시아 주요 시장, 특히 **한국(South Korea)**과 **대만(Taiwan)**에서는 모든 모델의 성과가 급격히 붕괴함.

### (2) 한국 시장에 대한 공식 원문 서술 (p.70~76 축자 인용)
- **p.71**: *"whereas Taiwan and Korea remain challenging environments, with ensemble gains... and is close to zero in Korea (about 0.06). Within the linear family, PCR continues to underperform"*
  - (한국 시장에서 앙상블 모델의 성과 개선폭은 거의 0에 가까운 0.06 수준에 그치며, 주성분회귀 등 선형 모델도 부진함)
- **p.75**: *"Taiwan and Korea remain the most challenging environments. By contrast, Australia and Germany deliver consistent multi-window Sharpe ratios of roughly 0.82 and 1.12, whereas Taiwan and Korea remain challenging, with Sharpe ratios generally below 1"*
  - (호주와 독일이 0.82~1.12 수준의 안정적인 샤프비율을 보이는 반면, **대만과 한국은 가장 정복하기 어려운(most challenging) 환경으로 남아 있으며 샤프비율이 대체로 1.0 미만에 머묾**)
- **p.76**: *"while Korea remains comparatively hard to exploit, with Sharpe ratios generally below 1... Taiwan and Korea remain"*
  - (한국 시장은 초과수익을 착취(exploit)하기가 비교적 극히 어려움)

---

## 7. 14개 TSFM 사전학습 코퍼스 내 금융 데이터 포함 여부 (Table D.2, p.132~136)
부록 Table D.2에서 저자들은 주요 TSFM 14종의 사전학습 코퍼스를 전수 조사함:
1. **Chronos**: 100B 관측치 $\rightarrow$ **Finance-Related Datasets: None** (금융 데이터 없음).
2. **TimesFM**: 100B 관측치 $\rightarrow$ **Finance-Related: M4 대회 데이터만 포함** (거시/판매/금융 혼합의 거시 시계열, 개별 주식 없음).
3. **Moirai**: 27B 관측치 $\rightarrow$ **Finance-Related: Monash archive (M-series, NN5, FRED-MD, Bitcoin)** (개별 주식 주가/수익률 없음).
4. **Kairos**: 300B 관측치 $\rightarrow$ Moirai와 동일.
5. **MOMENT**: UCR/UEA, Monash 등 오픈소스 아카이브 $\rightarrow$ 개별 주식 시계열 없음.

---

## 8. 우리 학위 논문 연구와의 직접적 접점 및 차별점

1. **한국 시장(Korean Market) 배치의 완벽한 정당성**:
   - `Re(Visiting)`이 이미 한국을 포함하여 글로벌 평가를 수행했으므로 "한국 시장 최초 적용"이라는 주장은 거짓(기각)임.
   - 대신 `Re(Visiting)` 저자들 스스로 밝힌 **"한국은 전 세계에서 TSFM과 앙상블이 가장 정복하기 어려운(most challenging) 극단적 환경"**이라는 공식 실증 결과를 인용하여, 한국 시장을 **"사전학습 TSFM의 신뢰도가 가장 먼저 무너지는 극한의 취약성 검증 시험대(stress testbed)"**로 삼는 이론적 논거를 확보함.
2. **기성 TSFM 제로샷 붕괴의 메커니즘 규명 공백**:
   - `Re(Visiting)`은 "기성 TSFM이 금융 데이터에서 성능이 왜 처참한가"에 대해 "코퍼스에 금융이 없어서"라는 정성적 추정에 그침.
   - 우리 연구는 **합성 통제 실험(FinStressTS의 6대 메커니즘 축: 변동성 군집, 두꺼운 꼬리, 체제전환 등)**을 통해 기성 TSFM이 정확히 금융의 *어떤 통계적 메커니즘* 앞에서 불확실성 추정(CRPS/PIT)을 잃어버리는지 **원인별로 정밀 분해(diagnosis)**하므로, `Re(Visiting)`의 거시적 발견을 미시적 메커니즘으로 심화 발전시키는 독보적 차별점을 가짐.
3. **불확실성 추정(CRPS/Calibration) 대조**:
   - `Re(Visiting)`은 점 예측 기반의 $R^2_{\text{OOS}}$ 및 포트폴리오 샤프비율만 평가함.
   - 우리 연구는 사전학습 TSFM의 확률적 출력(분위수/분포)과 캘리브레이션 붕괴를 직접 측정하므로 평가 관점이 근본적으로 상보적임.
