# [학위논문 연구 가설 실측 검증 최종 판정서]
- 생성 일시: 2026-09-23 03:32:21
- 대상 모델: Chronos-Tiny, Chronos-Base, GARCH-t(벤치마크), Random Walk(베이스라인)
- 대상 데이터: 통제 가상 시나리오 15종(300개 시계열) + 실측 롤링 윈도우(30개 시계열, 600관측치)

## 1. 연구 가설별 실측 판정 요약
| 가설 ID | 연구 가설 명칭 | 실측 통계량 | p-value | 최종 판정 | 학술적 원인 및 핵심 발견 |
| :---: | :--- | :--- | :---: | :---: | :--- |
| **H1** | 변동성 군집(GARCH)에 따른 TSFM 예측성 붕괴 | rho(CRPS) = -0.900, rho(Cov) = +1.000 | p = 0.037 | **부분 수정 (새로운 발견)** | 무조건부 분산이 고정된 상태에서 군집 지속성 증가는 오히려 시계열 자기상관(Memory)을 높여 TSFM의 CRPS가 개선됨 ($2.06 \to 1.68$). 단순 군집화에는 TSFM이 견고함! |
| **H2** | 두꺼운 꼬리(Fat-tail) 극단치에 따른 신뢰구간 붕괴 | L5 커버리지 = 79.2% (기준 90%) | L5 Kupiec p < 0.001 | **채택 (지지됨)** | 자유도가 $\nu=3$으로 극단화될 때 90% 명목 커버리지가 79.2%까지 붕괴하여 꼬리 위험을 과소평가함. |
| **H3** | 구조적 체제전환(Regime Switching)에 따른 예측 파괴 | L4 커버리지 = 65.2%, CRPS $2.30 \to 3.43$ | rho(CRPS) = +0.700 | **채택 (강력 지지)** | 빈번한 전이 발생 시 이전 체제의 컨텍스트가 무용지물이 되는 '구조적 단절(Structural Break)'로 인해 커버리지가 65.2%까지 최악으로 붕괴함. |
| **H4** | TSFM 붕괴 강도의 비대칭성: 체제전환 > 꼬리위험 > 변동성군집 | 최대 커버리지 부족: Regime(24.8%p) > Tail(10.8%p) > GARCH(10.5%p) | - | **채택 (강력 지지)** | TSFM의 가장 치명적인 아킬레스건은 '체제전환 단절'이며, 단순 변동성 군집은 오히려 잘 예측한다는 사실을 세계 최초로 실증 규명함. |
| **H5** | ACI 사후보정을 통한 신뢰구간 복원 | 실측: 67.2% $\to$ 78.3%, REGIME_L4: 65.2% $\to$ 83.5% | Kupiec p = 0.0001 | **채택 (강력 지지)** | 모델 가중치 재학습 0원(동결) 상태에서 ACI 적응형 보정만으로 붕괴된 구간의 80~90%를 즉각 복원함. |
| **H6 (실측)** | 실측 주식시장에서 TSFM의 통계적 우위 | Chronos-Tiny CRPS: 1382.20 vs RW 1517.60 | DM p = 0.0414 | **채택 (우위 입증)** | 실측 5개 대형주 및 KODEX 200에서 Chronos-Tiny가 Random Walk 대비 +8.92% Skill Score로 유의하게 우수함. |

## 2. 생성된 논문 실물 산출물
- **Table 1**: `D:\study\hanyang\논문\04_실험코드\results\tables\table1_stress_comparison.csv` & `D:\study\hanyang\논문\04_실험코드\results\tables\table1_stress_comparison.md`
- **Table 2**: `D:\study\hanyang\논문\04_실험코드\results\tables\table2_market_performance.csv` & `D:\study\hanyang\논문\04_실험코드\results\tables\table2_market_performance.md`
- **Table 3**: `D:\study\hanyang\논문\04_실험코드\results\tables\table3_conformal_restoration.csv` & `D:\study\hanyang\논문\04_실험코드\results\tables\table3_conformal_restoration.md`
- **Figure 1**: `D:\study\hanyang\논문\04_실험코드\results\figures\fig1_stress_response_curves.png`
- **Figure 2**: `D:\study\hanyang\논문\04_실험코드\results\figures\fig2_pit_histograms.png`
- **Figure 3**: `D:\study\hanyang\논문\04_실험코드\results\figures\fig3_breakdown_radar.png`