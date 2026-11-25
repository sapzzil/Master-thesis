"""v3 4차: 외부 검토 2차 목록(A~E, 반복 정리 제외). 사용: python3 v3m_review.py <원고_md_dir>"""
import sys, os, csv
F0 = '01_표지_차례_국문요지.md'; F1 = '02_제1장_서론.md'; F2 = '03_제2장_관련연구.md'; F3 = '04_제3장_연구설계.md'
F4 = '05_제4장_금융특성의_영향.md'; F5 = '06_제5장_실증평가.md'; F6 = '07_제6장_사후보정.md'; F7 = '08_제7장_결론.md'
FR = '09_참고문헌.md'; FA = '10_부록A_실험절차이력.md'; FB = '11_부록B_특성강도비교.md'; FE = '13_ABSTRACT.md'
TAIL98 = '같은 분포 모양에서 꼬리 쪽 극단값의 영향이 커지는 98% 구간'
E = [
 # ── 국문요지 ──
 (F0, '새 데이터에 추가 학습 없이 예측구간을 함께 낸다.', '새 데이터에 추가 학습 없이 점 예측과 함께 예측구간을 낸다.'),
 (F0, '금융 데이터의 특성에 있는지 모델과 사용 설정에 있는지를 가리고', '금융 데이터의 특성에 있는지, 아니면 모델과 사용 설정에 있는지를 가리고'),
 (F0, '커버리지 오차는 금융 특성보다 모델과 설정에서 비롯되었다.', '본 실험 범위에서 커버리지 오차는 금융 특성보다 모델과 설정에 따라 더 크게 달라졌다.'),
 (F0, '16개 조건 중 절반이 실질 기준(80% ± 2%p)을 벗어났다. 반대로 특성을 실제 종목 중 가장 강한 수준으로 넣어도',
      '16개 조건 중 절반이 실질 기준(80% ± 2%p)을 벗어났다(±3%p로 넓히면 벗어난 조건은 5개). 반대로 특성을 실제 종목 중 가장 강한 수준(전환 빈도만 실측의 2배)으로 넣어도'),
 (F0, '두꺼운 꼬리와 잦은 국면 전환은 직관과 달리 80% 구간의 커버리지를 오히려 높였다.', '두꺼운 꼬리와 잦은 국면 전환은 80% 구간의 커버리지를 오히려 높였다.'),
 (F0, '평균 근처에 더 모여 있기 때문이며, 같은 이유로 98% 구간(Chronos-2)에서는 커버리지가 낮아졌다.',
      '평균 근처에 더 모여 있기 때문이다. ' + TAIL98 + '(Chronos-2)에서는 커버리지가 낮아졌다.'),
 (F0, '합성 데이터의 진단은 실제 주가에서도 같았다. 실제 10종목의 커버리지는 특성 없는 합성 데이터의 값과 평균 1.1%p 차이였고, 크게 어긋나는 조건은 합성 데이터에서 이미 드러났다. 그러나 분포 전체의 정확도(분위수 손실)는',
      '실제 10종목의 커버리지는 특성 없는 합성 데이터의 값과 평균 1.1%p 차이로 가까웠고, 크게 어긋나는 두 조건은 합성 데이터에서 이미 드러났다. 다만 2%p 이내의 작은 차이까지 합성 데이터로 맞힌다고 보기는 어렵다. 그러나 0.1~0.9 분위수 범위의 분포 정확도(분위수 손실)는'),
 (F0, '금융 수익률에 대한 TSFM 예측구간을 신뢰할 수 있는지는 데이터의 성질보다 어떤 모델을 어떤 설정으로 쓰느냐에 달려 있다.',
      '본 실험 범위에서 금융 수익률에 대한 TSFM 예측구간의 커버리지는 데이터의 성질보다 어떤 모델을 어떤 설정으로 쓰느냐에 따라 더 크게 달라졌다.'),
 (F0, '다만 분포의 정확도가 단순 기준 모형을 넘지 못하므로, 현재의 TSFM을 쓴다면 수익률을 맞히는 용도가 아니라 위험을 측정하는 용도로 한정하고, 설정 점검과 사후보정을 먼저 거쳐야 한다.',
      '다만 가장 나은 조건(1년·수익률)에서도 분포 정확도는 단순 기준 모형(RW) 수준이고 GARCH-t보다 낮았다. 따라서 현재의 TSFM을 쓴다면 설정 점검과 사후보정을 먼저 거쳐야 한다.'),
 # ── 1장 ──
 (F1, '이 모델들은 예측에 드는 수고를 크게 줄여 주어 주목받는다. 기존에는', '기존에는'),
 (F1, '수많은 종목과 지표를 다루는 금융 분야에서는 이런 범용성이 특히 매력적이어서, 금융 데이터에 TSFM을 적용하려는 연구도 빠르게 늘고 있다',
      '수많은 종목과 지표를 다루는 금융 분야에서도 TSFM을 적용하려는 연구가 빠르게 늘고 있다'),
 (F1, '1. 예측구간의 커버리지 오차의 원인은 금융 데이터의 성질보다 모델과 입력 설정에 있다.', '1. 본 실험 범위에서 예측구간의 커버리지 오차는 금융 데이터의 성질보다 모델과 입력 설정에 따라 더 크게 달라졌다.'),
 (F1, '중 절반이 실질 기준(80% ± 2%p)을 벗어났다. 가장 단순한 데이터에서 이미 80%에서 벗어났으므로 이 오차의 원인은 데이터가 아니라 모델과 설정이다. 반대로 특성을 실제 10종목 중 가장 강한 수준(L5)까지 넣어도',
      '중 절반이 실질 기준(80% ± 2%p)을 벗어났다(±3%p로 넓히면 벗어난 조건은 5개). 특성이 없는 데이터에서 생긴 오차이므로 금융 특성으로는 설명되지 않는다. 반대로 특성을 실제 10종목 중 가장 강한 수준(L5, 전환 빈도만 실측의 2배)까지 넣어도'),
 (F1, '같은 이유로 98% 구간에서는 커버리지가 낮아졌다(4.3.2절).', TAIL98 + '에서는 커버리지가 낮아졌다(4.3.2절).'),
 (F1, '3. 합성 데이터의 진단은 실제 주가에서도 성립한다.', '3. 합성 데이터의 결과는 실제 주가와 가까웠다.'),
 (F1, '따라서 실제 데이터에 쓰기 전에 합성 데이터로 이런 조건을 가려낼 수 있다.', '따라서 실제 데이터에 쓰기 전에 합성 데이터로 이런 조건을 가려낼 수 있다. 다만 2%p 이내의 작은 차이까지 맞힌다고 보기는 어렵다(5.4절).'),
 (F1, '구간 양 끝만이 아니라 분포 전체가 얼마나 맞는지를', '구간 양 끝만이 아니라 0.1~0.9 분위수 범위의 분포가 얼마나 맞는지를'),
 (F1, '따라서 TSFM 예측구간을 쓴다면 수익률 예측보다는 위험의 크기를 측정하는 용도로 한정하고, 보정을 거쳐야 한다.',
      '따라서 TSFM 예측구간을 쓴다면 설정 점검과 사후보정을 거쳐야 하며, 가장 나은 조건(1년·수익률)에서도 분포 정확도는 RW 수준이고 GARCH-t보다 낮다는 점을 전제해야 한다.'),
 (F1, '- 평가 관점: 꼬리가 두꺼운 분포에서 분산 기반 80% 구간의 커버리지는 오히려 올라가고 99% 근처 구간에서는 내려간다는 것을 이론 계산으로 보이고, 극단 분위수를 내는 Chronos-2의 98% 구간에서 실제로 확인하였다.',
      '- 평가 관점: 꼬리가 두꺼운 분포에서 분산 기반 80% 구간의 커버리지는 올라가고 98~99% 구간에서는 내려간다는 이론 계산을 TSFM 예측구간에 적용하여, 극단 분위수를 내는 Chronos-2의 98% 구간에서 확인하였다.'),
 # ── 2장 ──
 (F2, '실제로 일별 수익률의 자기상관은 0에 가깝고, 본 연구 표본에서도 종목별로 −0.10에서 +0.04 사이였다(5.5.1절).',
      '실제로 일별 수익률의 자기상관은 작아, 본 연구 표본에서도 종목별로 −0.10에서 +0.04 사이였다(5.5.1절). 표본이 커서 통계적으로 유의한 종목도 있지만, 방향을 예측하는 데 쓰기에는 작은 값이다.'),
 (F2, 'Moirai-2.0은 개발 단계에서 그 일부', 'Moirai-2.0은 그 일부'),
 (F2, 'Chronos는 개발 단계에서 공개 시계열과', 'Chronos는 공개 시계열과'),
 (F2, '개발 단계에서 공개 시계열과 합성 데이터로 사전학습되었으며, 다변량', '공개 시계열과 합성 데이터로 사전학습되었으며, 다변량'),
 (F2, '개발 단계에서 3,600만 개 계열로', '3,600만 개 계열로'),
 (F2, '(Gneiting, Balabdaoui, Raftery, 2007, p. 8)', '(Gneiting, Balabdaoui, Raftery, 2007)'),
 (F2, '모든 분위수 수준에 대한 분위수 손실을 평균한 것과 같다.', '모든 분위수 수준에 대한 분위수 손실을 평균한 값의 2배와 같다.'),
 (F2, '의 분위수 손실 평균을 CRPS의 근사로 사용한다(3.6.1절).', '의 분위수 손실 평균을 사용한다. 이 값의 2배가 0.1~0.9 범위에서 CRPS를 근사한 값이며, RW 대비 개선율처럼 비율로 비교하면 2배는 상쇄된다(3.6.1절).'),
 (F2, 'VaR은 일정 기간 동안', 'VaR는 일정 기간 동안'),
 (F2, '두 연구는 결론의 강도가 다르지만, 제로샷 TSFM이 금융 수익률의 점 예측에서 단순 기준을 크게 넘지 못한다는 점에서는 일치한다. 그러나 두 연구 모두 예측구간의 신뢰성은 다루지 않았다.',
      'Upadhyay(2026)는 평가 계획을 미리 고정한 뒤, 미국 지수선물(E-mini Nasdaq-100, S&P 500) 수익률에서 Chronos-2, TimesFM 2.5, Moirai 2.0 등 사전학습 모델을 5분~120분과 일 단위로 평가하였다. 어느 조건에서도 가격이 그대로라고 보는 무변화 예측보다 나은 경우가 없었으며, 80% 구간의 커버리지는 변동성 예측에 대해서만 보고하였다. 세 연구는 결론의 강도가 다르지만, 제로샷 TSFM이 금융 수익률의 점 예측에서 단순 기준을 크게 넘지 못한다는 점에서는 일치한다. 그러나 세 연구 모두 수익률 예측구간의 신뢰성은 다루지 않았다.'),
 (F2, '| Noguer i Alonso, Franklin(2026) | ○ | ○<br>(미국 5종목) | × | × | × |',
      '| Noguer i Alonso, Franklin(2026) | ○ | ○<br>(미국 5종목) | × | × | × |\n| Upadhyay(2026) | ○ | ○<br>(지수선물) | × | △<br>(변동성만) | × |'),
 # ── 3장 ──
 (F3, 'Noguer i Alonso, Franklin(2026)과 같은 종목(', 'Noguer i Alonso와 Franklin(2026)의 종목과 같음('),
 (F3, '같은 난수를 쓰므로 두 시나리오는 같은 데이터이며, 그림 4-1에서 값이 다른 것은 표본을 무작위로 뽑는 Chronos-T5뿐이다.',
      '같은 난수를 쓰므로 두 시나리오는 같은 데이터이며, 그림 4-1에서 값이 다른 것은 표본을 무작위로 뽑는 Chronos-T5뿐이다. 따라서 17개 시나리오 가운데 서로 다른 데이터는 16개이다.'),
 (F3, '약자 RW는 이 랜덤워크 가정에서 따왔다.', '약자 RW는 이 랜덤워크 가정에서 따왔으며, 2.6.1절의 선행연구가 쓴 랜덤워크(수익률 0을 예측하는 점 예측)와는 다르다.'),
 (F3, '- 분위수 손실: 9개 분위수의 pinball 손실 평균(CRPS 근사).', '- 분위수 손실: 9개 분위수의 pinball 손실 평균(2배 하면 0.1~0.9 범위의 CRPS 근사).'),
 (F3, '유의성은 Holm 보정(Holm, 1979) 후 p < 0.05로 판단하며', '유의성은 Holm 다중비교 보정(Holm, 1979) 후 p < 0.05로 판단하며'),
 (F3, '(시점과 실행 환경은 부록 A.1·A.2).', '(시점과 실행 환경은 부록 A.1·A.2). 평가 계획을 실험 전에 고정하는 방식은 금융 TSFM 평가에서도 쓰인다(Upadhyay, 2026).'),
 # ── 4장 ──
 (F4, '16개 TSFM 조건 중 L1에서 커버리지가 실질 기준(80% ± 2%p) 안에 든 것은 8개뿐이다. 금융 특성이 들어가기 전에 이미 모델과 입력 설정이 오차의 크기와 방향을 정하고 있다.',
      '16개 TSFM 조건 중 L1에서 커버리지가 실질 기준(80% ± 2%p) 안에 든 것은 8개뿐이다(±3%p로 넓히면 벗어난 조건은 5개). 한 달 조건에는 짧은 과거의 영향도 있다. Chronos-2를 뺀 한 달 조건 TSFM(75~78%)은 21일 표본의 평균과 표준편차를 그대로 쓴 정규분포의 이론 커버리지(77.5%)와 비슷하거나 그보다 조금 낮다. RW 한 달(77.6%)이 80%보다 낮은 것도 같은 이유이며, H5의 비교 기준인 RW는 이 추정 오차를 그대로 지닌 기준이다. 반면 Chronos-2는 한 달 조건에서도 79.8~81.5%로 80% 근처였다. 추정 오차를 반영하면 21일 자료로도 80% 구간을 만들 수 있으므로(t분포 예측구간), 목표는 한 달 조건에서도 80%로 둔다. 금융 특성이 들어가기 전에 이미 모델과 입력 설정에 따라 오차의 크기와 방향이 달라진다.'),
 (F4, '이론 계산이 예상한 대로 구간 수준이 높아질수록 꼬리와 국면 전환의 효과가 상승에서 하락으로 바뀌며, 98% 구간의 하락 폭(약 1%p)도 이론값과 비슷하다.',
      '98% 구간에서는 대체로 이론대로 하락하였고(꼬리의 1년·수익률은 0.0), 하락 폭(약 1%p)도 이론값(−1.0%p)과 비슷하다. 90% 구간은 조건마다 방향이 달라, 이론값(+2.4%p)에 가까운 것은 1년·수익률뿐이다.'),
 (F4, '1. 오차의 대부분은 특성이 아니라 모델·입력 설정에서 비롯된다.', '1. 본 실험 범위에서 오차는 특성보다 모델·입력 설정에 따라 크게 달라졌다.'),
 (F4, '꼬리와 국면 전환은 통념과 달리 80% 구간에 불리하지 않았다.', '꼬리와 국면 전환은 80% 구간에 불리하지 않았다.'),
 (F4, '같은 이유로 99% 근처 구간에서는 방향이 반대가 되어 Chronos-2의 98% 구간에서 실제로 커버리지가 낮아졌다(표 4-3, 4-4).',
      '같은 분포 모양에서 꼬리 쪽 극단값의 영향이 커지는 99% 구간에서는 이론상 방향이 반대가 되며(표 4-3), Chronos-2의 98% 구간에서도 커버리지가 낮아졌다(표 4-4).'),
 (F4, 'Holm 방법으로 보정한 p값이', 'Holm 방법으로 다중비교를 보정한 p값이'),
 (F4, '조건을 한 묶음으로 Holm 보정하였다', '조건을 한 묶음으로 Holm 다중비교 보정을 하였다'),
 (F4, 'Holm p는 16개 조건에 대해 보정한 p값이다.', 'Holm p는 16개 조건에 대해 다중비교를 보정한 p값이다.'),
 (F4, '(Wilcoxon, Holm 보정)에서도', '(Wilcoxon, Holm 다중비교 보정)에서도'),
 # ── 5장 ──
 (F5, '분포 전체의 정확도는 9개 분위수의 분위수 손실로 따로 본다.', '0.1~0.9 분위수 범위의 분포 정확도는 9개 분위수의 분위수 손실로 따로 본다.'),
 (F5, 'Holm p는 16개 조건에 대해 보정한 p', 'Holm p는 16개 조건에 대해 다중비교를 보정한 p'),
 (F5, '진한 막대는 Holm 보정 후 유의', '진한 막대는 Holm 다중비교 보정 후 유의'),
 (F5, '월 평균에 t검정, Holm 보정)을 적용하였다', '월 평균에 t검정, Holm 다중비교 보정)을 적용하였다'),
 (F5, '이 때문에 본 연구는 방향이 아닌 예측구간을 평가하였으며, 제6장의 사후보정도 실무적으로 중요하다.',
      '이 결과는 본 연구가 방향이 아닌 예측구간을 평가 대상으로 삼은 이유와 맞으며, 제6장의 사후보정이 실무적으로 중요함을 보여 준다.'),
 (F5, '1. 실제 주가에서도 오차는 모델과 입력 설정에서 비롯된다.', '1. 실제 주가에서도 커버리지는 시장·종목보다 모델과 입력 설정에 따라 크게 달라졌다.'),
 (F5, '3. 예측구간은 위험 측정에 쓸 때 의미가 있다. 탐색 분석에서 중앙값 부호로 매매하는 규칙은 계속 보유보다 못했지만, 구간 폭으로 비중을 조절하면 최대 낙폭이 −33.5%에서 −17~−25%로 줄었다. 이 효과는 구간의 커버리지가 맞을 때에만 의도대로 나타났다(5.5절).',
      '3. 탐색 분석에서 예측구간은 방향 매매보다 위험 크기 조절에 쓸 때 효과가 있었다. 중앙값 부호로 매매하는 규칙은 계속 보유보다 못했지만, 구간 폭으로 비중을 조절하면 최대 낙폭이 −33.5%에서 −17~−25%로 줄었다. 다만 이 효과는 RW 구간으로도 같았고(TSFM이 RW보다 나은 조건 없음), 구간의 커버리지가 맞을 때에만 의도대로 나타났다(5.5절).'),
 # ── 6장 ──
 (F6, '보정은 나머지 분위수를 바꾸지 않으므로 분포 전체의 정확도(제5장 H5)는', '보정은 나머지 분위수를 바꾸지 않으므로 분포의 정확도(제5장 H5)는'),
 (F6, '나머지 분위수(중앙값 등)는 바꾸지 않으므로 분포 전체의 정확도(H5)를', '나머지 분위수(중앙값 등)는 바꾸지 않으므로 분포의 정확도(H5)를'),
 (F6, '위반이 연속으로 발생하지는 않지만 변동이 큰 시기에는 위반이 다소 잦다는 뜻이다.',
      '전날 위반이 다음 날 위반으로 이어지지는 않았지만 변동이 큰 시기에는 위반이 다소 잦았다는 뜻이다. Christoffersen 검정은 바로 전날과의 관계만 보므로, 여러 날에 걸친 몰림은 잘 잡아내지 못한다.'),
 (F6, '제4장에서 오차의 주된 원인이 금융 특성이 아니라 모델·설정임을 보였고, 이 장에서 그 오차가 모델을 고치지 않고도 바로잡힌다는 것을 보였다. 두 결과를 종합하면 다음과 같은 실무 지침을 얻는다. TSFM을 금융 위험 측정에 쓸 때는 모델과 입력 설정을 먼저 점검하고, 사후보정을 기본으로 적용해야 한다.',
      '제4장에서는 본 실험 범위에서 오차가 금융 특성보다 모델·설정에 따라 크게 달라짐을 보였고, 이 장에서는 그 오차가 모델을 고치지 않고도 평균 커버리지 기준에서 바로잡힘을 보였다. 따라서 TSFM 예측구간을 쓴다면 모델과 입력 설정을 먼저 점검하고, 사후보정을 기본으로 적용해야 한다.'),
 # ── 7장 ──
 (F7, '| Wilcoxon, Holm 보정 |', '| Wilcoxon, Holm 다중비교 보정 |'),
 (F7, '| Friedman, Holm 보정 |', '| Friedman, Holm 다중비교 보정 |'),
 (F7, 'TSFM 예측구간의 오차는 크고 모델·설정마다 방향도 다르지만, 대부분 금융 데이터의 특성이 아니라 모델과 입력 설정에서 비롯된다(RQ1). 이 진단은 실제 주가에서도 성립하며,',
      'TSFM 예측구간의 오차는 크고 모델·설정마다 방향도 다르며, 본 실험 범위에서는 금융 데이터의 특성보다 모델과 입력 설정에 따라 더 크게 달라졌다(RQ1). 실제 주가의 커버리지도 특성 없는 합성 데이터와 가까웠고,'),
 (F7, '다만 분포의 정확도는 RW 수준이고 GARCH-t에는 조금 못 미치므로, TSFM 예측구간을 쓴다면 수익률 예측이 아니라 보정을 거친 위험 측정으로 용도를 한정해야 한다.',
      '다만 가장 나은 조건(1년·수익률)에서도 분포 정확도는 RW 수준이고 GARCH-t보다 낮았다. 따라서 TSFM 예측구간을 쓴다면 설정 점검과 사후보정을 거쳐야 한다.'),
 (F7, '3. TSFM 예측구간을 쓴다면 방향 예측이 아니라 위험 측정으로 용도를 한정해야 한다.',
      '3. TSFM 예측구간을 쓴다면 방향 예측에는 쓰지 않아야 하며, 위험 측정에 쓸 때도 정확도는 기준 모형 수준임을 전제해야 한다.'),
 (F7, '설정을 점검하고 보정을 거쳤을 때 TSFM 구간은 위험의 크기를 측정하는 도구로 의도대로 작동하였다.',
      '설정을 점검하고 보정을 거치면 TSFM 구간도 목표 변동성 전략과 VaR 한도에서 의도한 위험 수준을 지켰지만, RW 구간보다 나은 조건은 없었다.'),
 (F7, '따라서 "꼬리는 불리하지 않다"는 본 연구의 결과는 80% 구간에 대한 것이며 극단 위험에 그대로 적용할 수 없다.',
      '따라서 "꼬리는 불리하지 않다"는 본 연구의 결과는 80% 구간에 대한 것이며 극단 위험에 그대로 적용할 수 없다. 탐색 분석의 VaR 10%도 실무에서 쓰는 1~5%보다 덜 극단적인 한도이다.'),
 (F7, '결과를 본 뒤 정한 배율로 일괄 확대한 대조군보다 폭 효율이 낮았다.',
      '결과를 본 뒤 정한 배율로 일괄 확대한 대조군보다 폭 효율이 낮았다. 또한 ACI-CQR은 구간의 양 끝을 함께 조정하므로 하단 위반율(VaR)을 따로 맞추지 않는다.'),
 (F7, '본 연구에서 TSFM 예측구간의 신뢰성을 좌우한 것은 금융 데이터의 특성이 아니라 모델과 사용 설정, 그리고 사후보정 여부였다.',
      '본 연구의 실험 범위에서 TSFM 예측구간의 커버리지는 금융 데이터의 특성보다 모델과 사용 설정, 그리고 사후보정 여부에 따라 크게 달라졌다.'),
 (F7, '본 연구에서 TSFM의 분포 정확도는 단순 기준 모형을 넘지 못하였다. 대신 TSFM 예측구간이 금융 데이터에서 얼마나, 왜 어긋나는지를 진단하고, 이를 미리 점검하고 바로잡는 절차를 제시하였다는 데 의의가 있다. 이 점검과 보정은 모델 구조와 무관하므로 앞으로 공개될 모델에도 그대로 적용할 수 있다.',
      'TSFM의 분포 정확도는 가장 나은 조건에서도 단순 기준 모형(RW) 수준이었다. 본 연구는 TSFM 예측구간이 금융 데이터에서 얼마나, 어디에서 어긋나는지를 진단하고, 이를 미리 점검하고 바로잡는 절차를 제시하였다. 이 점검과 보정은 모델 내부 구조를 쓰지 않으므로 다른 사전학습 모델에도 같은 방식으로 적용할 수 있다.'),
 # ── 참고문헌 ──
 (FR, 'Gneiting, T., & Raftery, A. E. (2007). Strictly proper scoring rules, prediction, and estimation. *Journal of the American Statistical Association*, 102(477), 359–378.\n\nGneiting, T., Balabdaoui, F., & Raftery, A. E. (2007). Probabilistic forecasts, calibration and sharpness. *Journal of the Royal Statistical Society: Series B*, 69(2), 243–268.',
      'Gneiting, T., Balabdaoui, F., & Raftery, A. E. (2007). Probabilistic forecasts, calibration and sharpness. *Journal of the Royal Statistical Society: Series B*, 69(2), 243–268.\n\nGneiting, T., & Raftery, A. E. (2007). Strictly proper scoring rules, prediction, and estimation. *Journal of the American Statistical Association*, 102(477), 359–378.'),
 (FR, 'Vaswani, A., Shazeer, N.', 'Upadhyay, R. (2026). Do time-series foundation models forecast index-futures returns? A preregistered evaluation of models, metrics, and input representations. arXiv:2611.12141.\n\nVaswani, A., Shazeer, N.'),
 # ── 부록 ──
 (FA, 'RW 대비 분위수 손실 개선율은 1년·수익률 +1.03%에서', 'RW 대비 분위수 손실 개선율(예측 24,132건 전체로 계산하여, 평가 17,700건으로 계산한 표 5-2의 +0.9%와 조금 다름)은 1년·수익률 +1.03%에서'),
 (FA, '(Holm 보정 후 p < 0', '(Holm 다중비교 보정 후 p < 0'),
 (FA, '16개씩 하던 Holm 보정을', '16개씩 하던 Holm 다중비교 보정을'),
 (FB, '16개 조건에 대해 Holm 방법으로 보정한 p값이', '16개 조건에 대해 Holm 방법으로 다중비교를 보정한 p값이'),
 (FB, '보정 후 p = 0.060)은 보정 후 유의하지 않은 경우이다', '다중비교 보정 후 p = 0.060)은 다중비교 보정 후 유의하지 않은 경우이다'),
 # ── ABSTRACT ──
 (FE, 'with half of the 16 settings outside the 80% ± 2 percentage-point band.', 'with half of the 16 settings outside the 80% ± 2 percentage-point band (five outside a ±3-point band).'),
 (FE, 'Raising feature strength to the strongest observed level moved coverage mostly within 3 percentage points.',
      'Raising feature strength to the strongest level (the strongest observed value, or twice the observed maximum for regime-switching frequency) moved coverage mostly within 3 percentage points.'),
 (FE, "for the same reason, these features lowered the coverage of Chronos-2's 98% intervals.",
      "with the same distributional shape, the larger influence of tail extremes lowered the coverage of Chronos-2's 98% intervals."),
 (FE, 'These results show that the reliability of TSFM intervals on financial returns is governed by model and input settings rather than by stylized facts, and that synthetic experiments calibrated to real markets track real-stock coverage closely enough to flag badly miscalibrated models and settings before deployment.',
      'Within the scope of these experiments, the coverage of TSFM intervals on financial returns varied more with model and input settings than with stylized facts, and feature-free synthetic coverage was close enough to real-stock coverage to flag the badly miscalibrated settings observed here before deployment, though not to predict small deviations.'),
 (FE, 'reaching parity only in the best settings (one-year return input for all four models).', 'reaching parity only in the best settings (one-year return input for all four models) and remaining below GARCH-t.'),
 (FE, 'If current TSFMs are deployed in practice, their use should therefore be limited to risk measurement rather than return forecasting, after checking models and usage settings and applying training-free post-hoc calibration.',
      'If current TSFMs are deployed in practice, models and usage settings should therefore be checked first and training-free post-hoc calibration applied.'),
]

