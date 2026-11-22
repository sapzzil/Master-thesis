# 2026-11-22 발표 자료 수정: 구성·사실·표기 (결정로그 참조)
import re, os, sys
D = sys.argv[1] if len(sys.argv) > 1 else '.'
def ed(name, pairs):
    p = os.path.join(D, name + '.html'); s = open(p).read()
    for a, b in pairs:
        if a not in s and b in s: continue
        if a not in s: raise SystemExit(f'{name}: 못 찾음 {a[:60]!r}')
        s = s.replace(a, b)
    open(p, 'w').write(s)
def aside(name, text):
    p = os.path.join(D, name + '.html'); s = open(p).read()
    s, n = re.subn(r'<aside>.*?</aside>', '<aside>' + text + '</aside>', s, flags=re.S)
    assert n == 1, name; open(p, 'w').write(s)

# ---- summary
ed('summary', [('그래서: 새 TSFM을 위험 관리에 쓰는 순서', '그래서: 새 TSFM을 위험 관리에 쓰는 순서(결론에서 다시)')])

# ---- bg1
ed('bg1', [
 ('TSFM이 내는 예측구간은 그대로 위험 한도가 되므로, 구간이 틀리면 투자 결정이 틀린다', 'TSFM은 내려받아 바로 예측구간을 내지만, 그 구간이 위험 한도와 투자 비중이 되므로 틀리면 결정이 틀린다'),
 ('<p class="bd">VaR, 손절 기준</p>', '<p class="bd">VaR, 변동성 목표 비중</p>'),
 ('예) 오늘 100원, 1억 원 투자', '예) 오늘 100원, 1억 원 투자, 하루 변동 약 2%'),
 ('97.3~102.7원 (±2.7%)<br>한도 초과가 실제로도 10거래일에 하루꼴', '97.3~102.7원 · 손실 한도 270만 원<br>초과가 실제로도 10거래일에 하루꼴'),
 ('98.5~101.5원 (±1.5%)<br>한도 초과가 잦다 → 위험을 작게 봄', '98.5~101.5원 · 손실 한도 150만 원<br>초과가 잦다 → 위험을 작게 봄'),
 ('95~105원 (±5%)<br>한도 초과가 거의 없다 → 투자를 과하게 줄임', '95~105원 · 손실 한도 500만 원<br>초과가 거의 없다 → 투자를 과하게 줄임'),
 ('금융에서는 이 구간이 그대로 위험 한도와 투자 비중이 됩니다.', '금융에서는 이 구간이 위험 한도와 투자 비중을 정하는 데 쓰입니다.'),
])
# ---- bg2
ed('bg2', [('구간이 맞는지는 실제 값이 들어온 날의 비율(커버리지)로만 판단할 수 있고, 점 예측 정확도로는 알 수 없다', '구간이 맞는지는 실제 값이 구간 안에 들어온 날의 비율(커버리지)로 판단하며, 점 예측 정확도로는 알 수 없다')])
# ---- related
ed('related', [
 ('<p class="bd">세기는 연구자가 정함, CRPS만 평가</p>', '<p class="bd">세기는 연구자가 정함, 구간 커버리지 미평가</p>'),
 ('<p class="bt">빈자리 ①</p>', '<p class="bt">빈자리 ① · N1</p>'),
 ('<p class="bt">빈자리 ②</p>', '<p class="bt">빈자리 ② · N2</p>'),
 ('<p class="bt">빈자리 ③</p>', '<p class="bt">빈자리 ③ · N3</p>'),
 ('Noguer i Alonso 외(2026)', 'Noguer i Alonso·Franklin(2026)'),
])
# ---- novelty 노트의 N 순서를 빈자리 순서와 맞춤(N1 진단 방식=①, N2 평가 대상=②, N3 보정=③): 이미 그 순서
# ---- synthgen
ed('synthgen', [('합성 데이터는 같은 난수 위에 실측 세기의 특성 하나만 얹어, 결과 차이가 그 특성 때문임을 보장한다', '합성 데이터는 같은 난수 위에 실측 세기의 특성 하나만 얹어, 결과 차이를 그 특성의 효과로 볼 수 있게 했다')])
# ---- hyp
ed('hyp', [
 ('"금융 특성이 구간을 망가뜨린다"는 기존 관점을 실험 전에 가설로 고정했다', '가설 7개와 판정 기준을 실험 전에 고정했다. RQ1의 H1~H3b가 "금융 특성이 구간을 망가뜨린다"는 기존 관점이다'),
 ('H1~H3이 지지되면 기존 관점이 맞다', 'H1~H3b가 지지되면 기존 관점이 맞다'),
])
# ---- r1a
ed('r1a', [('본문 4.1절 표 4-1', '본문 4.2절 표 4-1')])
# ---- r1b
ed('r1b', [
 ('<p class="bd">2%p 이상 하락은 2개 조합</p>', '<p class="bd">2%p 이상 하락은 2개 조건 · 전환 크기는 유의한 변화 없음</p>'),
 ('<p class="bd">꼬리 11개, 전환 빈도 7개 조합 · 전환 크기는 영향 없음</p>', '<p class="bd">유의한 상승: 꼬리 11개, 전환 빈도 7개 조건</p>'),
 ('본문 4.2절 표 4-2, 그림 4-2, 부록 A.4', '본문 4.3절 표 4-2, 그림 4-2, 부록 A.4'),
])
# ---- r1t5
ed('r1t5', [('<h2 class="title">실험 중 발견</h2>', '<h2 class="title">라이브러리 기본 설정의 함정</h2>'),
 ('이 문제가 특성 없는 합성 데이터에서 이미 그대로 드러났다는 점', '이 문제가 특성 없는 합성 데이터에서 먼저 드러났다는 점')])
