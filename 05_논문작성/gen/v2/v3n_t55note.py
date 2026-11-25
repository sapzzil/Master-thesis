"""표 5-5 주에 본문에서 쓴 TimesFM-2.5 1년·가격의 연수익률·평균 비중을 적는다(E2_voltarget.csv). 사용: v3n_t55note.py <원고_md_dir>"""
import sys, os
F5 = '06_제5장_실증평가.md'
o = '계속 보유의 실현변동/목표는 참고값이다.'
n = '계속 보유의 실현변동/목표는 참고값이다. 본문(5.5.2절)에서 쓴 TimesFM-2.5 1년·가격의 연수익률은 원래 9.0%, 보정 11.9%이고, 평균 비중은 0.47, 0.59이다.'
p = os.path.join(sys.argv[1], F5); s = open(p, encoding='utf8').read()
assert s.count(o) == 1
open(p, 'w', encoding='utf8').write(s.replace(o, n)); print('ok')
