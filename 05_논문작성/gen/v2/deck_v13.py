"""발표 v13: v12 위에 (1) 진행 표시줄(A안, 제목 줄 오른쪽), (2) 17쪽 19개 조건 그림, (3) 부록 B1~B13 재구성(본편과 같은 틀·한 줄 메시지·문장 정리, 본편 순서로 재번호),
(4) 본편 → 부록, 부록 → 본편 이동 링크와 '← 보던 장으로' 단추를 넣는다. 결정로그 193~194차.
사용: python3 deck_v13.py <v12.pptx> <out_v13.pptx>
"""
import sys, os, re, copy, io
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import deck_v12 as D
from deck_v12 import (shape, para, box, arrow, table, note, add_xml, new_slide, set_text, by_name, pic, NAVY, BODY, FILL, MUTED, ORANGE, FIG, V12, NS)
from pptx import Presentation
from pptx.util import Pt
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from lxml import etree

A, R = NS['a'], NS['r']
P = NS['p']
AHYP = 'http://schemas.microsoft.com/office/drawing/2018/hyperlinkcolor'
TMP = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_tmp_v13')
os.makedirs(TMP, exist_ok=True)

NAV = ['배경', '질문·구성', 'RQ1 진단', 'RQ2 실증', 'RQ3 보정', '결론']
NAV_OF = {3: 0, 4: 0, 5: 1, 6: 1, 7: 2, 8: 2, 9: 2, 10: 2, 11: 2, 12: 3, 13: 3, 14: 3, 15: 4, 16: 4, 17: 4, 18: 5, 19: 5, 20: 5}
SHORT = {1: '생성 검증', 2: '시나리오별 커버리지', 3: '기본 설정 사례', 4: '종목별 커버리지', 5: '공개 이후 기간', 6: '일괄 확대 대조군', 7: '변동성 수준별',
         8: '추가 민감도', 9: '투자 규칙', 10: '가설 판정', 11: '원인 진단 질의', 12: '꼬리 가설 질의', 13: '사후보정 질의'}
LINKS = {7: [1], 8: [2], 9: [12], 10: [3], 11: [2, 11], 13: [3, 4, 5], 14: [5, 8], 15: [6], 16: [6, 7, 8, 13], 18: [9], 19: [10]}
BACKREF = {}
for pg, bs in LINKS.items():
    for b in bs:
        BACKREF.setdefault(b, []).append(pg)
NMAIN = 21


def bpage(b):
    return NMAIN + b


# ---------- 링크 ----------
def link_rpr(rpr, rid):
    h = etree.SubElement(rpr, f'{{{A}}}hlinkClick')
    h.set(f'{{{R}}}id', rid); h.set('action', 'ppaction://hlinksldjump')
    el = etree.SubElement(h, f'{{{A}}}extLst'); ext = etree.SubElement(el, f'{{{A}}}ext')
    ext.set('uri', '{A12FA001-AC4F-418D-AE19-62706E023703}')
    c = etree.SubElement(ext, f'{{{AHYP}}}hlinkClr', nsmap={'ahyp': AHYP}); c.set('val', 'tx')


def set_footer(slide, pieces, order):
    """pieces: [(text, target_page or None)] — 바닥글 TextBox 5의 첫 run 서식으로 다시 만든다."""
    tb = by_name(slide, 'TextBox 5'); p_ = tb.text_frame.paragraphs[0]._p
    runs = p_.findall(f'{{{A}}}r'); base = runs[0]
    for r in runs:
        p_.remove(r)
    for br in p_.findall(f'{{{A}}}br'):
        p_.remove(br)
    end = p_.find(f'{{{A}}}endParaRPr')
    for t, pg in pieces:
        r = copy.deepcopy(base); r.find(f'{{{A}}}t').text = t
        rpr = r.find(f'{{{A}}}rPr')
        for o in rpr.findall(f'{{{A}}}hlinkClick'):
            rpr.remove(o)
        if pg is not None:
            rid = slide.part.relate_to(order[pg - 1].part, RT.SLIDE)
            link_rpr(rpr, rid)
            rpr.set('b', '1')
        if end is not None:
            end.addprevious(r)
        else:
            p_.append(r)
    tb.width = Pt(790)


def back_button(slide):
    add_xml(slide, [f'<p:sp><p:nvSpPr><p:cNvPr id="390" name="back-to-last-viewed"><a:hlinkClick r:id="" action="ppaction://hlinkshowjump?jump=lastslideviewed"/></p:cNvPr><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
                    f'<p:spPr><a:xfrm><a:off x="{int(40*D.EMU)}" y="{int(509*D.EMU)}"/><a:ext cx="{int(92*D.EMU)}" cy="{int(19*D.EMU)}"/></a:xfrm><a:prstGeom prst="roundRect"><a:avLst/></a:prstGeom>'
                    f'<a:solidFill><a:srgbClr val="{NAVY}"/></a:solidFill><a:ln><a:noFill/></a:ln></p:spPr><p:txBody><a:bodyPr lIns="0" tIns="0" rIns="0" bIns="0" anchor="ctr"/><a:lstStyle/>'
                    f'{para(("← 보던 장으로", 10.5, True, "FFFFFF"), "ctr")}</p:txBody></p:sp>'])