# ---- r1c
ed('r1c', [
 ('특성 중 꼬리는 80% 구간에서는 오히려 커버리지를 높이고 98% 구간에서는 낮춰, 구간 수준에 따라 효과가 뒤집힌다', '꼬리는 80% 구간에서는 오히려 커버리지를 높이고, 98·99% 같은 극단 구간에서는 낮춘다'),
 ('<div class="box prob left"><p class="bt">98% 구간: 꼬리 때문에 덜 맞음</p><p class="bd">Chronos-2: 꼬리 4개 조건 중 3개 −0.8~−1.0%p, 국면 전환 8개 모두 −0.6~−1.0%p</p></div>\n<div class="box prob left"><p class="bt">작아 보여도 크다</p><p class="bd">99%에서 1.2%p 하락 = 한도 초과일 1% → 2.2%</p></div>',
  '<div class="box prob left"><p class="bt">99% 구간(이론): 꼬리 때문에 덜 맞음</p><p class="bd">99.0 → 97.8% = 한도 초과일 1% → 2.2%</p></div>\n<div class="box prob left"><p class="bt">98% 구간(실측, Chronos-2)</p><p class="bd">극단 분위수를 내는 유일한 모델. 꼬리 4개 조건 중 3개 −0.8~−1.0%p, 국면 전환 8개 모두 −0.6~−1.0%p</p></div>'),
 ('C3: 80% 구간 하나로 꼬리 위험을 판단하면 틀린다', 'C2: 구간 하나의 커버리지로 꼬리 위험을 판단하면 잘못된 결론에 이를 수 있다'),
])
# ---- r1ans
ed('r1ans', [
 ('따라서 커버리지 차이의 90%는 모델과 설정에서, 7%만 금융 특성에서 온다', '따라서 커버리지 차이의 90%는 모델·설정으로, 7%만 금융 특성으로 설명된다'),
 ('<p class="bd">영향 없음</p>', '<p class="bd">유의한 변화 없음</p>'),
 ('<p class="bd">군집이 가장 불리</p>', '<p class="bd">16개 조건 중 10개 지지, 모두 군집이 가장 불리</p>'),
 ('기존 관점(H1~H3)은 대부분 지지되지 않음 · 본문 4.5절, 부록 A.4', '기존 관점(H1~H3b)은 대부분 지지되지 않음 · 본문 4.4~4.5절, 부록 A.4'),
])
# ---- r2a
ed('r2a', [
 ('실제 주가의 커버리지는 특성 없는 합성 결과와 평균 1.1%p 차이여서, 합성 점검으로 실제를 미리 가려낼 수 있다', '실제 주가의 커버리지는 특성 없는 합성 결과와 평균 1.1%p 차이였고, 크게 어긋나는 조건은 합성에서 미리 가려낼 수 있다'),
 ('크게 어긋나는 조합은 합성에서 이미 그대로', '크게 어긋나는 조건은 합성에서 먼저 드러남'),
 ('합성 L1에서 이미 드러남(4.3)', '합성 L1에서 먼저 드러남(부록 A.3)'),
 ('크게 어긋나는 조합이 합성 데이터에서 이미 그대로 드러났다는 점', '크게 어긋나는 조건이 합성 데이터에서 먼저 드러났다는 점'),
])
# ---- r2b
ed('r2b', [
 ('분포 정확도는 가장 단순한 기준(RW)을 넘지 못해, TSFM을 수익률 예측 도구로 쓸 이유는 없다', '분포 정확도는 가장 단순한 기준(RW) 수준이어서, TSFM 구간은 수익률 예측보다 위험 측정에 맞다'),
 ('<p class="bt">왜 RW가 강한가</p><p class="bd">방향 예측이 어려워 "중심 0, 폭은 최근 변동"이 정답에 가깝다</p>', '<p class="bt">왜 단순 모형을 넘기 어려운가</p><p class="bd">일별 수익률은 방향이 거의 없어 내일 변동의 크기가 관건이고, 이는 RW·GARCH-t도 잘한다</p>'),
 ('RW가 강한 이유는, 일별 수익률은 방향을 거의 예측할 수 없어서 "중심은 0, 폭은 최근 변동 크기"라는 답이 이미 정답에 가깝기 때문입니다. 정리하면 TSFM은 수익률을 맞히는 도구로서는 기존의 단순한 방법보다 낫지 않습니다.', '단순 모형을 넘기 어려운 이유는, 일별 수익률은 방향을 거의 예측할 수 없어서 내일 변동의 크기를 얼마나 맞히느냐가 관건인데, 그것은 과거 변동으로 만드는 RW나 군집을 반영하는 GARCH-t도 잘하기 때문입니다. 정리하면 TSFM은 수익률을 맞히는 도구로서는 기존의 단순한 방법보다 낫지 않습니다.'),
])
# ---- r3how: 비교 칸을 순서처럼 보이는 화살표 대신 두 칸 비교로
ed('r3how', [
 ('<p class="bd">기록 중 k번째 점수 × 폭만큼 넓히거나 좁힘</p>', '<p class="bd">k번째 점수 × 폭만큼 넓히거나 좁힘</p>'),
 ('<div class="flow">\n<div class="box gray"><p class="bt">일괄 확대</p><p class="bd">몇 배로 넓힐지 결과를 봐야 앎</p></div>\n<x-connector class="arr big" head="end"></x-connector>\n<div class="box"><p class="bt">사후보정</p><p class="bd">그날까지의 실제값만 사용</p></div>\n<x-connector class="arr big" head="end"></x-connector>\n<div class="box ok"><p class="bt">배율을 몰라도 80%</p><p class="bd">좁은 구간은 넓히고 넓은 구간은 좁힘</p></div>\n</div>',
  '<div class="cols2">\n<div class="box gray"><p class="bt">일괄 확대</p><p class="bd">몇 배로 넓힐지 결과를 봐야 앎(좁혀야 할 때도 있음)</p></div>\n<div class="box ok"><p class="bt">사후보정: 배율을 몰라도 80%</p><p class="bd">그날까지의 실제값만 써서 좁은 구간은 넓히고 넓은 구간은 좁힘</p></div>\n</div>'),
])
# ---- r3a: 겹치는 칸 합침
ed('r3a', [
 ('<div class="box ok"><p class="kpi">80%</p><p class="bd">합성 340개·실제 19개<br>모두 복원(H6 지지)</p></div>\n<div class="box"><p class="bt">보정 후 79.8~80.7%</p><p class="bd">실제 주가 79.9~80.3%</p></div>',
  '<div class="box ok"><p class="kpi">80%</p><p class="bd">합성 340개·실제 19개 모두 복원(H6 지지)<br>보정 후 79.8~80.7%, 실제 79.9~80.3%</p></div>'),
])
# ---- r3limit
ed('r3limit', [
 (' · 금융 특성은 "언제 틀리는가"에 크게 작용 · 본문 6.6절', ' · 본문 6.6절'),
 (' 이 결과는 금융 특성, 특히 변동성 군집과 국면 전환이 "언제 틀리는가"에는 크게 작용한다는 뜻이기도 합니다.', ' 시기에 따라 다르게 보정하는 방법은 향후 연구로 남겼습니다.'),
])
# ---- explore
ed('explore', [
 ('<h2 class="title">활용</h2>', '<h2 class="title">보정 구간의 활용(탐색 분석)</h2>'),
 ('보정된 구간은 방향 예측이 아니라 위험 한도와 투자 비중을 정하는 데서 효과를 냈다', '구간은 방향 예측보다 위험 크기를 잴 때 쓸모가 있고, 보정은 의도한 위험 수준을 지키게 했다'),
 ('<div class="box ok left"><p class="bt">VaR 10% 한도</p><p class="bd">한도 초과일 5.5~11.9% → 8.6~10.8%<br>검정 통과 조합 8개 → 14개</p></div>\n<div class="box ok left"><p class="bt">변동성 목표 비중</p><p class="bd">최대 낙폭 −33.5% → −17~−25%<br>실현 변동은 목표의 1.05~1.14배</p></div>\n<div class="box gray left"><p class="bt">방향 매매</p><p class="bd">모두 계속 보유(연 25.4%)보다 못함<br>방향 적중률 49~52%</p></div>',
  '<div class="box gray left"><p class="bt">왼쪽: 방향 매매</p><p class="bd">모두 계속 보유(연 25.4%)보다 못함<br>방향 적중률 49~52%</p></div>\n<div class="box left"><p class="bt">오른쪽: 구간 폭으로 비중 조절</p><p class="bd">최대 낙폭: 계속 보유 −33.5% → −17~−25%<br>TSFM 구간과 RW 구간의 차이는 없음</p></div>\n<div class="box ok left"><p class="bt">보정이 바꾼 것</p><p class="bd">실현 변동/목표 0.88~1.22 → 1.05~1.14배<br>VaR 10% 검정 통과 조건 8개 → 14개</p></div>'),
 ('본문 5.5절, 그림 5-4', '본문 5.5절, 표 5-5·5-6, 그림 5-4'),
])
aside('explore', '가설 검정과 별개로, 이 구간을 실제 투자 규칙에 써 보는 탐색 분석도 했습니다. 왼쪽 그림은 예측 중앙값의 부호로 사고파는 방향 매매입니다. 모두 계속 보유보다 못했고, 방향 적중률은 49에서 52%로 동전 던지기 수준이었습니다. 오른쪽 그림은 구간 폭으로 내일 변동을 추정해 보유 비중을 정하는 변동성 목표 전략입니다. 최대 낙폭이 계속 보유의 −33.5%에서 −17에서 −25%로 줄었습니다. 다만 이것은 비중을 조절하는 규칙 자체의 효과이고, TSFM 구간을 쓴 경우와 RW 구간을 쓴 경우의 차이는 없었습니다. 보정이 바꾼 것은 위험 수준을 의도대로 지키게 한 부분입니다. 보정 전에는 실현 변동이 목표의 0.88에서 1.22배로 조건마다 달랐는데, 예를 들어 너무 넓었던 TimesFM 1년·가격은 위험을 덜 써서 0.88배였습니다. 보정 후에는 모든 조건이 1.05에서 1.14배로 모였습니다. 구간 하단을 VaR 10% 한도로 쓸 때도, 10종목 중 8종목 이상에서 검정을 통과한 조건이 보정 전 8개에서 보정 후 14개로 늘었습니다. 그러니 TSFM 구간은 방향이 아니라 위험의 크기를 잴 때 쓸모가 있고, 그것도 커버리지가 맞을 때에만 의도대로 작동합니다.')

