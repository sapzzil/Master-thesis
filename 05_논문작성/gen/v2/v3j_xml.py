"""v3j: apply.py가 처리하지 못한 줄(표와 붙은 문단, <br> 칸, 그림 설명)과 차례 문구, 표 4-5 숫자, 3.2.5 식 줄바꿈을 XML에서 직접 바꾼다.
사용: python3 v3j_xml.py <unzipped_dir> <m1_dir>"""
import re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xml_phrase import replace_in_para, para_text
D, M1 = sys.argv[1], sys.argv[2]
p = os.path.join(D, 'word/document.xml'); x = open(p, encoding='utf8').read()

PAIRS = [
 ('특성 간 결손 비교 (H4)', '특성 간 비교: 커버리지가 가장 낮은 특성 (H4)', None),
 ('표 4-5. 고강도(L4·L5)에서 특성별 결손 (80% − 커버리지, %p; 양수 = 구간이 좁음)', '표 4-5. 강한 단계(L4·L5)에서 특성별 커버리지 (%)', None),
 ('H4는 고강도(L4·L5 평균)에서 네 특성의 결손(80% − 커버리지)이 서로 다른지를 같은 계열끼리 비교한다. 특성별 결손은 표 4-5와 같다.',
  'H4는 강한 단계(L4·L5 평균)에서 네 특성의 커버리지가 서로 다른지를 같은 계열끼리 비교한다. 특성별 커버리지는 표 4-5와 같다.', None),
 ('축마다 다름', '특성마다 다름', None),
 ('미지지', '지지 안 됨', lambda t: t.strip() == '미지지'),
 ('(채점 17,700건)', '(평가 17,700건)', None),
 ('× 채점 60일)', '× 평가 60일)', None),
 ('로 바꿔 채점', '로 바꿔 평가', None),
 ('준비 20일 + 채점 60일', '준비 20일 + 평가 60일', None),
 ('모든 지표는 채점 60일로 계산', '모든 지표는 평가 60일로 계산', None),
 ('(6개 메커니즘)', '(6개 구조)', None),
 ('(4축, 실측 모수)', '(4개 특성, 실측 모수)', None),
 ('아래: 목표 수준 ', '아래: 목표 이탈률 ', None),
 ('변동성 목표 비중 조절', '목표 변동성에 맞춘 비중 조절', None),
 ('비중 조절(변동성 목표 1%)', '비중 조절(목표 변동성 1%)', None),
 ('변동성 목표 실현변동/목표', '목표 변동성 전략 실현변동/목표', None),
 ('변동성 목표 최대낙폭', '목표 변동성 전략 최대낙폭', None),
 ('변동성 목표 전략', '목표 변동성 전략', None),
 ('방향 매매', '방향 예측 매매', None),
 ('샤프', '샤프 비율', lambda t: t.strip() == '샤프'),
 ('RW 대비 샤프 차(보정)', 'RW 대비 샤프 비율 차(보정)', None),
 ('L1과 축별 L5', 'L1과 특성별 L5', None),
 ('보정과 날카로움', '보정과 구간 폭', None),
 ('2.3.3 적정 점수 규칙', '2.3.3 분위수 손실과 CRPS', None),
 ('실증 결과의 대응', '실증 결과의 일치 정도', None),
 ('평가 구간', '평가 대상 구간', lambda t: t.strip() == '평가 구간'),
 ('커버리지가 가장 낮은 특성', '가장 낮은 특성', lambda t: t.strip() == '커버리지가 가장 낮은 특성'),
 ('| 평가 |', '| 평가 기간 |', None),
]
paras = list(re.finditer(r'<w:p[ >].*?</w:p>', x, flags=re.S))
out = []; prev = 0; cnt = {o: 0 for o, _, _ in PAIRS}
for m in paras:
    pp = m.group(0)
    for o, n, c in PAIRS:
        pp, k = replace_in_para(pp, o, n, c); cnt[o] += k
    out.append(x[prev:m.start()]); out.append(pp); prev = m.end()
out.append(x[prev:]); x = ''.join(out)
for o, k in cnt.items(): print(f'{k:3d}  {o[:50]}')

