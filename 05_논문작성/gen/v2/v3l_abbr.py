"""약어: 처음 나오는 곳에 원어를 적고, 뒤에서는 약어만 쓴다. 사용: python3 v3l_abbr.py <원고_md_dir>"""
import sys, os
F1 = '02_제1장_서론.md'; F2 = '03_제2장_관련연구.md'
E = [
 # 처음 나오는 곳: 원어 표기
 (F1, '이것이 위험 한도(VaR), 포지션 크기 조절,', '이것이 위험 한도(Value at Risk, VaR), 포지션 크기 조절,'),
 (F1, '단순 기준 모형(과거 변동성 기반 정규분포, RW)보다 나은가?', '단순 기준 모형(랜덤워크 가정에서 과거 변동성으로 만든 정규분포, RW)보다 나은가?'),
 (F1, '모델을 재학습하지 않는 온라인 사후보정(ACI-CQR)으로', '모델을 재학습하지 않는 온라인 사후보정(적응형 콘포멀 분위수 보정, ACI-CQR)으로'),
 (F1, 'RW와 GARCH(1,1)-t를 기준 모형으로 둔다.', 'RW와 변동성 군집을 표현하는 계량 모형인 GARCH(1,1)-t(2.1.2절)를 기준 모형으로 둔다.'),
 (F2, '달라지는 ARCH 모형을 제안하였고, Bollerslev(1986)는 여기에 어제의 분산을 더한 GARCH 모형으로 일반화하였다.',
      '달라지는 ARCH(autoregressive conditional heteroskedasticity) 모형을 제안하였고, Bollerslev(1986)는 여기에 어제의 분산을 더한 GARCH(generalized ARCH) 모형으로 일반화하였다.'),
 (F2, 'ARIMA 모형(Box, Jenkins, 1970)은', 'ARIMA(autoregressive integrated moving average) 모형(Box, Jenkins, 1970)은'),
 (F2, '분위수 손실과 연속 순위 확률 점수(CRPS)가 대표적이다.', '분위수 손실과 연속 순위 확률 점수(continuous ranked probability score, CRPS)가 대표적이다.'),
 (F2, '평가 지표는 예측 중앙값의 MAE였으며', '평가 지표는 예측 중앙값의 평균 절대오차(mean absolute error, MAE)였으며'),
 (F2, '15개 예측 모델(HAR, VAR,', '15개 예측 모델(HAR(heterogeneous autoregressive), VAR(vector autoregression),'),
 (F2, '점 예측(NMAE)과', '점 예측(정규화 평균 절대오차, NMAE)과'),
 # 뒤에서 다시 풀어 쓴 곳: 약어만
 (F2, '시계열 파운데이션 모델(time series foundation model, TSFM)은 이 발상을', '시계열 파운데이션 모델(TSFM)은 이 발상을'),
 (F2, 'VaR(Value at Risk)은 일정 기간', 'VaR은 일정 기간'),
]
d = sys.argv[1]; ok = bad = 0
for f, o, n in E:
    p = os.path.join(d, f); s = open(p, encoding='utf8').read()
    if s.count(o) != 1: print('BAD', f, s.count(o), o[:50]); bad += 1; continue
    open(p, 'w', encoding='utf8').write(s.replace(o, n)); ok += 1
print('applied', ok, 'bad', bad)
