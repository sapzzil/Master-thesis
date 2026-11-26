"""발표 v12: 1·2단계 6판(발표/발표_v12_1단계메시지_2단계고스트덱.md) 구성대로 v11 디자인 위에 새로 만든다.
본편 21장 + 부록 B1~B13. v11 파일은 바꾸지 않고 새 파일로 저장.
사용: python3 deck_v12.py <v11.pptx> <out_v12.pptx>
"""
import sys, copy, re, os
from lxml import etree
from pptx import Presentation
from pptx.util import Pt

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
FIG = f'{ROOT}/05_논문작성/figs'
V12 = f'{FIG}/v12'
NS = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
      'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
NAVY, BODY, FILL, MUTED, ORANGE, LINE = '1B365D', '1E293B', 'F4F6F9', '64748B', 'D9480F', 'CBD5E1'
EMU = 12700
TOTAL = 21
FOOT = '김승민 · 석사학위논문 심사 발표  |  '


def esc(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


# ---------- XML 조각 ----------
def run(t, sz=14, b=False, col=BODY):
    return (f'<a:r><a:rPr lang="ko-KR" sz="{int(sz*100)}" b="{1 if b else 0}"><a:solidFill><a:srgbClr val="{col}"/></a:solidFill>'
            f'<a:latin typeface="맑은 고딕"/><a:ea typeface="맑은 고딕"/></a:rPr><a:t>{esc(t)}</a:t></a:r>')


def para(runs, algn='l', bef=0, aft=0):
    if isinstance(runs, tuple):
        runs = [runs]
    rs = ''.join(run(*r) for r in runs)
    return (f'<a:p><a:pPr algn="{algn}"><a:spcBef><a:spcPts val="{int(bef*100)}"/></a:spcBef><a:spcAft><a:spcPts val="{int(aft*100)}"/></a:spcAft></a:pPr>{rs}</a:p>')


def shape(sid, x, y, w, h, paras, geom='rect', fill=None, line=None, lw=1.1, anchor='t', ins=(7, 5, 7, 5), name=None):
    fl = f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>' if fill else '<a:noFill/>'
    ln = f'<a:ln w="{int(lw*EMU)}"><a:solidFill><a:srgbClr val="{line}"/></a:solidFill></a:ln>' if line else '<a:ln><a:noFill/></a:ln>'
    av = '<a:avLst><a:gd name="adj" fmla="val 7000"/></a:avLst>' if geom == 'roundRect' else '<a:avLst/>'
    tx = '' if geom == 'rect' and not fill and not line else ''
    l, t, r, b = (int(v * EMU) for v in ins)
    nm = name or f'v12 {sid}'
    txb = ' txBox="1"' if (not fill and not line) else ''
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{sid}" name="{nm}"/><p:cNvSpPr{txb}/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="{int(x*EMU)}" y="{int(y*EMU)}"/>'
            f'<a:ext cx="{int(w*EMU)}" cy="{int(h*EMU)}"/></a:xfrm><a:prstGeom prst="{geom}">{av}</a:prstGeom>{fl}{ln}</p:spPr>'
            f'<p:txBody><a:bodyPr wrap="square" lIns="{l}" tIns="{t}" rIns="{r}" bIns="{b}" anchor="{anchor}"><a:normAutofit/></a:bodyPr><a:lstStyle/>{"".join(paras)}</p:txBody></p:sp>')


def box(sid, x, y, w, h, title, lines, hl=False, tsz=15, bsz=13, algn='ctr'):
    col = ORANGE if hl else NAVY
    ps = [para((title, tsz, True, col), algn, aft=5)] + [para((l, bsz, False, BODY), algn, bef=2) for l in lines]
    return shape(sid, x, y, w, h, ps, 'roundRect', 'FFF4EE' if hl else FILL, col, 1.3, 'ctr', (8, 6, 8, 6))


def arrow(sid, x, y, w=18, h=20, prst='rightArrow'):
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{sid}" name="v12 arrow {sid}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="{int(x*EMU)}" y="{int(y*EMU)}"/>'
            f'<a:ext cx="{int(w*EMU)}" cy="{int(h*EMU)}"/></a:xfrm><a:prstGeom prst="{prst}"><a:avLst/></a:prstGeom><a:solidFill><a:srgbClr val="{NAVY}"/></a:solidFill><a:ln><a:noFill/></a:ln></p:spPr></p:sp>')


def cell_paras(c, sz, head, algn):
    if isinstance(c, str):
        c = [[(c, sz, head, 'FFFFFF' if head else BODY)]]
    return ''.join(para(p, algn) for p in c)


def table(sid, x, y, widths, rows, hs, sz=13.5, aligns=None):
    ncol = len(widths)
    aligns = aligns or ['l'] * ncol
    trs = ''
    for i, (r, h) in enumerate(zip(rows, hs)):
        head = i == 0
        tcs = ''
        for j, c in enumerate(r):
            fill = NAVY if head else ('FFFFFF' if i % 2 else FILL)
            tcs += (f'<a:tc><a:txBody><a:bodyPr/><a:lstStyle/>{cell_paras(c, sz, head, "ctr" if head else aligns[j])}</a:txBody>'
                    f'<a:tcPr marL="{int(8*EMU)}" marR="{int(8*EMU)}" marT="{int(4*EMU)}" marB="{int(4*EMU)}" anchor="ctr">'
                    f'<a:lnL w="0"><a:noFill/></a:lnL><a:lnR w="0"><a:noFill/></a:lnR><a:lnT w="6350"><a:solidFill><a:srgbClr val="{LINE}"/></a:solidFill></a:lnT>'
                    f'<a:lnB w="6350"><a:solidFill><a:srgbClr val="{LINE}"/></a:solidFill></a:lnB><a:solidFill><a:srgbClr val="{fill}"/></a:solidFill></a:tcPr></a:tc>')
        trs += f'<a:tr h="{int(h*EMU)}">{tcs}</a:tr>'
    grid = ''.join(f'<a:gridCol w="{int(w*EMU)}"/>' for w in widths)
    return (f'<p:graphicFrame><p:nvGraphicFramePr><p:cNvPr id="{sid}" name="v12 table {sid}"/><p:cNvGraphicFramePr><a:graphicFrameLocks noGrp="1"/></p:cNvGraphicFramePr><p:nvPr/></p:nvGraphicFramePr>'
            f'<p:xfrm><a:off x="{int(x*EMU)}" y="{int(y*EMU)}"/><a:ext cx="{int(sum(widths)*EMU)}" cy="{int(sum(hs)*EMU)}"/></p:xfrm>'
            f'<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/table"><a:tbl><a:tblPr firstRow="1" bandRow="1"/><a:tblGrid>{grid}</a:tblGrid>{trs}</a:tbl></a:graphicData></a:graphic></p:graphicFrame>')