# ---------- 진행 표시줄 ----------
def nav(slide, cur):
    for sh in list(slide.shapes):
        if sh.name == 'v12 8':
            sh._element.getparent().remove(sh._element)
    ws = [40, 62, 62, 62, 62, 40]; x = 572; fr = []
    for i, (t, w) in enumerate(zip(NAV, ws)):
        on = i == cur
        fr.append(shape(300 + i, x, 27, w, 22, [para((t, 10.5, on, 'FFFFFF' if on else '94A3B8'), 'ctr')], 'roundRect', NAVY if on else 'F1F5F9', None, anchor='ctr', ins=(1, 0, 1, 0)))
        x += w + 3
    add_xml(slide, fr)
    by_name(slide, 'TextBox 2').width = Pt(525)


# ---------- 부록 장 ----------
def card(sid, x, y, w, h, title, lines, sz=13.5):
    ps = [para((title, sz + 1, True, NAVY), aft=4)] + [para((l, sz, False, BODY), bef=3) for l in lines]
    return shape(sid, x, y, w, h, ps, 'roundRect', FILL, '94A3B8', 0.8, 't', (10, 8, 10, 8))


def bullets(sid, x, y, w, h, lines, sz=13):
    return shape(sid, x, y, w, h, [para((('• ' + l) if not l.startswith('→') else l, sz, False, BODY), bef=5) for l in lines], ins=(0, 0, 0, 0))


def appx(prs, fr, b, title, msg, foot):
    s = new_slide(prs, fr, f'부록 B{b}: {title}', msg, '부록', foot, 0)
    set_text(by_name(s, 'TextBox 6'), f'부록 B{b}')
    return s