# ---- concl
ed('concl', [
 ('<h2 class="title">결론</h2>', '<h2 class="title">세 질문의 답과 결론</h2>'),
 ('<div class="box"><p class="bt">진단 · RQ1·RQ2</p><p class="bd">평균 커버리지 수준은 모델·입력 설정이 정한다(75~88%). 특성의 영향은 대부분 3%p 이내, 실제 주가도 같다</p></div>\n<div class="box ok"><p class="bt">처방 · RQ3</p><p class="bd">재학습 없는 보정으로 모든 경우 평균 80% 복원. 대가는 5~48% 넓은 구간</p></div>\n<div class="box prob"><p class="bt">남는 것</p><p class="bd">금융 특성은 "언제 틀리는가"에 작용한다. 평온·격변 시기의 차이와 극단 구간은 보정이 일부만 메운다</p></div>',
  '<div class="box"><p class="bt">RQ1 진단</p><p class="bd">평균 커버리지 수준은 모델·입력 설정이 정한다(75~88%). 특성의 영향은 대부분 3%p 이내</p></div>\n<div class="box"><p class="bt">RQ2 실증</p><p class="bd">실제 주가도 합성과 평균 1.1%p 차이. 분포 정확도는 RW 수준, GARCH-t에는 조금 못 미침</p></div>\n<div class="box ok"><p class="bt">RQ3 처방</p><p class="bd">재학습 없는 보정으로 모든 경우 평균 80% 복원. 대가는 5~48% 넓은 구간</p></div>'),
 ('<div class="box new"><p class="bt">합성 L1 점검</p><p class="bd">크게 어긋나면 탈락 · C1</p></div>', '<div class="box new"><p class="bt">합성 L1 점검</p><p class="bd">크게 어긋나면 탈락</p></div>'),
 ('<div class="box fix"><p class="bt">사후보정 붙이기</p><p class="bd">재학습 없음 · C2</p></div>', '<div class="box fix"><p class="bt">사후보정 붙이기</p><p class="bd">재학습 없음</p></div>'),
 ('<div class="box final"><p class="bt">위험 측정에 사용</p><p class="bd">VaR·투자 비중 · C4</p></div>', '<div class="box final"><p class="bt">위험 측정에 사용</p><p class="bd">VaR·투자 비중, 방향 예측 아님</p></div>'),
 ('<div class="flow">\n<p class="memo" style="flex:1;">방향 예측(수익률 맞히기)에는 쓰지 않는다: 분포 정확도는 RW 수준, 방향 적중률 49~52%</p>\n<div class="box prob" style="flex:1;"><p class="bt">극단 구간은 따로 점검 · C3</p><p class="bd">98%·99% 구간에서는 꼬리·전환이 커버리지를 낮춘다</p></div>\n</div>',
  '<div class="box prob left"><p class="bt">보정 후에도 남는 것</p><p class="bd">복원은 평균 기준이다. 변동이 큰 시기의 차이(10.1 → 2.9%p)와 위반 몰림이 일부 남고, 98% 같은 극단 구간에서는 꼬리·전환이 커버리지를 낮춘다(Chronos-2)</p></div>'),
 ('평균 수준은 모델과 설정이 정하고, 금융 특성은 언제 틀리는지에 작용한다 · 본문 7.1절 표 7-1', '가설 판정: H1 일부 지지, H2·H3a·H3b·H5 미지지, H4 16개 중 10개, H6 지지 · 본문 7.1절 표 7-1, 7.2절'),
])
aside('concl', '결론입니다. 세 질문의 답을 이어 보면 이렇습니다. RQ1, 80% 구간의 평균 커버리지 수준은 금융 특성보다 모델과 입력 설정이 정했습니다. 특성이 없는 데이터에서도 75에서 88%로 갈렸고, 특성을 강하게 해도 대부분 3%p 안에서만 움직였습니다. RQ2, 이 진단은 실제 주가에서도 성립해서 합성과 실제의 차이가 평균 1.1%p였고, 분포 전체의 정확도는 RW 수준, GARCH-t에는 조금 못 미쳤습니다. RQ3, 남은 오차는 재학습 없는 사후보정으로 모든 경우 평균 80%로 되돌릴 수 있었고, 대가는 5에서 48% 넓은 구간이었습니다. 그래서 새 TSFM을 위험 관리에 들일 때는, 라이브러리 기본값까지 포함해 모델과 설정을 합성 데이터로 먼저 점검하고, 사후보정을 붙이고, 수익률 예측이 아니라 위험 측정에 쓰는 순서를 제안합니다. 다만 복원은 평균 기준입니다. 변동이 큰 시기와 평온한 시기의 차이, 위반이 몰려 오는 문제가 일부 남고, 98% 같은 극단 구간에서는 꼬리와 국면 전환이 커버리지를 낮췄습니다. 그래서 이 결론은 80% 구간과 평균 커버리지에 한정해서 말씀드립니다.')

