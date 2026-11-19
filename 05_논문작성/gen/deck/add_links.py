"""심사 발표 pptx에 장 사이 이동 링크를 넣는다.
- 본편 바닥글 "자세히 → 부록 Q04 …(32쪽) · …": 항목마다 해당 부록 장으로
- 부록 바닥글 "← 본편 15 · 16 · 24쪽의 부가 설명 · 부록 목록 28쪽": 쪽 번호마다 본편 장으로, '부록 목록 28쪽'은 28쪽으로
- 28쪽 목록: Qnn 칩, 제목, nn쪽 글자를 해당 부록 장으로
링크 글자색은 원래 색(남색)을 유지하도록 hlinkClr=tx를 넣고, 테마 링크색도 남색으로 바꾼다.
"""
import copy, re, sys
from pptx import Presentation
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from lxml import etree

A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
AHYP = 'http://schemas.microsoft.com/office/drawing/2018/hyperlinkcolor'
src, dst = sys.argv[1], sys.argv[2]
prs = Presentation(src)
slides = list(prs.slides)
N = len(slides)
assert N == 43, N
count = {'main': 0, 'appx_back': 0, 'list': 0}


def rid_to(slide, page):
    return slide.part.relate_to(slides[page - 1].part, RT.SLIDE)


def make_run(base_r, text, slide=None, page=None):
    r = copy.deepcopy(base_r)
    for t in r.findall(f'{{{A}}}t'):
        t.text = text
    rpr = r.find(f'{{{A}}}rPr')
    for old in rpr.findall(f'{{{A}}}hlinkClick'):
        rpr.remove(old)
    if page is not None:
        h = etree.SubElement(rpr, f'{{{A}}}hlinkClick')
        h.set(f'{{{R}}}id', rid_to(slide, page))
        h.set('action', 'ppaction://hlinksldjump')
        ext_lst = etree.SubElement(h, f'{{{A}}}extLst')
        ext = etree.SubElement(ext_lst, f'{{{A}}}ext')
        ext.set('uri', '{A12FA001-AC4F-418D-AE19-62706E023703}')
        c = etree.SubElement(ext, f'{{{AHYP}}}hlinkClr', nsmap={'ahyp': AHYP})
        c.set('val', 'tx')
        # rPr 자식 순서: ln, fill, effect, highlight, uLnTx, uLn, uFillTx, uFill, latin, ea, cs, sym, hlinkClick ... → 글꼴 뒤면 맞음
    return r


def split_para(slide, para_el, pieces):
    """pieces: [(text, page or None)] — 문단의 첫 run 서식을 복제해 다시 만든다."""
    runs = para_el.findall(f'{{{A}}}r')
    base = runs[0]
    assert ''.join(t for t, _ in pieces) == ''.join(''.join(x.text or '' for x in r.findall(f'{{{A}}}t')) for r in runs)
    pos = list(para_el).index(runs[0])
    for r in runs:
        para_el.remove(r)
    for k, (t, pg) in enumerate(pieces):
        para_el.insert(pos + k, make_run(base, t, slide, pg))


def link_whole(slide, para_el, page):
    for r in para_el.findall(f'{{{A}}}r'):
        para_el.replace(r, make_run(r, ''.join(x.text or '' for x in r.findall(f'{{{A}}}t')), slide, page))


