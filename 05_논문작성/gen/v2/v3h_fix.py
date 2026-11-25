import sys,glob,os
d=sys.argv[1]
E=[
('01_표지_차례_국문요지.md','현재의 TSFM은 수익률을 맞히는 도구가 아니라 설정 점검과 보정을 거친 위험 측정 도구로 쓰는 것이 적절하다.','현재의 TSFM을 쓴다면 수익률을 맞히는 용도가 아니라 위험을 측정하는 용도로 한정하고, 설정 점검과 사후보정을 먼저 거쳐야 한다.'),
('02_제1장_서론.md','따라서 TSFM 예측구간은 수익률을 맞히는 데보다, 보정을 거쳐 위험의 크기를 측정하는 데 쓰는 것이 적절하다.','따라서 TSFM 예측구간을 쓴다면 수익률 예측보다는 위험의 크기를 측정하는 용도로 한정하고, 보정을 거쳐야 한다.'),
('08_제7장_결론.md','TSFM 예측구간은 수익률 예측보다 보정을 거친 위험 측정에 쓰는 것이 적절하다.','TSFM 예측구간을 쓴다면 수익률 예측이 아니라 보정을 거친 위험 측정으로 용도를 한정해야 한다.'),
('08_제7장_결론.md','3. TSFM 예측구간은 방향 예측이 아니라 위험 측정에 써야 한다.','3. TSFM 예측구간을 쓴다면 방향 예측이 아니라 위험 측정으로 용도를 한정해야 한다.'),
('13_ABSTRACT.md','Current TSFMs are therefore better used not as return forecasters but as risk-measurement tools, after checking models and usage settings and applying training-free post-hoc calibration.','If current TSFMs are deployed in practice, their use should therefore be limited to risk measurement rather than return forecasting, after checking models and usage settings and applying training-free post-hoc calibration.'),
('04_제3장_연구설계.md','전환 빈도와 전환 크기의 L4는 같은 설정이다.','전환 빈도와 전환 크기의 L4는 같은 설정이다. 같은 난수를 쓰므로 두 시나리오는 같은 데이터이며, 그림 4-1에서 값이 다른 것은 표본을 무작위로 뽑는 Chronos-T5뿐이다.'),
]
ok=bad=0
for f,o,n in E:
    p=os.path.join(d,f); s=open(p).read()
    if s.count(o)==1: s=s.replace(o,n); open(p,'w').write(s); ok+=1
    else: print('BAD',f,s.count(o),o[:40]); bad+=1
print('applied',ok,'bad',bad)