# ---- contrib
ed('contrib', [
 ('이 연구는 새 TSFM을 위험 관리에 들이기 전의 점검·보정 절차와 그 근거를 남긴다', '이 연구는 새 TSFM을 위험 관리에 들이기 전의 점검 방법과 그 근거를 남긴다'),
 ('기여와 근거 · 앞에서 예고한 네 가지', '기여와 근거 · 3쪽에서 예고한 네 가지'),
 ('<div class="row3"><div class="box ok left"><div class="row-t"><p class="cc">C1</p><p class="bt">점검 절차</p></div></div><div class="box left"><p class="bd">합성과 실제의 커버리지 차이 평균 1.1%p. 88%(TimesFM 1년·가격)와 14%(기본 설정 Chronos-T5)가 합성에서 이미 그대로 드러남</p></div><div class="box gray"><p class="bt">4.3, 5.1</p></div></div>',
  '<div class="row3"><div class="box ok left"><div class="row-t"><p class="cc">C1</p><p class="bt">방법론</p></div></div><div class="box left"><p class="bt">실측 세기 합성 실험을 실제 적용 전 점검 절차로</p><p class="bd">합성과 실제의 차이 평균 1.1%p. 88%(TimesFM 1년·가격)와 14%(기본 설정 Chronos-T5)도 합성에서 먼저 드러남</p></div><div class="box gray"><p class="bt">5.4, 부록 A.3</p></div></div>'),
 ('<div class="row3"><div class="box ok left"><div class="row-t"><p class="cc">C2</p><p class="bt">처방 검증</p></div></div><div class="box left"><p class="bd">합성 340개·실제 19개 모두 평균 80% 복원. 대가는 폭 5~48%, 시기 차이 10.1 → 2.9%p</p></div><div class="box gray"><p class="bt">6.2~6.4</p></div></div>\n<div class="row3"><div class="box ok left"><div class="row-t"><p class="cc">C3</p><p class="bt">평가 관점</p></div></div><div class="box left"><p class="bd">꼬리 L5의 80% 구간 커버리지 86.6%(이론)·86.3%(실측), 98% 구간에서는 오히려 하락</p></div><div class="box gray"><p class="bt">4.4</p></div></div>\n<div class="row3"><div class="box ok left"><div class="row-t"><p class="cc">C4</p><p class="bt">실증·실무</p></div></div><div class="box left"><p class="bd">TSFM 4종 × 입력 4개, 두 시장 24,132건을 같은 절차로 전부 보고. VaR 통과 조합 8 → 14개, 최대 낙폭 −33.5% → −17~−25%</p></div><div class="box gray"><p class="bt">3.3, 6.5</p></div></div>',
  '<div class="row3"><div class="box ok left"><div class="row-t"><p class="cc">C2</p><p class="bt">평가 관점</p></div></div><div class="box left"><p class="bt">구간 하나의 커버리지로 꼬리 위험을 판단하지 않는다</p><p class="bd">꼬리 L5의 80% 구간 86.6%(이론)·86.3%(실측), Chronos-2의 98% 구간에서는 하락</p></div><div class="box gray"><p class="bt">4.3.2</p></div></div>\n<div class="row3"><div class="box ok left"><div class="row-t"><p class="cc">C3</p><p class="bt">실증</p></div></div><div class="box left"><p class="bt">최신 TSFM 4종을 두 시장에서 같은 절차로 평가</p><p class="bd">입력 4개, 24,132건. 가설 7개를 실험 전에 고정하고 지지되지 않은 결과까지 전부 보고</p></div><div class="box gray"><p class="bt">3.3, 3.6</p></div></div>\n<div class="row3"><div class="box ok left"><div class="row-t"><p class="cc">C4</p><p class="bt">실무</p></div></div><div class="box left"><p class="bt">설정 점검과 사후보정이 필요함을 보임</p><p class="bd">보정으로 합성 340개·실제 19개 평균 80%. VaR 검정 통과 조건 8 → 14개, 실현 변동이 목표에 모임</p></div><div class="box gray"><p class="bt">5.5, 6.1~6.2</p></div></div>'),
 ('<div class="bar"><p class="bar-t">실무 지침</p></div>\n<div class="eq3">\n<div class="box"><p class="bt">① 모델·설정을 먼저 점검</p><p class="bd">라이브러리 기본값 포함</p></div>\n<div class="box"><p class="bt">② 사후보정을 기본으로</p><p class="bd">재학습 없이 붙일 수 있음</p></div>\n<div class="box"><p class="bt">③ 위험 크기에 사용</p><p class="bd">방향 예측에는 쓰지 않음</p></div>\n</div>\n', ''),
 ('점검과 보정은 모델 구조와 무관해 새 TSFM에도 같은 방식으로 적용 · ACI-CQR은 기존 방법의 결합 · 본문 1.4절, 7.2절', '점검과 보정은 모델 내부 구조를 쓰지 않아 새 TSFM·다른 자산에도 같은 방식으로 적용 가능 · ACI-CQR은 기존 방법의 결합 · 본문 1.4절, 7.2절'),
])
aside('contrib', '3쪽에서 예고한 기여 네 가지를 근거와 함께 다시 정리하겠습니다. 첫째, 방법론입니다. 실제 종목에서 잰 세기로 합성 데이터를 만들고 특성 하나씩만 바꾸는 실험을 TSFM 구간 진단에 적용했고, 그 결과가 실제 주가와 평균 1.1%p 차이로 재현됐습니다. 크게 어긋나는 TimesFM 1년·가격과 기본 설정 Chronos-T5도 합성에서 먼저 드러났으니, 실제에 쓰기 전의 점검 절차로 쓸 수 있습니다. 둘째, 평가 관점입니다. 꼬리가 두꺼우면 80% 구간에서는 커버리지가 오히려 오르고 98% 구간에서는 떨어지므로, 구간 하나의 커버리지만 보고 꼬리 위험을 판단하면 잘못된 결론에 이를 수 있습니다. 셋째, 실증입니다. 최신 TSFM 네 종을 네 가지 입력으로 두 시장에서 같은 절차로 평가했고, 가설을 실험 전에 고정해 지지되지 않은 결과까지 전부 보고했습니다. 넷째, 실무입니다. 설정 점검과 사후보정이 필요하다는 것을 보였고, 보정이 VaR 검정 통과와 변동성 목표 같은 실제 규칙에서 차이를 만든다는 것을 확인했습니다. 점검과 보정은 모델 내부 구조를 쓰지 않아서 앞으로 나올 모델에도 같은 방식으로 쓸 수 있습니다.')