def note(sid, x, y, w, h, items, title=None, sz=14):
    ps = ([para((title, sz + 0.5, True, NAVY), aft=6)] if title else []) + [para(i if isinstance(i, list) else [(i, sz, False, BODY)], bef=5) for i in items]
    return shape(sid, x, y, w, h, ps, 'roundRect', FILL, '94A3B8', 0.8, 't', (10, 8, 10, 8))


def add_xml(slide, frags):
    tree = slide.shapes._spTree
    wrap = f'<root xmlns:a="{NS["a"]}" xmlns:p="{NS["p"]}" xmlns:r="{NS["r"]}">' + ''.join(frags) + '</root>'
    for el in etree.fromstring(wrap):
        tree.append(el)


# ---------- 장 틀 ----------
def set_text(shp, text):
    """첫 단락 첫 run의 서식을 유지하고 글자만 바꾼다. text에 \n이 있으면 단락을 나눈다."""
    txb = shp.text_frame._txBody
    ps = txb.findall('a:p', NS)
    tmpl = next((p for p in ps if p.find('a:r', NS) is not None), ps[0])
    for p in ps[1:]:
        txb.remove(p)
    first = ps[0]
    if first is not tmpl:
        txb.replace(first, copy.deepcopy(tmpl)); first = txb.findall('a:p', NS)[0]
    rs = first.findall('a:r', NS)
    for r in rs[1:]:
        first.remove(r)
    for br in first.findall('a:br', NS):
        first.remove(br)
    lines = text.split('\n')
    rs[0].find('a:t', NS).text = lines[0]
    for ln in lines[1:]:
        np_ = copy.deepcopy(first); np_.findall('a:r', NS)[0].find('a:t', NS).text = ln; txb.append(np_)


def by_name(slide, name):
    return next(s for s in slide.shapes if s.name == name)


def page_shape(slide):
    for s in slide.shapes:
        if s.has_text_frame and re.fullmatch(r'\s*(\d+\s*/\s*\d+|부록 [AB]\d+)\s*', s.text_frame.text):
            return s
    return None


def new_slide(prs, frame_src, title, msg, group, foot, page):
    s = prs.slides.add_slide(frame_src.slide_layout)
    for ph in list(s.placeholders):
        ph._element.getparent().remove(ph._element)
    for nm in ('Rectangle 1', 'TextBox 2', 'Rectangle 3', 'Rectangle 4', 'TextBox 5', 'TextBox 6'):
        s.shapes._spTree.append(copy.deepcopy(by_name(frame_src, nm)._element))
    set_text(by_name(s, 'TextBox 2'), title)
    by_name(s, 'TextBox 2').width = Pt(700)
    set_text(by_name(s, 'TextBox 5'), FOOT + foot)
    set_text(by_name(s, 'TextBox 6'), f'{page} / {TOTAL}')
    frags = []
    if group:
        frags.append(shape(8, 740, 26, 180, 26, [para((group, 13, True, MUTED), 'r')], ins=(0, 0, 0, 0), anchor='ctr'))
    if msg:
        frags.append(shape(9, 40, 69, 880, 28, [para((msg, 15, True, NAVY))], ins=(0, 0, 0, 0), anchor='ctr'))
    add_xml(s, frags)
    return s


def pic(slide, path, x, y, w=None, h=None):
    return slide.shapes.add_picture(path, Pt(x), Pt(y), Pt(w) if w else None, Pt(h) if h else None)


