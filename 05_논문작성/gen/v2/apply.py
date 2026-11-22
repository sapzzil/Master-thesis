"""v2 원고(md) 변경을 사용자 Word 파일 사본에 문단 단위로 옮긴다. 서식(pPr, 글꼴 rPr)은 원래 문단 것을 그대로 쓴다.
usage: apply.py src.docx dst.docx old_dir new_dir
- md 줄 단위 diff. 본문 문단·목록·제목·캡션: 해당 docx 문단의 글자만 교체, 새 문단은 이웃 문단 pPr 복제로 삽입, 삭제는 제거.
- 표 행: 칸 수가 같으면 칸별 글자 교체. 표 구조 변경·그림·수식 줄 변경은 중단(수동 처리).
"""
import sys, re, glob, os, zipfile, difflib, html
sys.path.insert(0, os.path.dirname(__file__))
from common import pieces, display, PARA, ptext

src, dst, old_dir, new_dir = sys.argv[1:5]
DEBUG = len(sys.argv) > 5
z = zipfile.ZipFile(src)
x = z.read('word/document.xml').decode('utf-8')

def esc(s): return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

# 본문 문단 목록(차례 항목 제외)
def body_paras(x):
    out = []
    for m in PARA.finditer(x):
        p = m.group(0)
        if '<w:hyperlink' in p or re.search(r'<w:pStyle w:val="(?:10|20|30|a6)"/>', p) and 'TOC' in p:
            continue
        if '<w:hyperlink' in p: continue
        out.append([m.start(), m.end(), ptext(p)])
    return out

def base_rpr(p):
    m = re.search(r'<w:r(?: [^>]*)?>(?:<w:rPr>(.*?)</w:rPr>)?<w:t', p)
    r = (m.group(1) or '') if m else ''
    r = re.sub(r'<w:vertAlign [^>]*/>|<w:b/>|<w:bCs/>|<w:i/>|<w:iCs/>', '', r)
    return r

def make_runs(md_text, rpr):
    out = []
    for t, k in pieces(md_text):
        if not t: continue
        extra = {'sub': '<w:vertAlign w:val="subscript"/>', 'sup': '<w:vertAlign w:val="superscript"/>',
                 'b': '<w:b/><w:bCs/>', 'i': '<w:i/><w:iCs/>', '': ''}[k]
        # 글꼴·크기 뒤, vertAlign은 rPr 끝 쪽 순서
        rp = (('<w:b/><w:bCs/>' if k == 'b' else '') + ('<w:i/><w:iCs/>' if k == 'i' else '') + rpr +
              (extra if k in ('sub', 'sup') else ''))
        if k in ('b', 'i'):
            # rFonts는 b보다 앞이어야 함
            fm = re.match(r'(<w:rFonts [^>]*/>)?(.*)', rpr)
            rp = (fm.group(1) or '') + ('<w:b/><w:bCs/>' if k == 'b' else '<w:i/><w:iCs/>') + fm.group(2)
        out.append(f'<w:r>{"<w:rPr>"+rp+"</w:rPr>" if rp else ""}<w:t xml:space="preserve">{esc(t)}</w:t></w:r>')
    return ''.join(out)

def md_text_of(line):
    l = line.strip()
    l = re.sub(r'^[-*]\s+', '', l)
    l = re.sub(r'^#+\s+', '', l)
    l = re.sub(r'^>\s*', '', l)
    return l

def rebuild(p, md_line):
    m = re.match(r'(<w:p[ >][^>]*>|<w:p>)?(<w:pPr>.*?</w:pPr>)?', p, re.S)
    head = re.match(r'<w:p(?: [^>]*)?>', p).group(0)
    ppr = re.search(r'<w:pPr>.*?</w:pPr>', p, re.S)
    ppr = ppr.group(0) if ppr else ''
    # 문단 끝 북마크 등 run 아닌 요소 보존: bookmarkStart/End
    marks = ''.join(re.findall(r'<w:bookmark(?:Start|End) [^>]*/>', p))
    return head + ppr + marks + make_runs(md_text_of(md_line), base_rpr(p)) + '</w:p>'

def kind(line):
    s = line.strip()
    if s.startswith('|'): return 'table'
    if s.startswith('!') or s.startswith('$$') or s.startswith('<'): return 'fixed'
    return 'text'

edits = []  # (start, end, newxml)
paras = body_paras(x)
from collections import Counter as _C
CNT = _C(p[2].strip() for p in paras)
cursor = 0
def find_para(line, start_idx):
    t = display(md_text_of(line)) if not line.strip().startswith('>') else display(md_text_of(line))
    for i in range(start_idx, len(paras)):
        if paras[i][2].strip() == t.strip():
            return i
    raise SystemExit(f'못 찾음: {t[:80]!r}')