# ---- limits
ed('limits', [
 ('다만 극단 구간, 위기 수준, 다른 자산과 여러 날 앞 예측은 이 연구가 확인하지 못했다', '다만 극단 구간, 여러 날 앞 예측과 다른 자산, 외부 변수는 이 연구가 확인하지 못했다'),
 ('<p class="bt">80% 구간 중심</p></div><div class="box left"><p class="bd">극단 구간(98%)은 Chronos-2 한 모델로만 확인</p>', '<p class="bt">구간 수준</p></div><div class="box left"><p class="bd">주분석은 80% 구간. 극단 구간(98%)은 Chronos-2 한 모델로만 확인</p>'),
 ('<p class="bt">특성의 범위</p></div><div class="box left"><p class="bd">대형주 실측 범위 안(전환 빈도만 넘음). 위기 수준의 특성, 특성끼리의 결합은 미실험</p></div><x-connector class="arr" head="end"></x-connector><div class="box ok left"><p class="bd">위기 수준·결합 시나리오</p></div></div>\n<div class="row3l"><div class="box prob"><p class="bt">표본</p></div><div class="box left"><p class="bd">다음 날 예측, 미국·한국 대형주 10종목</p></div><x-connector class="arr" head="end"></x-connector><div class="box ok left"><p class="bd">여러 날 앞 예측, 다른 자산</p></div></div>',
  '<p class="bt">표본</p></div><div class="box left"><p class="bd">다음 날 예측, 미국·한국 대형주 10종목. 특성 세기도 이 종목들의 실측 범위 안</p></div><x-connector class="arr" head="end"></x-connector><div class="box ok left"><p class="bd">여러 날 앞 예측, 다른 자산군</p></div></div>'),
 ('<p class="bt">모델·입력</p></div><div class="box left"><p class="bd">Chronos-T5 base, Moirai small. 종가 단변량(거래량은 일부 확인)</p></div><x-connector class="arr" head="end"></x-connector><div class="box ok left"><p class="bd">TimesFM 1년·가격 과대 원인 규명</p></div></div>',
  '<p class="bt">모델</p></div><div class="box left"><p class="bd">Chronos-T5 base, Moirai small, 미세조정 모델 제외. TimesFM 1년·가격 과대 원인은 일부만 규명</p></div><x-connector class="arr" head="end"></x-connector><div class="box ok left"><p class="bd">금융 데이터로 학습한 모델과 비교, TimesFM 과대 원인 규명</p></div></div>\n<div class="row3l"><div class="box prob"><p class="bt">입력 정보</p></div><div class="box left"><p class="bd">종가 단변량. 거래량은 Chronos-2 하나로만 확인</p></div><x-connector class="arr" head="end"></x-connector><div class="box ok left"><p class="bd">실현·내재변동성 등 외부 변수</p></div></div>'),
 ('<p class="bd">평균만 맞춘다. 위반 몰림·분포 정확도는 그대로, 폭 효율 개선 여지</p></div><x-connector class="arr" head="end"></x-connector><div class="box ok left"><p class="bd">시기에 따라 다르게 보정하는 조건부 보정</p>', '<p class="bd">평균만 맞춘다. 위반 몰림·분포 정확도는 그대로, 폭 효율은 대조군보다 낮음</p></div><x-connector class="arr" head="end"></x-connector><div class="box ok left"><p class="bd">폭 효율 개선, 시기에 따라 다르게 보정하는 조건부 보정</p>'),
])
aside('limits', '한계도 분명히 말씀드리겠습니다. 첫째, 주분석은 80% 구간이고 극단 구간은 극단 분위수를 내는 Chronos-2 한 모델로만 확인했습니다. 둘째, 다음 날 예측과 미국·한국 대형주 10종목에 한정되고, 합성 데이터의 세기도 이 종목들에서 잰 범위 안입니다. 셋째, 계산 자원 때문에 Chronos-T5는 base, Moirai는 small 크기만 썼고, 금융 데이터로 미세조정한 모델은 다루지 않았습니다. TimesFM 1년·가격이 넓게 나오는 원인도 일부만 밝혔습니다. 넷째, 입력은 종가 하나뿐이고 거래량은 Chronos-2 하나로만 확인했습니다. 다섯째, 보정은 평균 수준만 맞추고, 위반이 몰려 오는 문제와 분포 전체의 정확도는 그대로 두며, 폭 효율은 결과를 보고 정한 일괄 확대보다 낮았습니다. 향후 연구로는 극단 분위수를 내는 다른 모델에서의 재검증, 여러 날 앞 예측과 다른 자산, 금융 데이터로 학습한 모델과의 비교와 TimesFM 과대 원인 규명, 외부 변수, 그리고 폭 효율과 시기별 보정을 생각하고 있습니다.')