# ---------- 각 장 ----------
def build(prs, O):
    S = {}
    fr = O[2]   # v11 3쪽을 틀로

    # 3 TSFM 예측구간의 위험 관리 활용
    s = new_slide(prs, fr, 'TSFM 예측구간의 위험 관리 활용', 'TSFM이 낸 80% 구간의 아래 끝은 손실 한도(VaR 10%)로 쓰이므로, 실제값이 구간에 80% 들어오는지(커버리지)가 중요하다',
                  '연구 배경', '본문 1.1절, 2.3~2.4절', 3)
    B = [('과거 수익률', ['한 종목의 일별 수익률', '(과거 21일 또는 252일)']), ('TSFM', ['미리 학습된 모델', '추가 학습 없이 예측']),
         ('분위수 9개', ['다음 날 수익률의', '10%~90% 분위수']), ('80% 예측구간', ['10% ~ 90% 분위수', '(명목 커버리지 80%)']),
         ('VaR 10%', ['구간의 아래 끝', '= 하루 손실 한도'])]
    fr_ = []
    for i, (t, ls) in enumerate(B):
        xx = 40 + i * 182
        fr_.append(box(100 + i, xx, 106, 154, 80, t, ls, hl=(i == 4), tsz=14.5, bsz=12))
        if i < 4:
            fr_.append(arrow(110 + i, xx + 159, 136))
    add_xml(s, fr_)
    src = O[2]
    for nm, (y,) in (('TextBox 14', (198,)), ('Table 15', (222,)), ('TextBox 17', (392,))):
        el = copy.deepcopy(by_name(src, nm)._element); s.shapes._spTree.append(el)
        shp = by_name(s, nm); shp.left = Pt(40); shp.top = Pt(y)
    by_name(s, 'TextBox 14').width = Pt(880); by_name(s, 'TextBox 17').width = Pt(880)
    pic(s, f'{FIG}/slide3_예측구간_VaR.png', 540, 216, 380, 167)
    add_xml(s, [shape(120, 40, 425, 880, 60, [para([('커버리지', 14, True, NAVY), (': 실제 수익률이 예측구간 안에 든 날의 비율(실현 커버리지). 구간이 약속한 비율(명목 커버리지, 80%)과 같아야 '
                                                   'VaR 10%를 넘는 날도 10%가 된다.', 14, False, BODY)])], 'roundRect', FILL, '94A3B8', 0.8, 'ctr', (12, 6, 12, 6))])
    S[3] = s

    # 4 금융 TSFM 연구에서 확인되지 않은 것
    s = new_slide(prs, fr, '금융 TSFM 연구에서 확인되지 않은 것', '금융 TSFM 연구는 점 예측 정확도만 비교했고, 합성 데이터 진단 연구는 TSFM 예측구간을 다루지 않았다',
                  '연구 배경', '본문 1.1절, 2.6절, 표 2-1', 4)
    rows = [['연구 갈래', '한 것', '하지 않은 것'],
            [[[('금융 TSFM 평가', 14.5, True, NAVY)], [('Rahimikia 외(2025), Noguer i Alonso·Franklin(2026), Upadhyay(2026)', 11.5, False, MUTED)]],
             [[('제로샷 TSFM의 금융 수익률 점 예측 정확도 비교', 14, False, BODY)], [('→ 단순 기준 모형을 크게 넘지 못함', 14, False, BODY)]],
             [[('수익률 예측구간의 커버리지', 14.5, True, ORANGE)]]],
            [[[('합성 데이터 진단', 14.5, True, NAVY)], [('FinStressTS(Sun 외, 2026)', 11.5, False, MUTED)]],
             [[('금융 구조를 하나씩 조절한 합성 데이터로', 14, False, BODY)], [('학습형 예측 모델의 약점 진단', 14, False, BODY)]],
             [[('사전학습 TSFM, 예측구간의 커버리지', 14.5, True, ORANGE)]]],
            [[[('사후보정', 14.5, True, NAVY)], [('CQR(Romano 외, 2019), ACI(Gibbs·Candès, 2021)', 11.5, False, MUTED)]],
             [[('모델과 무관하게 구간의 커버리지를 맞추는 방법', 14, False, BODY)]],
             [[('금융 TSFM 예측구간에 적용·검증', 14.5, True, ORANGE)]]]]
    add_xml(s, [table(100, 40, 108, [300, 330, 250], rows, [34, 78, 78, 78]),
                shape(101, 40, 395, 880, 90, [para([('확인되지 않은 세 가지', 14.5, True, NAVY)], aft=4),
                                              para([('① 구간이 명목 커버리지(80%)를 지키는가  ② 지키지 못한다면 원인이 금융 특성인가, 모델·입력 설정인가  '
                                                     '③ 재학습 없는 사후보정으로 바로잡을 수 있는가', 14, False, BODY)])],
                      'roundRect', 'FFF4EE', ORANGE, 1.2, 'ctr', (12, 6, 12, 6))])
    S[4] = s

    # 5 연구 질문
    s = new_slide(prs, fr, '연구 질문: 진단·실증·사후보정', '커버리지 오차의 원인을 합성 데이터로 진단하고(RQ1), 실제 주가로 평가하고(RQ2), 재학습 없이 바로잡는다(RQ3)',
                  '연구 질문과 실험 구성', '본문 1.2절', 5)
    rows = [['연구 질문', '질문', '쓰는 데이터'],
            [[[('RQ1 진단', 15, True, NAVY)]], '금융 특성(변동성 군집, 두꺼운 꼬리, 국면 전환의 빈도와 크기)이 강해질수록 TSFM 80% 예측구간의 커버리지가 떨어지는가, 아니면 모델과 입력 설정에서 이미 오차가 생기는가?', '합성 데이터'],
            [[[('RQ2 실증', 15, True, NAVY)]], '실제 미국·한국 대형주에서 TSFM 예측구간의 커버리지와 분포 정확도는 어떠하며, 단순 기준 모형(RW)보다 나은가?', '실제 10종목'],
            [[[('RQ3 사후보정', 15, True, NAVY)]], '모델을 재학습하지 않는 사후보정(ACI-CQR)으로 커버리지를 80%로 복원할 수 있는가? 그 대가로 구간은 얼마나 넓어지는가?', '두 데이터 모두']]
    add_xml(s, [table(100, 40, 112, [160, 560, 160], rows, [36, 112, 100, 100], sz=14.5, aligns=['ctr', 'l', 'ctr']),
                shape(101, 40, 470, 880, 24, [para(('RW: 과거 수익률의 평균과 표준편차로 만든 정규분포(과거변동 기준선). ACI-CQR: 적응형 콘포멀 분위수 보정', 12, False, MUTED))], ins=(0, 0, 0, 0))])
    S[5] = s

    # 6 실험 전체 구성
    s = new_slide(prs, fr, '실험 전체 구성', '모델 6개(19개 모델·조건)를 합성 데이터와 실제 10종목에 같은 80일 절차로 적용하고, 커버리지 78~82%를 적정으로 판정한다',
                  '연구 질문과 실험 구성', '본문 3.1~3.4절, 3.6절, 표 3-1, 표 3-6', 6)
    f = [box(100, 40, 106, 250, 150, '합성 데이터', ['실제 10종목에서 잰 강도로', '금융 특성을 하나씩 넣음', 'L1(특성 없음) + 4개 특성 × L2~L5', '= 17개 시나리오 × 100계열'], bsz=13),
         box(101, 40, 266, 250, 114, '실제 10종목', ['미국 5 · 한국 5 대형주', '2017~2026년, 평가 17,700건'], bsz=13),
         arrow(102, 296, 233),
         box(103, 320, 106, 300, 274, '모델 6개 (19개 모델·조건)', ['TSFM 4개 × 입력 조건 4개 = 16', 'Chronos-T5, Chronos-2,', 'TimesFM-2.5, Moirai-2',
                                                                '과거 21일·252일 × 수익률·가격', '기준 모형 = 3', 'RW(21일·252일), GARCH-t(252일)', ' ', '같은 절차: 80일 단위', '(준비 20일 + 평가 60일)',
                                                                '매일 다음 날 80% 예측구간'], bsz=13),
         arrow(104, 626, 233)]
    for i, (t, d) in enumerate([('RQ1 진단', '합성 데이터: 오차가 금융 특성과 모델·설정 중 어디에서 커지는가'),
                                ('RQ2 실증', '실제 10종목: 커버리지와 분포 정확도, 합성 결과와 비교'),
                                ('RQ3 사후보정', '두 데이터: ACI-CQR로 80% 복원과 구간 폭')]):
        f.append(box(105 + i, 650, 106 + i * 95, 270, 84, t, [d], hl=True, tsz=14.5, bsz=12.5))
    for i, (t, d) in enumerate([('커버리지', '78~82%를 적정으로 판정 (6,000건 표본 오차 약 ±1%p)'), ('분포 정확도', '분위수 손실, RW 대비 개선율'),
                                ('위험 관리', 'VaR 10% 위반율 검정 (탐색 분석)')]):
        f.append(shape(110 + i, 40 + i * 297, 398, 286, 64, [para((t, 14, True, NAVY), aft=2), para((d, 12.5, False, BODY))], 'roundRect', 'FFFFFF', '94A3B8', 0.8, 'ctr', (10, 4, 10, 4)))
    add_xml(s, f)
    S[6] = s

    # 7 합성 데이터 설계와 가설
    s = new_slide(prs, fr, '합성 데이터 설계와 가설', '실제 10종목에서 잰 강도로, 같은 난수에 금융 특성을 하나씩 넣어 17개 시나리오를 만들었다',
                  'RQ1 진단', '본문 3.2절, 3.6.2절, 그림 3-2, 표 3-7  |  자세히: 부록 B3', 7)
    BX = [('① 실제 10종목에서 강도 측정', ['GARCH-t: 군집(α+β)·꼬리(ν)', '2국면 모형: 전환 빈도·크기']),
          ('② 강도 단계 정하기', ['L1 특성 없음(정규분포)', 'L3 가장 약한 종목, L4 중앙값', 'L5 가장 강한 종목, L2 중간']),
          ('③ 특성 하나씩 넣어 생성', ['같은 난수 100개 계열', '하루 변동 2.11%·평균 0 고정']),
          ('④ 생성 검증', ['오라클 모형 커버리지', '79.3~80.2%', '→ 의도대로 생성됨'])]
    f = []
    for i, (t, ls) in enumerate(BX):
        xx = 40 + i * 227
        f.append(box(100 + i, xx, 106, 199, 104, t, ls, tsz=13.5, bsz=12))
        if i < 3:
            f.append(arrow(110 + i, xx + 204, 148))
    hyp = [['가설', '내용 (실험 전에 고정)'], ['H1', '군집이 강해질수록 커버리지 하락'], ['H2', '꼬리가 두꺼울수록 하락'], ['H3a', '국면 전환이 잦을수록 하락'],
           ['H3b', '국면 전환 충격이 클수록 하락'], ['H4', '강한 단계(L4·L5)에서 특성마다 커버리지가 다르다']]
    f.append(table(120, 500, 226, [70, 350], hyp, [30, 34, 34, 34, 34, 34], sz=13.5, aligns=['ctr', 'l']))
    f.append(shape(121, 500, 432, 420, 56, [para(('H1~H3b는 "금융 특성이 예측 모델에 불리하다"는 기존 연구(Sun 외, 2026)의 관점을 그대로 세운 것', 12.5, False, MUTED))], ins=(0, 0, 0, 0)))
    add_xml(s, f)
    pic(s, f'{FIG}/slide6_합성예시.png', 40, 226, 430, 272)
    S[7] = s

    # 8 금융 특성 강도와 커버리지 변화
    s = new_slide(prs, fr, '금융 특성 강도와 커버리지 변화', '특성을 L1에서 L5로 강하게 해도 커버리지 변화는 대부분 3%p 이내였고, 커버리지를 낮춘 특성은 변동성 군집뿐이었다',
                  'RQ1 진단', '본문 4.3절, 표 4-2, 그림 4-2', 8)
    pic(s, f'{V12}/p08_특성강도_변화.png', 40, 102, None, 396)
    add_xml(s, [note(100, 676, 112, 244, 376, ['군집  −0.8%p', '꼬리  +1.9%p', '전환 빈도  +1.3%p', '전환 크기  +0.2%p',
                                                [('64개 중 63개', 14, True, BODY), ('가 ±3%p 이내', 14, False, BODY)],
                                                [('꼬리·전환 빈도는 커버리지를 ', 14, False, BODY), ('오히려 높임', 14, True, ORANGE), (' (H2·H3a와 반대 방향)', 14, False, BODY)]],
                     title='L5 − L1 중앙값 (TSFM 16개 조건)')])
    S[8] = s

    # 9 예상과 다른 발견
    s = new_slide(prs, fr, '예상과 다른 발견', '두꺼운 꼬리는 80% 구간의 커버리지를 높이고 98~99% 구간의 커버리지를 낮춘다',
                  'RQ1 진단', '본문 2.1.2절, 4.3.2절, 그림 2-1, 표 4-3, 표 4-4', 9)
    pic(s, f'{V12}/p09_꼬리_구간수준.png', 40, 106, 880, 352)
    add_xml(s, [shape(100, 40, 462, 880, 34, [para([('따라서 80% 구간 하나의 커버리지만 보고 꼬리 위험(극단 손실)을 판단하면 틀릴 수 있다 ', 14, True, NAVY), ('(기여 C2, 평가 관점)', 13, False, MUTED)])], ins=(0, 0, 0, 0), anchor='ctr')])
    S[9] = s

    # 10 모델별·입력 조건별 커버리지 차이
    s = new_slide(prs, fr, '모델별·입력 조건별 커버리지 차이', '특성이 없는 L1에서도 커버리지는 모델·입력 조건에 따라 75~88%였고, 라이브러리 기본 설정 하나로 14%까지 떨어졌다',
                  'RQ1 진단', '본문 4.2절, 표 4-1, 논문 부록 A.3  |  자세히: 부록 B1, B2', 10)
    pic(s, f'{V12}/p10_L1_조건별.png', 40, 102, None, 396)
    add_xml(s, [note(100, 694, 112, 226, 376, [[('16개 중 8개', 14, True, ORANGE), ('가 적정 범위(78~82%) 밖', 14, False, BODY)],
                                                '같은 모델도 입력 조건에 따라 다름: TimesFM-2.5 77.2~87.6%',
                                                '금융 특성이 없는 데이터라서, 이 차이는 금융 특성으로 설명되지 않음'], title='L1 (금융 특성 없음)')])
    S[10] = s

    # 11 모델·설정과 금융 특성의 영향 비교
    s = new_slide(prs, fr, '모델·설정과 금융 특성의 영향 비교', '커버리지 차이의 90%는 모델·조건으로, 7%는 금융 특성으로 설명된다',
                  'RQ1 진단', '본문 4.2절, 1.4절', 11)
    pic(s, f'{V12}/p11_분해.png', 40, 112, 880, 286)
    add_xml(s, [shape(100, 40, 410, 880, 76, [para([('RQ1의 답', 14.5, True, NAVY)], aft=3),
                                              para([('본 실험 범위에서 TSFM 예측구간의 커버리지는 금융 특성보다 모델과 입력 설정에 따라 더 크게 달라졌다. '
                                                     '가장 크게 벗어난 TimesFM-2.5 1년·가격을 빼도 모델·입력 조건의 몫(76%)이 금융 특성(18%)보다 크다.', 14, False, BODY)])],
                      'roundRect', FILL, '94A3B8', 0.8, 'ctr', (12, 6, 12, 6))])
    S[11] = s

    # 12 실증 종목 선정과 평가 방법
    s = new_slide(prs, fr, '실증 종목 선정과 평가 방법', '미국 5종목은 선행연구와 같은 종목, 한국 5종목은 2017년 초 시가총액 순으로 골라 사후 선택 편향을 막았다',
                  'RQ2 실증', '본문 3.3절, 표 3-5, 3.6.2절  |  자세히: 부록 B8', 12)
    rows = [['구분', '종목', '선정 근거'],
            [[[('미국 5종목', 14.5, True, NAVY)]], 'AAPL, AMZN, GOOG, JPM, META', '선행연구(Noguer i Alonso·Franklin, 2026)와 같은 종목. 모두 2017년 초 미국 시가총액 상위 10위 안의 대형주'],
            [[[('한국 5종목', 14.5, True, NAVY)]], '삼성전자, SK하이닉스, 현대차, 한국전력, 현대모비스', '평가 시작일(2017-01-02) KOSPI 보통주 시가총액 순. 지금 기준으로 고르면 그동안 성장한 종목만 남는 편향이 생김'],
            [[[('평가', 14.5, True, NAVY)]], '2017~2026년 매 거래일 다음 날 예측', '합성 데이터와 같은 80일 단위(준비 20일 + 평가 60일)로 나눠 두 결과를 직접 비교. 평가 17,700건']]
    add_xml(s, [table(100, 40, 110, [130, 290, 460], rows, [34, 86, 86, 86], sz=14, aligns=['ctr', 'l', 'l']),
                shape(101, 40, 422, 880, 64, [para([('가설 H5', 14.5, True, NAVY), ('  실제 주식에서 TSFM이 RW보다 분위수 손실이 작다 (같은 날·종목·과거 길이로 비교, 달력 월 단위 검정)', 14, False, BODY)])],
                      'roundRect', FILL, '94A3B8', 0.8, 'ctr', (12, 6, 12, 6))])
    S[12] = s

    # 13 합성 데이터와 실제 주가의 비교
    s = new_slide(prs, fr, '합성 데이터와 실제 주가의 비교', '실제 10종목의 커버리지는 L1과 평균 1.1%p 달랐고, 크게 벗어난 두 설정은 합성 데이터에서 먼저 드러났다',
                  'RQ2 실증', '본문 5.1절, 5.4절, 그림 5-3, 논문 부록 A.3  |  자세히: 부록 B8', 13)
    pic(s, f'{V12}/p13_합성_실제.png', 40, 102, None, 396)
    add_xml(s, [note(100, 560, 112, 360, 376, ['19개 모델·조건에서 합성 L1과 실제의 차이 평균 1.1%p, 최대 3.6%p',
                                                'TimesFM-2.5 1년·가격: 합성 87.6% → 실제 87.7%',
                                                'Chronos-T5 기본 설정(수익률): 합성 14~16% → 실제 17~18%',
                                                [('→ 크게 벗어나는 설정은 실제 데이터에 쓰기 전에 합성 데이터로 걸러낼 수 있다', 14, True, NAVY)],
                                                [('단, 2%p 이내의 작은 차이까지 맞히지는 못함 (p = 0.07)', 13, False, MUTED)]], title='읽는 법: 점선에 가까울수록 합성과 실제가 같음')])
    S[13] = s

    # 14 기준 모형 대비 분포 정확도
    s = new_slide(prs, fr, '기준 모형 대비 분포 정확도', 'TSFM 16개 조건 중 12개에서 분위수 손실이 RW보다 유의하게 컸고, RW보다 실질적으로 나은 조건은 없었다',
                  'RQ2 실증', '본문 5.2~5.3절, 5.6절, 표 5-2, 그림 5-2  |  자세히: 부록 B7', 14)
    pic(s, f'{V12}/p14_RW대비_정확도.png', 40, 102, None, 396)
    add_xml(s, [note(100, 666, 112, 254, 376, [[('12개', 14, True, ORANGE), (': RW보다 유의하게 부정확 (−0.8~−9.8%, 한 달 또는 가격 입력)', 14, False, BODY)],
                                                [('3개', 14, True, BODY), (': 차이 없음 (1년·수익률)', 14, False, BODY)],
                                                [('1개', 14, True, BODY), (': Chronos-2 1년·수익률 +0.9%, 실질 기준 2% 미만', 14, False, BODY)],
                                                [('→ 가설 H5 지지되지 않음', 14, True, NAVY)]], title='분위수 손실: 작을수록 정확')])
    S[14] = s

    # 15 ACI-CQR 보정 방법
    s = new_slide(prs, fr, 'ACI-CQR 보정 방법', 'ACI-CQR은 모델을 그대로 두고, 최근 실제값이 구간을 벗어났는지에 따라 매일 구간 양 끝을 조정한다',
                  'RQ3 사후보정', '본문 2.5절, 3.5.1절, 3.6.2절', 15)
    BX = [('① 이탈 기록', ['매일 실제값이 구간에서', '얼마나 벗어났는지를', '구간 폭 대비 점수로 기록']),
          ('② 구간 양 끝 조정', ['기록된 점수로', '오늘 구간의 양 끝을', '넓히거나 좁힘']),
          ('③ 목표 갱신', ['실제값을 확인한 뒤', '벗어났으면 다음 구간을 넓게,', '계속 들어오면 좁게'])]
    f = []
    for i, (t, ls) in enumerate(BX):
        xx = 40 + i * 214
        f.append(box(100 + i, xx, 112, 186, 150, t, ls, bsz=13.5))
        if i < 2:
            f.append(arrow(110 + i, xx + 191, 177))
    f.append(arrow(112, 689, 177))
    f.append(box(113, 716, 112, 204, 150, '모델은 그대로', ['재학습 없음', '모델이 낸 구간만 사용', 'α = 0.20, γ = 0.05 고정'], hl=True, bsz=13.5))
    f.append(shape(120, 40, 274, 880, 26, [para(('논문 3.5.1절: 이탈 점수 s = max(l − y, y − u) / (u − l),   다음 날 목표 이탈률 α ← α + γ(0.20 − 이탈 여부)', 12.5, False, MUTED))], ins=(0, 0, 0, 0)))
    f.append(shape(121, 40, 318, 880, 70, [para([('가설 H6', 14.5, True, NAVY), ('  보정 후 커버리지가 80%로 복원된다 (판정: 커버리지 90% 신뢰구간이 77~83% 안)', 14, False, BODY)])],
                   'roundRect', FILL, '94A3B8', 0.8, 'ctr', (12, 6, 12, 6)))
    f.append(shape(122, 40, 402, 880, 80, [para([('대조군', 14.5, True, NAVY), ('  원래 구간을 같은 배율로 일괄 확대한 구간. 배율은 결과를 본 뒤 정한 값이라 실제 운용에서는 알 수 없음 → 보정은 그때까지의 실제값만으로 조정', 14, False, BODY)])],
                   'roundRect', 'FFFFFF', '94A3B8', 0.8, 'ctr', (12, 6, 12, 6)))
    add_xml(s, f)
    S[15] = s

    # 16 보정 후 커버리지와 구간 폭
    s = new_slide(prs, fr, '보정 후 커버리지와 구간 폭', '합성·실제 모든 모델·조건에서 평균 커버리지가 80%로 돌아왔고, 구간 폭은 오라클보다 5~48% 넓어졌다',
                  'RQ3 사후보정', '본문 6.1~6.3절, 표 6-1, 표 6-2, 그림 6-1  |  자세히: 부록 B5, B10', 16)
    pic(s, f'{V12}/p16_보정결과.png', 40, 102, 600, 360)
    rows = [['구간 폭 (합성)', '오라클 대비'], ['TSFM 과거 1년', '1.05~1.24배'], ['TSFM 과거 한 달', '1.14~1.48배'], ['오라클에 보정 적용', '1.05~1.09배']]
    add_xml(s, [shape(100, 40, 466, 600, 30, [para(('보정 후 평균 커버리지: 합성 340개 79.8~80.7%, 실제 19개 79.9~80.3%', 13, True, NAVY))], ins=(0, 0, 0, 0), anchor='ctr'),
                table(101, 656, 112, [146, 118], rows, [34, 40, 40, 40], sz=13.5, aligns=['l', 'ctr']),
                note(102, 656, 286, 264, 200, ['오라클 = 데이터를 만든 실제 분포로 낸 구간(80%를 맞추는 가장 좁은 구간)',
                                                '원래 80%에 가까운 조건일수록 덜 넓어짐',
                                                '1년 조건이 한 달 조건보다 비용이 작음'], sz=13)])
    S[16] = s

    # 17 VaR 백테스트
    s = new_slide(prs, fr, 'VaR 백테스트 (탐색 분석)', '구간 아래 끝을 VaR 10% 한도로 쓸 때, 10종목 중 8종목 이상에서 위반율 검정을 통과한 조건이 보정 전 8개에서 보정 후 14개로 늘었다',
                  'RQ3 사후보정', '본문 5.5.3절, 6.6절, 표 5-6  |  자세히: 부록 B6', 17)
    rows = [['VaR 10% 백테스트 (실제 10종목)', '보정 전', '', '보정 후'],
            [[[('위반율 검정을 8종목 이상 통과한 조건 (19개 중)', 14.5, True, NAVY)]], [[('8개', 20, False, BODY)]], '→', [[('14개', 22, True, '1F6FB2')]]],
            [[[('TimesFM-2.5 1년·가격 위반율', 14.5, True, NAVY)], [('구간이 넓어 손실 한도를 덜 넘던 조건', 12.5, False, MUTED)]], [[('5.5%', 17, False, BODY)]], '→', [[('9.0%', 18, True, BODY)]]],
            [[[('Moirai-2 한 달·수익률 위반율', 14.5, True, NAVY)], [('구간이 좁아 손실 한도를 자주 넘던 조건', 12.5, False, MUTED)]], [[('11.9%', 17, False, BODY)]], '→', [[('10.5%', 18, True, BODY)]]]]
    add_xml(s, [table(100, 90, 120, [440, 150, 60, 150], rows, [38, 72, 80, 80], sz=14, aligns=['l', 'ctr', 'ctr', 'ctr']),
                shape(101, 90, 410, 800, 70, [para(('위반율 = 실제 손실이 VaR 10%(80% 구간 아래 끝)를 넘은 날의 비율, 목표 10%. 위반율 검정 = Kupiec 검정(금융기관 VaR 백테스트와 같은 방식).', 13, False, MUTED)),
                                              para(('투자 규칙에 적용한 탐색 분석으로, 실험 전에 정한 가설 검정에는 포함하지 않음.', 13, False, MUTED), bef=4)], ins=(0, 0, 0, 0))])
    S[17] = s

    # 18 실무 도입 절차
    s = new_slide(prs, fr, '실무 도입 절차', '합성 데이터로 모델·설정을 먼저 점검하고, 사후보정을 붙여 쓰고, 방향 예측에는 쓰지 않는다',
                  '결론', '본문 7.2절', 18)
    BX = [('① 합성 데이터로 점검', ['실측 강도로 만든 합성 데이터에서', '모델·입력 설정의 커버리지 확인', ' ', '예: TimesFM-2.5 1년·가격 88%,', 'Chronos-T5 기본 설정 14~16%를', '실제 적용 전에 발견'], False),
          ('② 사후보정을 붙여 사용', ['ACI-CQR로 평균 커버리지를 80%로', ' ', '재학습 없음, 계산 비용 거의 없음', 'VaR 검정 통과 8개 → 14개'], False),
          ('③ 용도 제한', ['방향 예측에는 쓰지 않음', ' ', '위험 측정에 쓸 때도 정확도는', '기준 모형(RW) 수준임을 전제'], True)]
    f = []
    for i, (t, ls, hl) in enumerate(BX):
        xx = 40 + i * 304
        f.append(box(100 + i, xx, 116, 272, 250, t, ls, hl=hl, tsz=16, bsz=14))
        if i < 2:
            f.append(arrow(110 + i, xx + 277, 231, 22, 24))
    f.append(shape(120, 40, 390, 880, 90, [para([('모델 내부 구조를 쓰지 않는 절차', 14.5, True, NAVY)], aft=3),
                                           para(('금융기관이 위험 측정 모형을 도입 전에 검증하고 VaR를 사후 점검하는 체계에, 내부를 들여다보기 어려운 사전학습 모델을 그대로 넣을 수 있다.', 14, False, BODY))],
                   'roundRect', FILL, '94A3B8', 0.8, 'ctr', (12, 6, 12, 6)))
    add_xml(s, f)
    S[18] = s

    # 19 결론과 연구 기여
    s = new_slide(prs, fr, '결론과 연구 기여', '세 연구 질문의 답과 기여 네 가지', '결론', '본문 1.4절, 7.1절, 표 7-1  |  자세히: 부록 B4', 19)
    cols = [('연구 질문', [('RQ1 진단', '금융 특성이 강해질수록 커버리지가 낮아지는가?'), ('RQ2 실증', '실제 주가에서 커버리지와 분포 정확도는?'), ('RQ3 사후보정', '재학습 없이 80%로 되돌릴 수 있는가?')]),
            ('답', [('모델·설정의 영향이 더 컸다', 'L1에서도 75~88%, 차이의 90%는 모델·조건, 7%는 금융 특성'), ('합성과 가까웠고, 정확도는 RW 수준', '차이 평균 1.1%p, 16개 중 12개가 RW보다 손실 큼'),
                    ('평균 커버리지가 80%로 돌아왔다', '모든 조건, 구간 폭은 오라클보다 5~48% 넓음')]),
            ('기여', [('C1 방법론', '실측 기반 합성 데이터로 실제 적용 전 점검'), ('C2 평가 관점', '꼬리가 80%와 98~99% 구간의 커버리지를 반대로 바꿈'),
                     ('C3 실증', '최신 TSFM 4종, 미국·한국 대형주, 실험 전 고정한 기준'), ('C4 실무', '점검 → 사후보정 → 용도 제한 절차')])]
    f = []
    for ci, (head, items) in enumerate(cols):
        xx = 40 + ci * 300
        f.append(shape(100 + ci, xx, 104, 280, 30, [para((head, 16, True, 'FFFFFF'), 'ctr')], 'roundRect', NAVY, None, anchor='ctr', ins=(4, 2, 4, 2)))
        n = len(items); hh = (500 - 142 - (n - 1) * 8) / n
        for k, (t, d) in enumerate(items):
            f.append(shape(110 + ci * 10 + k, xx, 142 + k * (hh + 8), 280, hh, [para((t, 14.5, True, NAVY), aft=3), para((d, 13, False, BODY))],
                           'roundRect', FILL if ci < 2 else 'FFF4EE', '94A3B8' if ci < 2 else ORANGE, 0.9, 'ctr', (10, 4, 10, 4)))
    add_xml(s, f)
    S[19] = s
    return S