def build_appx(prs, fr, pics):
    S = {}
    # B1 생성 검증
    s = appx(prs, fr, 1, '합성 데이터 생성 검증', '생성한 데이터는 목표값과 맞았고, 정답 분포를 아는 오라클 모형의 커버리지는 79.3~80.2%였다', '본문 3.2.6절, 표 3-4, 4.1절')
    rows = [['확인 항목', '목표', '생성 결과'], ['하루 변동 (17개 시나리오)', '2.11%', '2.08~2.19%'], ['±3σ 초과일 비율 (꼬리 L5)', '1.379%', '1.386%'],
            ['변동비 (전환 크기 L5)', '3.19배', '3.21배'], ['격변 일수 비율 (국면 전환)', '17.6%', '16.6~17.7%'], ['오라클 모형 커버리지', '80%', '79.3~80.2%']]
    add_xml(s, [shape(100, 40, 108, 480, 22, [para(('100개 계열 전체(시나리오당 33,200일)로 목표값과 생성 결과를 비교', 13, False, MUTED))], ins=(0, 0, 0, 0)),
                table(101, 40, 136, [240, 100, 140], rows, [34] + [44] * 5, sz=14, aligns=['l', 'ctr', 'ctr']),
                note(102, 548, 136, 372, 254, ['데이터를 만들 때 쓴 실제 분포로 구간을 낸 기준 모형',
                                                '군집: 그날의 변동성을 아는 정규분포', '꼬리: 분산을 맞춘 t분포', '국면 전환: 어제 국면을 아는 혼합정규분포',
                                                [('이 모형이 80%를 맞추므로 데이터 생성과 평가 코드가 맞게 짝지어져 있음', 14, True, NAVY)]], title='오라클 모형')])
    S[1] = s
    # B2 시나리오별 커버리지
    s = appx(prs, fr, 2, '합성 데이터 시나리오별 커버리지', '17개 시나리오 전체에서도 커버리지는 특성(행)보다 모델·입력 조건(열)에 따라 달라졌다', '본문 4.2절, 표 4-1, 그림 4-1')
    add_xml(s, [shape(100, 40, 102, 600, 22, [para([('■ 남색 테두리: L1(특성 없음)    ', 12.5, True, NAVY), ('■ 빨간 테두리: TimesFM-2.5 1년·가격', 12.5, True, 'C0392B')])], ins=(0, 0, 0, 0))])
    pic(s, pics['heat'], 40, 128, 600, None)
    add_xml(s, [note(101, 660, 128, 260, 360, ['색은 행(특성 강도)보다 열(모델·입력 조건)에 따라 달라짐',
                                                'Chronos-T5 가격 입력(74~78%)과 TimesFM-2.5 1년·가격(87~88%)은 어느 시나리오에서도 이 범위를 벗어나지 않음',
                                                '이 표의 커버리지를 모델·조건과 특성으로 나눈 것이 본편 11쪽(90% 대 7%)'], title='읽는 법', sz=13.5)])
    S[2] = s
    # B3 기본 설정 사례
    s = appx(prs, fr, 3, '라이브러리 기본 설정 사례', 'Chronos-T5의 기본 설정(top-k = 50)이 수익률 구간의 양 끝을 잘라 커버리지가 14~18%로 떨어졌다', '본문 3.4절, 논문 부록 A.3, 표 A-2, 표 A-3')
    BX = [('① 출력 방식', ['값을 4,096칸 눈금으로', '나눠 다음 칸을 뽑음']), ('② 기본 설정', ['확률 높은 50칸 안에서만', '뽑음 (top-k = 50)']),
          ('③ 수익률 입력', ['80% 구간에 수백 칸이', '필요한데 50칸으로 잘림']), ('④ 결과', ['구간이 지나치게 좁아짐', '(합성 L1 커버리지 14%)'])]
    f = []
    for i, (t, ls) in enumerate(BX):
        xx = 40 + i * 227
        f.append(box(100 + i, xx, 106, 199, 86, t, ls, hl=(i == 3), tsz=14, bsz=12.5))
        if i < 3:
            f.append(arrow(110 + i, xx + 204, 139))
    rows = [['Chronos-T5 수익률 입력', '기본 설정 (top-k = 50)', '제한 해제 후'], ['합성 L1 (특성 없음)', '14.0~14.7%', '76.0~78.6%'], ['실제 10종목', '16.9~17.6%', '77.8~80.0%']]
    f.append(table(120, 40, 214, [170, 170, 130], rows, [36, 44, 44], sz=14, aligns=['l', 'ctr', 'ctr']))
    f.append(bullets(121, 530, 214, 390, 270, ['가격 입력은 하루 변동이 가격 수준에 비해 작아 몇 칸 안에 들어가므로 영향이 없었음(차이 0.01%p)',
                                                  '점검 중 발견해 이 설정만 해제(top-k = 4,096)하고 같은 과제·시드·평가 코드로 다시 계산함. 해제 전 결과도 논문 부록 A.3에 실음',
                                                  '실제 주가에서 낮았던 커버리지(17~18%)가 특성 없는 합성 L1에서도 비슷하게(14~15%) 나타남']))
    add_xml(s, f)
    S[3] = s
    # B4 종목별 커버리지
    s = appx(prs, fr, 4, '종목별 커버리지', '미국 5종목과 한국 5종목의 커버리지 차이는 모든 TSFM 조건에서 2%p 이내였다', '본문 5.1절, 논문 부록 C, 표 C-1, 표 C-2')
    hdr = ['모델 · 대표 조건', 'AAPL', 'AMZN', 'GOOG', 'JPM', 'META', '삼성전자', 'SK하이닉스', '현대차', '한국전력', '현대모비스']
    data = [['Chronos-T5 1년·수익률', '79.1', '81.7', '80.4', '79.8', '79.4', '80.0', '78.7', '80.0', '81.2', '79.2'],
            ['Chronos-2 1년·수익률', '78.0', '80.1', '79.6', '78.8', '79.2', '79.4', '78.9', '79.3', '79.4', '78.7'],
            ['TimesFM-2.5 1년·수익률', '75.6', '77.5', '77.1', '76.3', '75.4', '79.2', '79.3', '77.5', '76.8', '77.9'],
            [[[('TimesFM-2.5 1년·가격', 12, True, 'C0392B')]], '86.2', '88.4', '87.3', '87.3', '86.0', '87.6', '87.2', '89.1', '89.2', '88.6'],
            ['Moirai-2 1년·수익률', '78.6', '81.1', '80.9', '79.7', '80.2', '80.3', '79.7', '79.4', '79.5', '79.1'],
            ['RW 1년', '83.6', '84.6', '84.1', '84.4', '85.7', '81.1', '79.9', '81.8', '83.2', '81.7'],
            ['GARCH-t 1년', '78.7', '79.2', '79.1', '77.4', '78.5', '79.1', '78.1', '78.2', '78.7', '77.3']]
    add_xml(s, [table(100, 40, 108, [154] + [68] * 5 + [72, 88, 66, 72, 78], [hdr] + data, [34] + [36] * 7, sz=12, aligns=['l'] + ['ctr'] * 10),
                bullets(101, 40, 404, 880, 90, ['같은 TSFM 조건에서 두 시장의 커버리지 차이는 모두 2%p 이내, 종목별 범위도 대부분 4%p 폭 안에 들어옴(표 5-1, 표 C-1·C-2)',
                                                 'TimesFM-2.5 1년·가격의 과대(구간이 넓음, 86.0~89.2%)는 10종목 모두에서 나타남. 커버리지가 달라지는 정도의 92%는 모델·조건, 1%는 종목으로 설명됨'], sz=13)])
    S[4] = s
    # B5 공개 이후 기간
    s = appx(prs, fr, 5, '모델 공개 이후 기간 점검', '학습 데이터에 들어갈 수 없는 모델 공개 이후 기간만 따로 봐도 결과는 같은 방향이었다', '본문 5.3절, 표 5-3')
    hdr = ['모델', '대표 조건', '공개 후 시작일', '예측 수', '커버리지 (전체 → 공개 후)', 'RW 대비 개선 (전체 → 공개 후)']
    data = [['Chronos-T5', '한 달·수익률', '2024-04-01', '4,291', '77.8% → 76.8%', '−1.7% → −1.9%'], ['Chronos-T5', '1년·수익률', '2024-04-01', '4,291', '80.0% → 77.5%', '+0.1% → −0.5%'],
            ['Chronos-2', '한 달·수익률', '2025-11-01', '1,295', '81.8% → 82.2%', '−7.3% → −7.1%'], ['Chronos-2', '1년·수익률', '2025-11-01', '1,295', '79.1% → 78.3%', '+0.9% → +0.2%'],
            ['TimesFM-2.5', '1년·수익률', '2025-10-01', '1,478', '77.2% → 71.8%', '−0.1% → −0.8%'], ['TimesFM-2.5', '1년·가격', '2025-10-01', '1,478', '87.7% → 84.0%', '−3.7% → −6.6%'],
            ['Moirai-2', '1년·수익률', '2025-09-01', '1,678', '79.8% → 76.0%', '+0.3% → 0.0%'], ['Moirai-2', '1년·가격', '2025-09-01', '1,678', '82.1% → 80.8%', '−2.2% → −2.5%']]
    add_xml(s, [table(100, 40, 106, [120, 120, 130, 90, 200, 220], [hdr] + data, [32] + [29] * 8, sz=12.5, aligns=['l', 'l', 'ctr', 'ctr', 'ctr', 'ctr']),
                bullets(101, 40, 380, 880, 116, ['공개 이후에도 TimesFM-2.5 1년·가격의 과대(84.0%)가 그대로였고, RW보다 손실이 큰 결과도 같았음',
                                                  '1년·수익률 조건의 커버리지는 공개 후 2.5~5.4%p(Chronos-2는 0.8%p) 낮아졌지만, 학습 데이터와 관계없는 RW 1년(83.0% → 79.2~81.3%)과 GARCH-t(78.4% → 74.8~76.6%)도 같은 기간 1.8~3.8%p 낮아져 하락의 대부분은 그 기간의 시장 상황 때문으로 보임',
                                                  'TSFM이 0.7~2.0%p 더 떨어져 학습 데이터 중복의 영향이 일부 있을 수 있으나, 기간이 1~2.5년으로 짧아 가려내기 어려움'], sz=12.5)])
    S[5] = s
    # B6 일괄 확대 대조군
    s = appx(prs, fr, 6, '일괄 확대 대조군 비교', '결과를 본 뒤 정한 배율로 넓히면 같은 폭에서 커버리지가 더 높지만, 그 배율은 실제 운용에서 미리 알 수 없다', '본문 3.5.2절, 6.4절, 표 6-1, 표 6-2')
    rows = [['비교 항목', '일괄 확대 대조군', 'ACI-CQR'],
            [[[('조정 방식', 14, True, NAVY)]], '보정 후 구간과 평균 폭이 같아지도록, 결과를 본 뒤 정한 배율을 원래 구간에 곱함', '전날까지의 이탈 기록만으로 매일 구간 양 끝을 넓히거나 좁힘'],
            [[[('같은 평균 폭일 때의 커버리지', 14, True, NAVY)]], '합성 81~86% · 실제 82~83%', '합성 79.8~80.7% · 실제 79.9~80.3% (매일 폭을 바꾸는 과정에서 일부 폭이 커버리지에 기여하지 못함)'],
            [[[('실제 운용에서 쓸 수 있는가', 14, True, NAVY)]], '필요한 배율을 미리 알 수 없음. 모델·조건에 따라 0.8~1.3배(기본 설정 Chronos-T5는 8~9배)', '쓸 수 있음. 배율을 몰라도 모든 TSFM 출력 뒤에 붙여 평균 80% 복원']]
    add_xml(s, [table(100, 40, 110, [200, 340, 340], rows, [34, 70, 70, 70], sz=13.5, aligns=['l', 'l', 'l']),
                bullets(101, 40, 400, 880, 80, ['넓혀야 할지 좁혀야 할지도 모델·조건마다 다름(TimesFM-2.5 1년·가격은 0.83배로 좁혀야 함)', '대조군과의 폭 효율 차이를 줄이는 것은 향후 과제'], sz=13.5)])
    S[6] = s
    # B7 변동성 수준별
    s = appx(prs, fr, 7, '변동성 수준별 커버리지', '보정 후 평온한 달과 변동이 큰 달의 커버리지 차이는 10.1%p에서 2.9%p로 줄었지만, 1년 조건은 변동이 큰 달에 76~79%로 남았다', '본문 6.6절, 표 6-4, 표 5-6')
    pic(s, pics['regime'], 40, 104, 450, None)
    rows = [['구분 (보정 후)', '평온한 달', '변동이 큰 달'], ['TSFM 한 달', '80.3~81.4%', '79.3~80.5%'], ['TSFM 1년', '82.0~83.2%', [[('77.5~78.9%', 13.5, True, 'C0392B')]]],
            ['RW 1년', '83.6%', [[('76.5%', 13.5, True, 'C0392B')]]], ['GARCH-t 1년', '82.7%', [[('78.6%', 13.5, True, 'C0392B')]]]]
    add_xml(s, [shape(100, 510, 106, 410, 52, [para(('평온한 달과 변동이 큰 달의 차이: 10.1%p → 2.9%p', 14.5, True, NAVY), 'ctr'), para(('(19개 모델·조건 평균, 보정 전 최대 22.8%p)', 12.5, False, MUTED), 'ctr')],
                      'roundRect', FILL, '94A3B8', 0.8, 'ctr', (8, 4, 8, 4)),
                table(101, 510, 168, [150, 130, 130], rows, [32, 34, 34, 34, 34], sz=13.5, aligns=['l', 'ctr', 'ctr']),
                bullets(102, 510, 350, 410, 140, ['80% 복원은 전체 기간 평균 기준이라 변동이 큰 달마다 80%를 맞추지는 않음',
                                                   '한 달·가격 조건은 보정 후에도 위반이 몰리는 날이 남음(독립성 검정 통과 0~3종목). 이 검정은 전날과의 관계만 봐서 여러 날 몰림은 잘 잡지 못함',
                                                   '평온한 달 = 종목·월별 변동성 하위 20%, 변동이 큰 달 = 상위 20%'], sz=12.5)])
    S[7] = s
    # B8 추가 민감도
    s = appx(prs, fr, 8, '추가 민감도 점검', '보정 속도와 GARCH-t 이상값은 결론을 바꾸지 않았고, 거래량을 넣어도 RW보다 정확해지지 않았다', '본문 5.2절, 6.2절, 6.5절, 표 6-3, 논문 부록 A.4')
    C = [('① 보정 속도 γ (실제 19개 조건) → 16쪽', ['γ = 0.005, 0.01, 0.02, 0.05(본문), 0.1 모두 19개 조건이 판정 범위(77~83%) 안, 보정 후 79.8~80.9%',
                                                 '폭 배율(보정 후 폭 ÷ 보정 전 폭)은 γ가 커질수록 0.84~1.19배 → 0.90~1.27배로 조금 커짐']),
         ('② 거래량 입력 (Chronos-2) → 14쪽', ['종가와 함께 로그 거래량을 넣어 분포 정확도가 나아지는지 확인',
                                              'RW 대비 개선율: 1년·수익률 +1.03% → +0.98%(유의하지 않음), 한 달·수익률 −7.30% → −6.35%로 여전히 RW보다 손실이 큼 (예측 24,132건 기준)']),
         ('③ TimesFM-2.5 1년·가격 과대 원인 → 10쪽', ['입력 정규화를 끄거나, 마지막 값 기준으로 크기를 바꾸거나, 로그 가격을 넣어도 합성 L1 87.4~87.7%로 같음',
                                                     '연속 분위수 헤드를 끄면 87.6% → 83.4%(4.2%p 감소). 나머지 원인은 밝히지 못함']),
         ('④ GARCH-t 이상값 2건 → 16쪽', ['합성 136,000건 중 2건에서 추정이 잘못돼 구간 폭이 극단적으로 커짐(사전에 정한 대체 규칙에 걸리지 않음)',
                                          '이 2건을 RW 1년으로 바꾸면 커버리지는 79.31%로 같고 평균 폭은 17,318%p → 4.87%p. 가설 판정은 바뀌지 않음'])]
    add_xml(s, [card(100 + i, 40 + (i % 2) * 445, 106 + (i // 2) * 196, 435, 186, t, ls) for i, (t, ls) in enumerate(C)])
    S[8] = s
    # B9 투자 규칙
    s = appx(prs, fr, 9, '투자 규칙 적용 (탐색 분석)', 'TSFM 구간의 중앙값으로 사고팔면 계속 보유보다 수익이 낮았고, 투자 비중 조절 효과는 RW 구간과 같았다', '본문 5.5.1~5.5.2절, 표 5-4, 표 5-5, 그림 5-4')
    pic(s, pics['econ'], 120, 104, 720, None)
    add_xml(s, [card(100, 40, 372, 435, 124, '① 방향 예측 매매 (중앙값 > 0이면 보유)', ['거래비용을 넣으면 모든 TSFM(연 −1.0~16.4%)이 계속 보유(연 25.4%)보다 낮음',
                                                                                 '방향 적중률 49.3~51.6%, 잦은 매매로 비용 누적 → 방향 예측에는 쓸 수 없음'], sz=12.5),
                card(101, 485, 372, 435, 124, '② 투자 비중 조절 (하루 변동 1% 목표)', ['보정 구간으로 조절하면 실제 변동이 목표의 1.05~1.14배로 가까워짐',
                                                                                '최대 낙폭 축소(−33.5% → −17~−25%)는 RW 구간으로도 같음'], sz=12.5)])
    S[9] = s
    # B10 가설 판정
    s = appx(prs, fr, 10, '가설 판정 요약', 'H6은 모든 조건에서, H4는 16개 중 10개, H1은 일부 조건에서 지지되었고, H2·H3a는 반대 방향, H3b·H5는 지지되지 않았다', '본문 7.1절, 표 7-1')
    G, Rd, O = '2E7D32', 'C0392B', 'D9480F'

    def j(t, c):
        return [[(t, 13, True, c)]]
    rows = [['질문', '가설', '판정', '핵심 발견'],
            ['RQ1', 'H1 군집 → 하락', j('일부 지지', O), '2개 조건에서 2%p 이상 하락(−2.0~−2.5%p). 커버리지를 낮춘 특성은 군집뿐'],
            ['RQ1', 'H2 꼬리 → 하락', j('지지 안 됨 (반대)', Rd), '11개 조건에서 유의한 상승. 꼬리가 두꺼운 분포의 모양 때문(98% 구간에서는 하락)'],
            ['RQ1', 'H3a 전환 빈도 → 하락', j('지지 안 됨 (반대)', Rd), '7개 조건에서 작은 상승. 국면이 섞이면 전체 분포의 꼬리가 두꺼워짐'],
            ['RQ1', 'H3b 전환 크기 → 하락', j('지지 안 됨', Rd), '유의한 변화 없음'],
            ['RQ1', 'H4 특성마다 다름', j('16개 중 10개 지지', G), '10개 모두 군집이 가장 불리'],
            ['RQ2', 'H5 TSFM이 RW보다 정확', j('지지 안 됨', Rd), '12개는 RW보다 손실 큼, 3개 차이 없음, 1개는 손실이 작았으나 차이가 2% 미만. 1년 조건 모두 GARCH-t보다 손실 큼'],
            ['RQ3', 'H6 보정 후 80% 복원', j('지지', G), '합성 323개·실제 19개 모두 판정 범위(77~83%) 안, 보정 후 평균 79.8~80.7%. 위반 몰림은 일부 조건에 남음']]
    add_xml(s, [table(100, 40, 108, [60, 200, 150, 470], rows, [34] + [50] * 7, sz=13, aligns=['ctr', 'l', 'ctr', 'l'])])
    S[10] = s
    # B11~B13 질의 대비
    Q = {11: ('질의 대비 ① "원인 진단"은 무엇을 검정했는가', '직접 검정한 것은 특성의 효과이고, 모델·설정의 영향은 L1 결과와 분산 분해로 보였다', '본문 3.6.2절, 4.2절, 4.4절, 5.4절',
              [('① 직접 검정한 것: 특성의 효과(H1~H4)', ['같은 난수에서 특성 하나만 L1 → L5로 바꿨을 때 커버리지가 떨어지는지 검정(Wilcoxon, Holm 다중비교 보정)',
                                                    '군집만 일부 조건에서 하락, 꼬리·전환 빈도는 반대(상승), 전환 크기는 변화 없음']),
               ('② 모델·설정 쪽 근거: 기술통계', ['특성이 없는 L1에서 이미 16개 중 8개가 78~82%를 벗어남',
                                             '커버리지 차이를 나눠 보면 90%는 모델·조건, 7%는 시나리오(TimesFM 1년·가격을 빼도 76% 대 18%)']),
               ('③ 기준을 바꿔도 같은가', ['±3%p로 넓히면 벗어난 조건은 5개(Chronos-T5 3개, TimesFM 1년·가격, Moirai-2 한 달·수익률)',
                                       '한 달 조건(Chronos-2 제외)은 21일 표본 정규분포의 이론값 77.5%와 비슷하거나 조금 낮음. 목표는 80% 유지(t분포 구간은 21일로도 80%)']),
               ('④ 결론의 범위', ['결론은 "본 실험 범위(16개 조건, 17개 시나리오, 80% 구간, 10종목)에서 커버리지는 모델·설정에 따라 더 크게 달라졌다"까지이며, 원인을 증명했다고 주장하지 않음',
                               '합성과 실제가 가까운 것(평균 1.1%p)은 크게 벗어나는 설정을 미리 가려내는 데 쓰고, 작은 차이(p = 0.07)까지 맞힌다고 주장하지 않음'])]),
         12: ('질의 대비 ② 꼬리 가설(H2)을 왜 "하락"으로 세웠는가', '기존 관점을 그대로 가설로 세웠고, 결과가 반대로 나온 이유는 분포 모양의 이론 계산으로 설명된다', '본문 2.1.2절, 3.6.2절, 4.3.2절, 표 4-3, 표 4-4',
              [('① 가설을 세운 이유', ['H1~H3b는 "금융 특성은 예측 모델에 불리하다"는 선행연구(FinStressTS 등)의 관점을 그대로 가설로 둔 것',
                                    '이 관점이 사전학습 TSFM의 80% 예측구간에도 성립하는지 확인하는 것이 RQ1의 목적']),
               ('② 이론: 분산이 같으면 구간 수준에 따라 방향이 반대', ['꼬리가 두꺼우면 값이 평균 근처에 더 모여 정규분포 기준 80% 구간은 86.6%로 상승',
                                                         '꼬리 쪽 극단값의 영향이 커져 99% 구간은 97.8%로 하락(초과 1% → 2.2%)']),
               ('③ 관측: TSFM에서도 같은 방향', ['80% 구간: 16개 조건 중 11개에서 유의한 상승(6개는 2%p 이상), 하락은 0개',
                                              '98% 구간(Chronos-2): 꼬리 3/4 조건, 국면 전환 8/8 조건에서 0.6~1.0%p 하락. 90% 구간은 조건마다 다름']),
               ('④ 기여의 성격', ['알려진 이론 계산을 TSFM 예측구간에 적용해 확인한 것(새 이론을 제시하지는 않음)',
                               '실무 함의: 80% 구간 하나의 커버리지만 보고 꼬리 위험(극단 손실)을 판단하면 잘못된 결론에 이를 수 있음'])]),
         13: ('질의 대비 ③ 사후보정의 의미와 Chronos-T5 재실행', '평균 80% 복원 자체보다 그 대가(구간 폭 증가)와 남은 한계가 핵심이다', '본문 3.4절, 3.5절, 6.3~6.6절, 논문 부록 A.2~A.3',
              [('① ACI는 원래 평균을 맞추게 설계된 방법인데?', ['맞음. 평균 80% 복원(H6) 자체보다 그 대가와 한계가 핵심',
                                                        '대가: 이상적인 구간보다 폭 5~48% 증가. 한계: 평온한 달과 변동이 큰 달의 차이는 10.1 → 2.9%p로 줄었지만 1년 조건은 변동이 큰 달에 76~79%, 한 달·가격은 위반이 몰리는 날이 남음(B7)']),
               ('② 현실에서 쓸 수 있는 대조군은?', ['결과를 본 뒤 정한 배율로 넓히면 폭 효율은 더 좋지만, 필요한 배율(0.8~1.3배)은 미리 알 수 없음(B6)',
                                                '준비 20일만으로 정한 고정 배율 대조군과의 비교는 향후 과제']),
               ('③ Chronos-T5만 다시 돌린 이유', ['라이브러리 기본값 top-k = 50이 수익률 입력의 분포 양 끝을 잘라 커버리지 14~18%(샘플링 설정이 모델의 예측 분포 양 끝을 잘라 낸 것)',
                                               '같은 과제·시드·평가 코드로 이 설정만 해제해 다시 계산, 해제 전 결과도 논문 부록 A.3에 함께 실음. 다른 모델의 가설 판정은 바뀌지 않음']),
               ('④ TimesFM 출력 헤드는 왜 그대로 두었나', ['라이브러리가 제공하는 두 출력 방식 가운데 권장 방식',
                                                      '출력 헤드는 일부 원인(끄면 4.2%p 감소), 나머지는 밝히지 못함. 권장 방식이라 본 실험에서는 그대로 둠'])])}
    for b, (t, m, ft, cs) in Q.items():
        s = appx(prs, fr, b, t, m, ft)
        add_xml(s, [card(100 + i, 40 + (i % 2) * 445, 106 + (i // 2) * 196, 435, 186, tt, ls) for i, (tt, ls) in enumerate(cs)])
        S[b] = s
    return S


# ---------- 17쪽 ----------
def rebuild17(s):
    for sh in list(s.shapes):
        if sh.name in ('v12 table 100', 'v12 101'):
            sh._element.getparent().remove(sh._element)
    pic(s, f'{V12}/p17_VaR.png', 40, 102, 640, None)
    add_xml(s, [note(100, 696, 112, 224, 376, ['빈 점 → 찬 점: 보정 전 → 후 위반율, 세로선 = 목표 10%',
                                                '오른쪽 숫자: 10종목 중 위반율 검정을 통과한 종목 수, 굵게 = 8종목 이상',
                                                [('이미 10% 근처이던 Chronos-T5·TimesFM-2.5 한 달·가격은 보정 후 8.6~9.0%로 낮아져 통과 종목이 줄었음(5.5.3절)', 13, False, ORANGE)],
                                                [('위반율 검정 = Kupiec 검정. 투자 규칙에 적용한 탐색 분석', 12, False, MUTED)]], title='읽는 법', sz=13)])


def main(src, out):
    prs = Presentation(src)
    O = list(prs.slides)
    fr = O[2]
    # 옛 부록 그림 꺼내기 (v12 순서: 22 히트맵, 26 변동성, 27 투자 규칙)
    pics = {}
    for key, idx in (('heat', 21), ('regime', 25), ('econ', 26)):
        ph = next(sh for sh in O[idx].shapes if sh.shape_type == 13)
        path = os.path.join(TMP, f'{key}.{ph.image.ext}'); open(path, 'wb').write(ph.image.blob); pics[key] = path
    S = build_appx(prs, fr, pics)
    rebuild17(O[16])
    # 순서: 본편 21장 + 새 부록
    order = O[:21] + [S[b] for b in range(1, 14)]
    lst = prs.slides._sldIdLst
    elmap = {int(el.get('id')): el for el in lst}
    keep = [elmap[sl.slide_id] for sl in order]
    drop = [el for el in lst if el not in keep]
    for el in list(lst):
        lst.remove(el)
    for el in keep:
        lst.append(el)
    for el in drop:
        prs.part.drop_rel(el.get(f'{{{R}}}id'))
    # 진행 표시줄과 본편 바닥글 링크
    FOOT_REF = {}
    for pg in range(3, 21):
        sl = order[pg - 1]
        nav(sl, NAV_OF[pg])
        cur = by_name(sl, 'TextBox 5').text_frame.text
        ref = re.sub(r'^.*?\|\s*', '', cur, count=1).split('  |  자세히')[0].strip()
        pieces = [(ref, None)]
        if pg in LINKS:
            pieces.append(('   |   자세히 → ', None))
            for k, b in enumerate(LINKS[pg]):
                if k:
                    pieces.append((' · ', None))
                pieces.append((f'B{b} {SHORT[b]}({bpage(b)}쪽)', bpage(b)))
        set_footer(sl, pieces, order)
    # 부록 바닥글: 본편 쪽 링크 + 보던 장으로
    for b in range(1, 14):
        sl = order[bpage(b) - 1]
        cur = by_name(sl, 'TextBox 5').text_frame.text
        ref = re.sub(r'^.*?\|\s*', '', cur, count=1).strip()
        pieces = [(ref, None)]
        if b in BACKREF:
            pieces.append(('   |   ← 본편 ', None))
            for k, pg in enumerate(BACKREF[b]):
                if k:
                    pieces.append((' · ', None))
                pieces.append((f'{pg}쪽', pg))
        set_footer(sl, pieces, order)
        tb = by_name(sl, 'TextBox 5'); tb.left = Pt(140); tb.width = Pt(690)
        back_button(sl)
    # 질의응답 장 안내 문장
    qa = order[20]
    set_text(by_name(qa, 'TextBox 4'), '부록 B1~B13: 생성 검증 · 시나리오별 커버리지 · 기본 설정 사례 · 종목별 · 공개 이후 기간 · 대조군 · 변동성 수준별 · 민감도 · 투자 규칙 · 가설 판정 · 질의 대비 3장')
    # 테마 링크색 남색
    for master in prs.slide_masters:
        tp = [rel.target_part for rel in master.part.rels.values() if rel.reltype == RT.THEME][0]
        x = tp.blob.decode('utf-8')
        x = re.sub(r'<a:hlink><a:srgbClr val="[0-9A-Fa-f]{6}"/></a:hlink>', '<a:hlink><a:srgbClr val="1B365D"/></a:hlink>', x)
        x = re.sub(r'<a:folHlink><a:srgbClr val="[0-9A-Fa-f]{6}"/></a:folHlink>', '<a:folHlink><a:srgbClr val="1B365D"/></a:folHlink>', x)
        tp._blob = x.encode('utf-8')
    prs.save(out)
    print('slides', len(order), 'dropped', len(drop))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