# ---- Q06
ed('qa06', [
 ('"평균적으로 얼마나 맞나"는 설정이 정하고, "언제 틀리나"는 특성이 좌우한다', '80% 구간의 평균 수준은 설정이 정한다. 다만 극단 구간에서는 특성이 작용하므로, 결론은 80% 구간 기준으로 한정했다'),
 ('<tr><td>시기별 커버리지(실제)</td><td>-</td><td>평온·변동기 차이 평균 10.1%p(최대 22.8%p)</td></tr>\n', ''),
 ('<p class="bt" style="font-size:31px;">설정 문제 = 늘 5분 빠른 시계</p><p class="bd" style="font-size:28px;color:#2B2F36;line-height:1.5;">평균이 한쪽으로 어긋난다. 합성 점검으로 미리 보이고, 사후보정으로 평균 80%가 된다</p>',
  '<p class="bt" style="font-size:31px;">80% 구간 평균: 설정이 정한다</p><p class="bd" style="font-size:28px;color:#2B2F36;line-height:1.5;">특성 없는 데이터에서 이미 75~88%로 갈리고 특성은 대부분 3%p 이내. 합성 점검으로 미리 보이고, 보정으로 80%가 된다</p>'),
 ('<p class="bt" style="font-size:31px;">금융 특성 = 날씨가 나쁠 때만 틀리는 시계</p><p class="bd" style="font-size:28px;color:#2B2F36;line-height:1.5;">평소엔 맞다가 변동이 큰 시기와 극단 구간에서 드러난다. 보정이 일부만 메운다</p>',
  '<p class="bt" style="font-size:31px;">극단 구간: 특성이 작용한다</p><p class="bd" style="font-size:28px;color:#2B2F36;line-height:1.5;">Chronos-2의 98% 구간에서는 꼬리·전환이 커버리지를 낮춘다. 그래서 "특성은 중요하지 않다"가 아니라 "80% 구간 평균에서는 설정이 더 크다"</p>'),
 ('표 4-1, 4-2, 4-4, 5.1절, 표 6-4 · 통째로', '표 4-1, 4-2, 4-4, 5.1절, 7.3절 한계 1 · 통째로'),
])
aside('qa06', '80% 구간의 평균 커버리지를 기준으로 하면 그렇습니다. 특성이 없는 데이터에서도 모델과 입력에 따라 75에서 88%로 13%p나 벌어졌고, 특성을 가장 강하게 해도 대부분 3%p 안에서만 움직였습니다. 실제 주가에서도 커버리지 변동의 92%가 모델과 조건의 차이였고 종목 차이는 1%였습니다. 하지만 통째로 "금융 특성은 덜 중요하다"고 말하면 과장입니다. Chronos-2의 98% 극단 구간에서는 꼬리와 국면 전환이 커버리지를 실제로 떨어뜨렸습니다. 그래서 논문에서도 이 결론을 80% 구간과 평균 커버리지에 한정했고, 극단 위험에 그대로 적용할 수 없다고 한계로 밝혔습니다.')