def table_cells(line):
    return [c.strip() for c in line.strip().strip('|').split('|')]

report = []
for of in sorted(glob.glob(os.path.join(old_dir, '*.md'))):
    nf = os.path.join(new_dir, os.path.basename(of))
    if not os.path.exists(nf): continue
    def _split(lines):
        out = []
        for l in lines:
            m = re.match(r'^(\*\*(?:그림|표) [^*]+\*\*)\.?\s+(\S.*)$', l)
            if m: out += [m.group(1), m.group(2)]
            else: out.append(l)
        return out
    A = _split([l for l in open(of, encoding='utf-8').read().split('\n') if l.strip()])
    B = _split([l for l in open(nf, encoding='utf-8').read().split('\n') if l.strip()])
    if A == B: continue
    sm = difflib.SequenceMatcher(None, A, B, autojunk=False)
    # 각 equal 블록의 텍스트 줄로 cursor를 앞으로 당겨 위치를 고정
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            for l in A[i1:i2]:
                if kind(l) == 'text' and not l.lstrip().startswith('- ') and len(display(md_text_of(l)).strip()) >= 25 and CNT.get(display(md_text_of(l)).strip(), 0) == 1 and l.strip() != '---':
                    try:
                        cursor = find_para(l, cursor) + 1; print("eq", cursor, l[:40]) if DEBUG else None
                    except SystemExit:
                        pass
            continue
        olds, news = A[i1:i2], B[j1:j2]
        ko = {kind(l) for l in olds}; kn = {kind(l) for l in news}
        if 'fixed' in ko | kn:
            raise SystemExit(f'{os.path.basename(of)}: 그림·수식 줄 변경은 수동 처리 {olds[:1]} -> {news[:1]}')
        if 'table' in ko | kn:
            if not (ko == {'table'} and kn == {'table'} and len(olds) == len(news)):
                raise SystemExit(f'{os.path.basename(of)}: 표 구조 변경 {olds[:1]}')
            # 행 단위 칸 교체: 표 안 문단은 칸 순서대로 나옴
            for lo, ln in zip(olds, news):
                co, cn = table_cells(lo), table_cells(ln)
                assert len(co) == len(cn), (lo, ln)
                if set(lo.replace('|', '').strip()) <= set('-: '): continue
                k = cursor
                for a, b in zip(co, cn):
                    i = find_para('x ' if False else a, k) if a else None
                    if i is None: continue
                    if a != b:
                        p = x[paras[i][0]:paras[i][1]]
                        edits.append((paras[i][0], paras[i][1], rebuild(p, b)))
                        report.append(('cell', a[:30], b[:30]))
                    k = i + 1
                cursor = k
            continue
        # 텍스트 블록
        idx = []
        for l in olds:
            i = find_para(l, cursor); idx.append(i); cursor = i + 1
        if idx:
            anchor = idx[0]
            first_p = x[paras[anchor][0]:paras[anchor][1]]
            new_xml = ''
            for k, l in enumerate(news):
                tmpl = x[paras[idx[min(k, len(idx)-1)]][0]:paras[idx[min(k, len(idx)-1)]][1]]
                if l.strip().startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')) != md_text_of(olds[min(k, len(olds)-1)]).startswith(tuple('123456789')):
                    pass
                tmpl = re.sub(r'w14:paraId="[0-9A-F]+"', '', tmpl) if k > 0 else tmpl
                new_xml += rebuild(tmpl, l)
            edits.append((paras[idx[0]][0], paras[idx[0]][1], new_xml))
            for i in idx[1:]:
                edits.append((paras[i][0], paras[i][1], ''))
            report.append((tag, len(olds), len(news)))
        else:
            # 순수 삽입: 바로 앞 문단(cursor-1) 서식 복제, 뒤에 붙임
            prev = paras[cursor - 1]
            tmpl = re.sub(r'w14:paraId="[0-9A-F]+"', '', x[prev[0]:prev[1]])
            if re.search(r'<w:pStyle w:val="[0-9]+"/>', tmpl) or '<w:outlineLvl' in tmpl:
                raise SystemExit(f'삽입 위치 앞이 제목: {news[0][:40]}')
            edits.append((prev[1], prev[1], ''.join(rebuild(tmpl, l) for l in news)))
            report.append(('insert', 0, len(news)))

edits.sort(key=lambda e: e[0], reverse=True)
last = None
for s, e, n in edits:
    assert last is None or e <= last, '겹침'
    x = x[:s] + n + x[e:]; last = s
out = zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED)
for it in z.infolist():
    out.writestr(it, x.encode('utf-8') if it.filename == 'word/document.xml' else z.read(it.filename))
out.close()
from collections import Counter
print('edits', len(edits), Counter(r[0] for r in report))