titles = None
for si, s in enumerate(slides, 1):
    for sh in s.shapes:
        if not sh.has_text_frame:
            continue
        for para in sh.text_frame.paragraphs:
            txt = ''.join(r.text for r in para.runs)
            p_el = para._p
            if txt.startswith('자세히 → 부록 '):
                body = txt[len('자세히 → 부록 '):]
                items = body.split(' · ')
                pieces = [('자세히 → 부록 ', None)]
                for k, it in enumerate(items):
                    m = re.search(r'\((\d+)쪽\)$', it)
                    assert m, it
                    pieces.append((it, int(m.group(1))))
                    count['main'] += 1
                    if k < len(items) - 1:
                        pieces.append((' · ', None))
                split_para(s, p_el, pieces)
            elif txt.startswith('← 본편 '):
                m = re.match(r'← 본편 ([\d · ]+)쪽의 부가 설명 {2}· {2}부록 목록 28쪽$', txt) or \
                    re.match(r'← 본편 ([\d · ]+)쪽의 부가 설명 · 부록 목록 28쪽$', txt)
                assert m, repr(txt)
                nums = [int(x) for x in m.group(1).split(' · ')]
                tail = txt[txt.index('쪽의 부가 설명'):]
                pieces = [('← 본편 ', None)]
                for k, n in enumerate(nums):
                    pieces.append((str(n), n))
                    count['appx_back'] += 1
                    if k < len(nums) - 1:
                        pieces.append((' · ', None))
                cut = tail.index('부록 목록 28쪽')
                pieces += [(tail[:cut], None), ('부록 목록 28쪽', 28)]
                split_para(s, p_el, pieces)
            elif si == 28:
                if re.fullmatch(r'Q(0[1-9]|1[0-5])', txt):
                    link_whole(s, p_el, 28 + int(txt[1:])); count['list'] += 1
                elif re.fullmatch(r'(29|3\d|4[0-3])쪽', txt):
                    link_whole(s, p_el, int(txt[:-1])); count['list'] += 1

# 목록 장의 질문 제목: Qnn 칩 바로 다음 글 상자
s28 = slides[27]
shapes = [sh for sh in s28.shapes if sh.has_text_frame and sh.text_frame.text.strip()]
for i, sh in enumerate(shapes):
    t = sh.text_frame.text
    if re.fullmatch(r'Q(0[1-9]|1[0-5])', t) and i + 1 < len(shapes):
        for para in shapes[i + 1].text_frame.paragraphs:
            link_whole(s28, para._p, 28 + int(t[1:]))
        count['list'] += 1

# 테마 링크색을 남색으로(구버전 PowerPoint가 hlinkClr를 모를 때 대비)
for master in prs.slide_masters:
    theme_part = [rel.target_part for rel in master.part.rels.values() if rel.reltype == RT.THEME][0]
    xml = theme_part.blob.decode('utf-8')
    xml = re.sub(r'<a:hlink><a:srgbClr val="[0-9A-Fa-f]{6}"/></a:hlink>', '<a:hlink><a:srgbClr val="1D3461"/></a:hlink>', xml)
    xml = re.sub(r'<a:folHlink><a:srgbClr val="[0-9A-Fa-f]{6}"/></a:folHlink>', '<a:folHlink><a:srgbClr val="1D3461"/></a:folHlink>', xml)
    theme_part._blob = xml.encode('utf-8')

# 부록 장(28~43쪽)에 "← 보던 장으로" 단추: PowerPoint의 '마지막으로 본 슬라이드' 동작
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
PX = prs.slide_width / 1920  # 슬라이드 1920px 기준
BACK = 'ppaction://hlinkshowjump?jump=lastslideviewed'
for page in range(28, 44):
    s = slides[page - 1]
    btn = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Emu(int(470 * PX)), Emu(int(1010 * PX)), Emu(int(290 * PX)), Emu(int(46 * PX)))
    btn.name = 'back-to-last-viewed'
    btn.fill.solid(); btn.fill.fore_color.rgb = RGBColor(0x1D, 0x34, 0x61)
    btn.line.fill.background()
    tf = btn.text_frame; tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    para = tf.paragraphs[0]; para.alignment = PP_ALIGN.CENTER
    run = para.add_run(); run.text = '← 보던 장으로'
    f = run.font; f.size = Pt(12.5); f.bold = True; f.color.rgb = RGBColor(0xFF, 0xFF, 0xFF); f.name = 'Malgun Gothic'
    rpr = run._r.get_or_add_rPr()
    ea = etree.SubElement(rpr, f'{{{A}}}ea'); ea.set('typeface', 'Malgun Gothic')
    # 도형 전체에 동작(글자 위를 눌러도 작동). 글자에 걸면 링크색으로 바뀌어 흰 글자가 사라지므로 걸지 않음
    for parent in (btn._element.find('.//{http://schemas.openxmlformats.org/presentationml/2006/main}cNvPr'),):
        h = etree.SubElement(parent, f'{{{A}}}hlinkClick')
        h.set(f'{{{R}}}id', '')
        h.set('action', BACK)
    count.setdefault('back', 0); count['back'] += 1

prs.save(dst)
print(count)