# ---- Q09
ed('qa09', [
 ('같은 패치 방식의 Moirai-2는 같은 조건에서 79.7%로 정상', '같은 패치 방식의 Chronos-2(79.9%)·Moirai-2(79.7%)는 같은 조건에서 정상'),
 ('입력 창을 정규화하는 같은 패치 방식인 Moirai-2는 같은 조건에서 79.7%로 정상이어서', '같은 패치 방식인 Chronos-2와 Moirai-2는 같은 조건에서 79.9%와 79.7%로 정상이어서'),
])
# ---- Q10
ed('qa10', [
 ('<p class="bt" style="font-size:31px;">RW가 강한 이유</p><p class="bd" style="font-size:28px;color:#2B2F36;line-height:1.5;">일별 수익률은 방향을 거의 예측할 수 없어 "중심 0, 폭은 최근 변동"이 정답에 가깝다</p>',
  '<p class="bt" style="font-size:31px;">단순 모형이 강한 이유</p><p class="bd" style="font-size:28px;color:#2B2F36;line-height:1.5;">일별 수익률은 방향이 거의 없어 내일 변동의 크기가 관건이고, 이는 RW·GARCH-t도 잘한다</p>'),
 ('RW가 강했던 것은 일별 수익률의 방향을 거의 예측할 수 없어서, 중심은 0, 폭은 최근 변동 크기라는 답이 이미 정답에 가깝기 때문입니다.', '단순 모형이 강했던 것은 일별 수익률의 방향을 거의 예측할 수 없어서 내일 변동의 크기를 맞히는 것이 관건인데, 과거 변동으로 만드는 RW나 군집을 반영하는 GARCH-t도 그것을 잘하기 때문입니다.'),
])
# ---- Q12
ed('qa12', [
 ('변동성 목표 전략에서 보정한 Chronos-T5 2개 조합은 RW보다 샤프 비율이 유의하게 낮았다', '보정은 평균만 맞추고 원래 모델의 약점은 남는다. 보정한 Chronos-T5 2개 조건은 변동성 목표 전략에서 RW보다 샤프 비율이 유의하게 낮음'),
])
# ---- Q13
ed('qa13', [
 ('Chronos 학습 데이터에는 개별 종목 주가가 없고, Moirai 학습 데이터의 경제·금융 비중은 약 0.1%', '여러 분야의 공개 시계열과 합성 데이터로, 금융 수익률 비중은 작다(예: Moirai 1.0의 경제·금융 약 0.1%)'),
 ('참고로 Chronos의 학습 데이터에는 개별 종목 주가가 없고, Moirai의 학습 데이터에서 경제·금융 비중은 약 0.1%입니다.', '참고로 TSFM의 학습 데이터는 에너지, 교통, 날씨 같은 여러 분야의 공개 시계열과 합성 데이터이고 금융 수익률의 비중은 작습니다. 예를 들어 Moirai 1.0의 학습 데이터에서 경제·금융 분야는 약 0.1%입니다. 다만 개별 종목이 들어 있는지는 공개 자료로 완전히 확인할 수 없어서 공개 이후 기간을 따로 계산했습니다.'),
])

# ---- 공통: 부록 근거의 내부 '디펜스' 번호 삭제, 조합 → 조건, 인용 표기
import glob
for p in glob.glob(os.path.join(D, '*.html')):
    s = open(p).read(); o = s
    s = re.sub(r' · 디펜스 [A-Z][0-9]+(?:-[0-9]+)?(?:, [A-Z][0-9]+(?:-[0-9]+)?)*', '', s)
    s = s.replace('모델·입력 조합', '모델·조건').replace('모델·조합', '모델·조건').replace('조합', '조건')
    s = s.replace('Noguer i Alonso 외(2026)', 'Noguer i Alonso·Franklin(2026)')
    if s != o: open(p, 'w').write(s)
print('ok')
