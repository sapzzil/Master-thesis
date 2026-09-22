# [Table 2] 실측 시장(미국 대형주 5종목 + KODEX 200) 롤링 윈도우 예측 성능 및 Diebold-Mariano 검정

| Model        |   CRPS (Unbiased) | Skill Score vs RW (%)   | 90% Coverage (%)   |     MAE |   PIT KS Stat |   DM Stat (vs RW) |   DM p-value (vs RW) |   DM Stat (vs GARCH) |   DM p-value (vs GARCH) |
|:-------------|------------------:|:------------------------|:-------------------|--------:|--------------:|------------------:|---------------------:|---------------------:|------------------------:|
| chronos-tiny |           1382.2  | +8.92%                  | 67.2%              | 1717.2  |        0.1817 |            -1.735 |               0.0414 |               -0.32  |                  0.3746 |
| chronos-base |           1535.01 | -1.15%                  | 71.5%              | 2033.89 |        0.16   |             0.156 |               0.562  |                1.031 |                  0.8488 |
| garch_t      |           1426.06 | +6.03%                  | 72.3%              | 1986.2  |        0.175  |            -0.785 |               0.2161 |                0     |                  0.5    |
| random_walk  |           1517.6  | +0.00%                  | 61.8%              | 1813.26 |        0.1783 |             0     |               0.5    |                0.785 |                  0.7839 |

- 표본: 2020~2024년 롤링 5개 윈도우 $\times$ 6개 자산 = 30개 시계열 $\times$ 20일 예측계 = 600 관측치
- `Skill Score`: $1 - \text{CRPS}_{\text{model}} / \text{CRPS}_{\text{RW}}$ (양수일수록 Random Walk 대비 우수)
- `DM Stat (HLN)`: Harvey, Leybourne, Newbold(1997) 유한표본 보정 일측 Diebold-Mariano 통계량
- `DM p-value`: $H_0: \text{Model} \ge \text{Benchmark}$ vs $H_1: \text{Model} < \text{Benchmark}$ ($p < 0.05$이면 통계적으로 유의하게 우수)