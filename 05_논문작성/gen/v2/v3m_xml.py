"""v3m: apply.py가 못 한 부분(그림 5-2 설명, 표 2-1 행 추가, 참고문헌 순서·추가, 표 5-5 열 추가)을 XML에서 처리. 사용: v3m_xml.py <unzipped> <m1>"""
import re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xml_phrase import replace_in_para, para_text
D, M1 = sys.argv[1], sys.argv[2]
p = os.path.join(D, 'word/document.xml'); x = open(p, encoding='utf8').read()
PAR = r'<w:p[ >].*?</w:p>'
def paras(): return list(re.finditer(PAR, x, flags=re.S))
# 1) 그림 5-2 설명(본문·그림 차례)
out=[]; prev=0; c=0
for m in paras():
    pp,k = replace_in_para(m.group(0), '진한 막대는 Holm 보정 후 유의', '진한 막대는 Holm 다중비교 보정 후 유의'); c+=k
    out.append(x[prev:m.start()]); out.append(pp); prev=m.end()
out.append(x[prev:]); x=''.join(out); print('그림 5-2', c)

def set_cell(tc, lines):
    """칸의 문단들을 lines 수에 맞추어 글자만 바꾼다(첫 run 서식 유지)."""
    ps = list(re.finditer(PAR, tc, flags=re.S))
    assert len(ps) == len(lines), (len(ps), lines)
    for m, new in reversed(list(zip(ps, lines))):
        pp, k = replace_in_para(m.group(0), para_text(m.group(0)), new, maxn=1)
        assert k == 1
        tc = tc[:m.start()] + pp + tc[m.end():]
    return tc

# 2) 표 2-1: Noguer 행을 복제해 Upadhyay 행 추가
rows = list(re.finditer(r'<w:tr[ >].*?</w:tr>', x, flags=re.S))
nog = [r for r in rows if para_text(r.group(0)).replace('\xa0',' ').startswith('Noguer i Alonso, Franklin(2026)')]
assert len(nog) == 1, len(nog)
r = nog[0].group(0)
cells = list(re.finditer(r'<w:tc>.*?</w:tc>', r, flags=re.S))
new_vals = [['Upadhyay(2026)'], ['○'], ['○', '(지수선물)'], ['×'], ['△', '(변동성만)'], ['×']]
nr = r; parts=[]; prev=0
for cm, v in zip(cells, new_vals):
    tc = cm.group(0)
    np_ = len(re.findall(PAR, tc, flags=re.S))
    if np_ != len(v):  # 문단 수가 다르면 비슷한 칸을 빌려 온다
        src = [c2.group(0) for c2 in cells if len(re.findall(PAR, c2.group(0), flags=re.S)) == len(v)]
        tc = src[0]
    parts.append(r[prev:cm.start()]); parts.append(set_cell(tc, v)); prev = cm.end()
parts.append(r[prev:]); nr=''.join(parts)
x = x[:nog[0].end()] + nr + x[nog[0].end():]
print('표 2-1 행 추가')

# 3) 참고문헌: Gneiting 두 항목 순서 바꾸기, Upadhyay 추가
ps = paras()
g1 = [m for m in ps if para_text(m.group(0)).startswith('Gneiting, T., &amp; Raftery')]
g2 = [m for m in ps if para_text(m.group(0)).startswith('Gneiting, T., Balabdaoui')]
assert len(g1)==1 and len(g2)==1 and g1[0].end() <= g2[0].start()
a, b = g1[0], g2[0]
x = x[:a.start()] + b.group(0) + x[a.end():b.start()] + a.group(0) + x[b.end():]
ps = paras()
vas = [m for m in ps if para_text(m.group(0)).startswith('Vaswani, A.')]
assert len(vas)==1
ref_new = 'Upadhyay, R. (2026). Do time-series foundation models forecast index-futures returns? A preregistered evaluation of models, metrics, and input representations. '
# 서식: Vaswani 항목을 복제해 글자 교체(기울임 run 구조가 다를 수 있으므로 단순 run 하나로)
v = vas[0].group(0)
ppr = re.search(r'<w:pPr>.*?</w:pPr>', v, flags=re.S); rpr = re.search(r'<w:rPr>.*?</w:rPr>', v[ppr.end() if ppr else 0:], flags=re.S)
rp = rpr.group(0) if rpr else ''
rp_i = rp.replace('<w:rPr>', '<w:rPr><w:i/>', 1) if rp else '<w:rPr><w:i/></w:rPr>'
newp = '<w:p>' + (ppr.group(0) if ppr else '') + f'<w:r>{rp}<w:t xml:space="preserve">{ref_new}arXiv:2611.12141.</w:t></w:r></w:p>'
# Vaswani 앞의 빈 문단 구조 유지: 새 항목 + (Vaswani 바로 앞 문단이 빈 문단이면 그것도 복제)
prevp = [m for m in ps if m.end() <= vas[0].start()][-1]
blank = prevp.group(0) if para_text(prevp.group(0)).strip()=='' else ''
x = x[:vas[0].start()] + newp + blank + x[vas[0].start():]
print('참고문헌 처리')