APPX = [  # (v11 순서 번호(1부터), 새 부록 번호, 새 제목)
    (9, 'B1', '부록 B1: 합성 데이터 시나리오별 커버리지'), (10, 'B2', '부록 B2: 라이브러리 기본 설정 사례'), (7, 'B3', '부록 B3: 합성 데이터 생성과 검증'),
    (19, 'B4', '부록 B4: 가설 판정 요약'), (18, 'B5', '부록 B5: 시기별 커버리지'), (17, 'B6', '부록 B6: 투자 규칙 적용 (탐색 분석)'),
    (23, 'B7', '부록 B7: 모델 공개 이후 기간 점검'), (24, 'B8', '부록 B8: 종목별 커버리지'), (25, 'B9', '부록 B9: 추가 민감도 점검'),
    (26, 'B10', '부록 B10: 일괄 확대 대조군 비교'), (27, 'B11', '부록 B11: 질의 대비 ① "원인 진단"은 무엇을 검정했는가'),
    (28, 'B12', '부록 B12: 질의 대비 ② 꼬리 가설(H2)을 왜 "하락"으로 세웠는가'), (29, 'B13', '부록 B13: 질의 대비 ③ 사후보정의 의미와 Chronos-T5 재실행')]
A2B = {f'부록 A{i}': f'부록 B{i + 6}' for i in range(1, 8)}