def table55(d):
    """표 5-5에 '연수익률(%)', '평균 비중' 열(원래 / 보정) 추가. 값은 E2_voltarget.csv(t5fix)."""
    here = os.path.dirname(os.path.abspath(__file__))
    R = {}
    for r in csv.DictReader(open(os.path.join(here, '../../../04_실험코드/results_v4_t5fix_econ/E2_voltarget.csv'), encoding='utf-8-sig')):
        R[(r['전략'], r['구간'])] = (float(r['연수익률%']), float(r['평균비중']))
    p = os.path.join(d, F5); L = open(p, encoding='utf8').read().split('\n')
    i = [k for k, l in enumerate(L) if l.startswith('**표 5-5')][0]
    n = 0
    for k in range(i, i + 30):
        l = L[k]
        if not l.startswith('|'):
            if n: break
            continue
        c = l.split('|')
        if c[1].strip() == '전략':
            c.insert(6, ' 연수익률(%) '); c.insert(7, ' 평균 비중 ')
        elif set(c[1].strip()) <= set('-:'):
            c.insert(6, '---'); c.insert(7, '---')
        else:
            name = c[1].strip() + ('' if c[2].strip() == '-' else ' ' + c[2].strip())
            if c[1].strip() == '계속 보유':
                a, w = R[('계속 보유', '-')]; c.insert(6, f' {a:.1f} '); c.insert(7, f' {w:.2f} ')
            else:
                a0, w0 = R[(name, '원래')]; a1, w1 = R[(name, '보정')]
                c.insert(6, f' {a0:.1f} / {a1:.1f} '); c.insert(7, f' {w0:.2f} / {w1:.2f} ')
        L[k] = '|'.join(c); n += 1
    open(p, 'w', encoding='utf8').write('\n'.join(L))
    return n

if __name__ == '__main__':
    d = sys.argv[1]; ok = bad = 0
    for f, o, n in E:
        p = os.path.join(d, f); s = open(p, encoding='utf8').read()
        if s.count(o) != 1: print('BAD', f, s.count(o), o[:60]); bad += 1; continue
        open(p, 'w', encoding='utf8').write(s.replace(o, n)); ok += 1
    print('applied', ok, 'bad', bad, '| 표 5-5 열 추가', table55(d) if os.environ.get('SKIP55') != '1' else '건너뜀')