SKIP55 = os.environ.get('SKIP55') == '1'
def step4(x):
    md = open(os.path.join(M1, '06_제5장_실증평가.md'), encoding='utf8').read().split('\n')
    i = [k for k,l in enumerate(md) if l.startswith('**표 5-5')][0]
    mrows = []
    for l in md[i+1:i+40]:
        if l.startswith('|'):
            c=[s.strip() for s in l.split('|')[1:-1]]
            if not set(c[0]) <= set('-:'): mrows.append(c)
        elif mrows: break
    cap = [m for m in paras() if para_text(m.group(0)).startswith('표 5-5. 비중 조절')][-1]
    t0 = x.find('<w:tbl>', cap.end()); t1 = x.find('</w:tbl>', t0) + 8
    tbl = x[t0:t1]
    trs = list(re.finditer(r'<w:tr[ >].*?</w:tr>', tbl, flags=re.S))
    assert len(trs) == len(mrows), (len(trs), len(mrows))
    newtbl=[]; prev=0
    for tr, mr in zip(trs, mrows):
        r = tr.group(0)
        cs = list(re.finditer(r'<w:tc>.*?</w:tc>', r, flags=re.S))
        assert len(cs) == 6
        src = cs[4].group(0)
        add = set_cell(src, [mr[5]]) + set_cell(src, [mr[6]])
        r = r[:cs[4].end()] + add + r[cs[4].end():]
        newtbl.append(tbl[prev:tr.start()]); newtbl.append(r); prev = tr.end()
    newtbl.append(tbl[prev:]); tbl=''.join(newtbl)
    # 열 너비: 기존 6열 합을 유지해 8열로 다시 나눔
    g = re.search(r'<w:tblGrid>(.*?)</w:tblGrid>', tbl, flags=re.S)
    ws = [int(w) for w in re.findall(r'w:w="(\d+)"', g.group(1))]
    tot = sum(ws); frac = [0.14, 0.15, 0.10, 0.12, 0.10, 0.11, 0.10, 0.18]
    nw = [round(tot*f) for f in frac]; nw[-1] += tot - sum(nw)
    tbl = tbl[:g.start(1)] + ''.join(f'<w:gridCol w:w="{w}"/>' for w in nw) + tbl[g.end(1):]
    def fix_tcw(rm):
        r = rm.group(0); k=[0]
        def rep(mm):
            w = nw[k[0]] if k[0] < len(nw) else None; k[0]+=1
            return f'<w:tcW w:w="{w}" w:type="dxa"/>' if w else mm.group(0)
        return re.sub(r'<w:tcW [^>]*/>', rep, r)
    tbl = re.sub(r'<w:tr[ >].*?</w:tr>', fix_tcw, tbl, flags=re.S)
    x = x[:t0] + tbl + x[t1:]
    print('표 5-5 열 추가', ws, '->', nw)
    return x
if SKIP55: print('표 5-5 열 추가 건너뜀')
else: x = step4(x)
x = re.sub(r'<w:t>([^<]*)</w:t>', lambda m: ('<w:t xml:space="preserve">' if m.group(1)!=m.group(1).strip() else '<w:t>')+m.group(1)+'</w:t>', x)
open(p, 'w', encoding='utf8').write(x)