# 표 4-5 숫자: m1의 표 행 값으로 칸 교체
md = open(os.path.join(M1, '05_제4장_금융특성의_영향.md'), encoding='utf8').read().split('\n')
i = [k for k, l in enumerate(md) if l.startswith('**표 4-5')][0]
rows = {}
for l in md[i:i + 25]:
    c = [s.strip() for s in l.split('|')]
    if len(c) == 12 and re.fullmatch(r'\d+\.\d', c[3]): rows[(c[1], c[2])] = c[3:7]
# 본문 표 4-5 찾기: 캡션 문단 다음의 첫 <w:tbl>
cap = [m for m in re.finditer(r'<w:p[ >].*?</w:p>', x, flags=re.S) if para_text(m.group(0)).startswith('표 4-5. 강한 단계')]
cap = cap[-1]  # 본문 쪽(차례 다음)
t0 = x.find('<w:tbl>', cap.end()); t1 = x.find('</w:tbl>', t0) + 8
tbl = x[t0:t1]; done = 0
def fix_row(rm):
    global done
    r = rm.group(0)
    cells = list(re.finditer(r'<w:tc>.*?</w:tc>', r, flags=re.S))
    if len(cells) < 6: return r
    key = (para_text(cells[0].group(0)).replace('\xa0', ' ').strip(), para_text(cells[1].group(0)).replace('\xa0', ' ').strip())
    if key not in rows: return r
    parts = []; prev = 0
    for k, cm in enumerate(cells):
        c = cm.group(0)
        if 2 <= k <= 5:
            old = para_text(c).strip()
            c, nrep = replace_in_para(c, old, rows[key][k - 2], maxn=1)
            assert nrep == 1, (key, old)
        parts.append(r[prev:cm.start()]); parts.append(c); prev = cm.end()
    parts.append(r[prev:]); done += 1
    return ''.join(parts)
tbl = re.sub(r'<w:tr[ >].*?</w:tr>', fix_row, tbl, flags=re.S)
x = x[:t0] + tbl + x[t1:]
print('표 4-5 행', done, '/', len(rows))

# 3.2.5 식 줄바꿈: 해당 글머리표 문단에서 식 앞에 <w:br/>. run 서식(아래첨자)을 건드리지 않도록 해당 run만 나눈다. 줄 끝이 늘어나지 않게 왼쪽 정렬.
def brk(x, starts, before):
    ms = [m for m in re.finditer(r'<w:p[ >].*?</w:p>', x, flags=re.S) if para_text(m.group(0)).startswith(starts)]
    assert len(ms) == 1, (starts, len(ms))
    pp = ms[0].group(0)
    for b in before:
        runs = list(re.finditer(r'(<w:t(?: [^>]*)?>)([^<]*)(</w:t>)', pp))
        full = ''.join(r.group(2) for r in runs); i = full.find(b); assert i >= 0, b
        pos = 0
        for r in runs:
            t = r.group(2)
            if pos <= i < pos + len(t):
                o = i - pos
                seg = r.group(1) + t[:o] + '</w:t><w:br/><w:t xml:space="preserve">' + t[o:] + r.group(3)
                if o == 0: seg = '<w:br/>' + r.group(1) + t + r.group(3)
                pp = pp[:r.start()] + seg + pp[r.end():]
                break
            pos += len(t)
    head = pp.split('</w:pPr>')[0]
    if '<w:jc ' in head:
        pp = re.sub(r'<w:jc w:val="[^"]*"/>', '<w:jc w:val="left"/>', pp, count=1)
    else:
        pp = pp.replace('</w:pPr>', '<w:jc w:val="left"/></w:pPr>', 1)
    return x[:ms[0].start()] + pp + x[ms[0].end():]
x = brk(x, '군집(CL):', ['rt = σt zt, σt²', 'α = 0.1(α+β)'])
x = brk(x, '꼬리(TL):', ['rt = σ √', '같은 zt를 쓰므로'])
x = brk(x, '국면(RF·RS):', ['rt = σSt zt.', '격변 σ = 변동비'])
x = re.sub(r'<w:t>([^<]*)</w:t>', lambda m: ('<w:t xml:space="preserve">' if m.group(1) != m.group(1).strip() else '<w:t>') + m.group(1) + '</w:t>', x)
open(p, 'w', encoding='utf8').write(x)