def fix_refs(slide):
    for sh in slide.shapes:
        if not sh.has_text_frame:
            continue
        for p in sh.text_frame.paragraphs:
            for r in p.runs:
                t = r.text
                t2 = re.sub(r'부록 A([1-7])(?![\.\d])', lambda m: f'부록 B{int(m.group(1)) + 6}', t)
                t2 = t2.replace('부록 A1~A7', '부록 B1~B13')
                if t2 != t:
                    r.text = t2


def main(src, out):
    prs = Presentation(src)
    O = list(prs.slides)
    S = build(prs, O)
    # 1 표지, 2 목차(v11 2쪽 수정), 20 한계, 21 질의응답
    toc = O[1]
    rows = [('연구 배경', 'TSFM 예측구간의 위험 관리 활용, 금융 TSFM 연구에서 확인되지 않은 것', '3~4쪽'),
            ('연구 질문과 실험 구성', '연구 질문: 진단·실증·사후보정, 실험 전체 구성', '5~6쪽'),
            ('RQ1 진단 (합성 데이터)', '합성 데이터 설계와 가설, 금융 특성 강도와 커버리지 변화, 예상과 다른 발견, 모델별·입력 조건별 커버리지 차이, 영향 비교', '7~11쪽'),
            ('RQ2 실증 (실제 10종목)', '실증 종목 선정과 평가 방법, 합성 데이터와 실제 주가의 비교, 기준 모형 대비 분포 정확도', '12~14쪽'),
            ('RQ3 사후보정', 'ACI-CQR 보정 방법, 보정 후 커버리지와 구간 폭, VaR 백테스트', '15~17쪽'),
            ('결론', '실무 도입 절차, 결론과 연구 기여, 한계와 향후 과제 (부록 B1~B13 별첨)', '18~20쪽')]
    for (t, d, pg), tb, pb in zip(rows, ['TextBox 9', 'TextBox 13', 'TextBox 17', 'TextBox 21', 'TextBox 25', 'TextBox 29'],
                                  ['TextBox 10', 'TextBox 14', 'TextBox 18', 'TextBox 22', 'TextBox 26', 'TextBox 30']):
        shp = by_name(toc, tb); ps = shp.text_frame.paragraphs
        ps[0].runs[0].text = t; [r._r.getparent().remove(r._r) for r in ps[0].runs[1:]]
        ps[1].runs[0].text = d; [r._r.getparent().remove(r._r) for r in ps[1].runs[1:]]
        set_text(by_name(toc, pb), pg)
    set_text(by_name(toc, 'TextBox 6'), f'2 / {TOTAL}')
    lim = O[20]
    set_text(by_name(lim, 'TextBox 2'), '한계와 향후 과제')
    set_text(by_name(lim, 'TextBox 6'), f'20 / {TOTAL}')
    fix_refs(lim)
    qa = O[21]
    set_text(by_name(qa, 'TextBox 4'), '부록 B1~B13: 시나리오별 커버리지 · 기본 설정 사례 · 합성 데이터 생성 · 가설 판정 · 시기별 · 투자 규칙 · 공개 이후 기간 · 종목별 · 민감도 · 대조군 · 질의 대비 3장')
    for n, code, title in APPX:
        sl = O[n - 1]
        set_text(by_name(sl, 'TextBox 2'), title)
        pg = page_shape(sl)
        if pg is not None:
            set_text(pg, f'부록 {code}')
        fix_refs(sl)
        if code == 'B4':
            for sh in sl.shapes:
                if sh.has_table:
                    for row in sh.table.rows:
                        for c in row.cells:
                            for pp in c.text_frame.paragraphs:
                                for r in pp.runs:
                                    if '모두 77~83%' in r.text:
                                        r.text = '합성 323개·실제 19개 모두 판정 범위(77~83%) 안, 보정 후 평균 79.8~80.7%. 위반 몰림은 일부 조건에 남음'
    # 순서: 1, 2, 새 3~19, 20(한계), 21(질의응답), 부록
    order = [O[0], O[1]] + [S[k] for k in range(3, 20)] + [lim, qa] + [O[n - 1] for n, _, _ in APPX]
    lst = prs.slides._sldIdLst
    ids = {sl.slide_id: el for el in lst for sl in [None] if False}
    elmap = {int(el.get('id')): el for el in lst}
    keep = [elmap[sl.slide_id] for sl in order]
    drop = [el for el in lst if el not in keep]
    for el in list(lst):
        lst.remove(el)
    for el in keep:
        lst.append(el)
    for el in drop:
        prs.part.drop_rel(el.get('{%s}id' % NS['r']))
    prs.save(out)
    print('slides', len(keep), 'dropped', len(drop))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
