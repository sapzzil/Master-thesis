"""합성 데이터 장(원래 6쪽)을 설계 흐름도로 바꾸고, 연구 설계 ①·② 순서를 논문(3.1 → 3.2)에 맞춘다.
사용: python3 slide6_flow.py <풀린 pptx 폴더>
- 원래 6쪽(합성 데이터) = 흐름도 4단계 + ② 강도 표 + ③ 예시 그림 + ④ 생성 검증 표 → '연구 설계 ②'
- 원래 7쪽(예측 문제·모델·절차·데이터) → '연구 설계 ①'로 앞으로
"""
import sys, re, os, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import deck_v9b as D
EMU = D.EMU
FIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'figs', 'slide6_합성예시.png')
NAVY, BODY, FILL = '1B365D', '1E293B', 'F4F6F9'


def run(t, sz, b, col):
    return (f'<a:r><a:rPr lang="ko-KR" sz="{int(sz*100)}" b="{1 if b else 0}"><a:solidFill><a:srgbClr val="{col}"/></a:solidFill>'
            f'<a:latin typeface="맑은 고딕"/><a:ea typeface="맑은 고딕"/></a:rPr><a:t>{t}</a:t></a:r>')


def box_xml(sid, x, y, w, h, title, lines, tsz=13, bsz=11.5):
    ps = [f'<a:p><a:pPr algn="ctr"><a:spcAft><a:spcPts val="600"/></a:spcAft></a:pPr>{run(title, tsz, True, NAVY)}</a:p>']
    ps += [f'<a:p><a:pPr algn="ctr"><a:spcBef><a:spcPts val="200"/></a:spcBef></a:pPr>{run(l, bsz, False, BODY)}</a:p>' for l in lines]
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{sid}" name="Flow Box {sid}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="{int(x*EMU)}" y="{int(y*EMU)}"/>'
            f'<a:ext cx="{int(w*EMU)}" cy="{int(h*EMU)}"/></a:xfrm><a:prstGeom prst="roundRect"><a:avLst/></a:prstGeom><a:solidFill><a:srgbClr val="{FILL}"/></a:solidFill>'
            f'<a:ln w="13970"><a:solidFill><a:srgbClr val="{NAVY}"/></a:solidFill></a:ln></p:spPr><p:txBody><a:bodyPr wrap="square" lIns="72000" rIns="72000" rtlCol="0" anchor="ctr"/><a:lstStyle/>'
            + ''.join(ps) + '</p:txBody></p:sp>')


def arrow_xml(sid, x, y):
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{sid}" name="Flow Arrow {sid}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="{int(x*EMU)}" y="{int(y*EMU)}"/>'
            f'<a:ext cx="{int(18*EMU)}" cy="{int(20*EMU)}"/></a:xfrm><a:prstGeom prst="rightArrow"><a:avLst/></a:prstGeom><a:solidFill><a:srgbClr val="{NAVY}"/></a:solidFill><a:ln><a:noFill/></a:ln></p:spPr></p:sp>')


def text_xml(sid, x, y, w, h, text, sz=12.5):
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{sid}" name="Caption {sid}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="{int(x*EMU)}" y="{int(y*EMU)}"/>'
            f'<a:ext cx="{int(w*EMU)}" cy="{int(h*EMU)}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr><p:txBody><a:bodyPr wrap="square" lIns="0" tIns="0" rIns="0" bIns="0" anchor="ctr"/><a:lstStyle/>'
            f'<a:p><a:pPr algn="ctr"/>{run(text, sz, True, NAVY)}</a:p></p:txBody></p:sp>')


def table_xml(sid, x, y, widths, rows, sz=11, hrow=26):
    def cell(t, head, alt, left):
        fill = NAVY if head else ('FFFFFF' if alt else FILL)
        col = 'FFFFFF' if head else BODY
        al = 'l' if (left and not head) else 'ctr'
        return (f'<a:tc><a:txBody><a:bodyPr wrap="square"/><a:lstStyle/><a:p><a:pPr algn="{al}"/>{run(t, sz, head, col)}</a:p></a:txBody>'
                f'<a:tcPr anchor="ctr" marL="73152" marR="73152" marT="36000" marB="36000"><a:solidFill><a:srgbClr val="{fill}"/></a:solidFill></a:tcPr></a:tc>')
    grid = ''.join(f'<a:gridCol w="{int(w*EMU)}"/>' for w in widths)
    trs = ''.join(f'<a:tr h="{int(hrow*EMU)}">' + ''.join(cell(t, i == 0, i % 2 == 0, j == 0) for j, t in enumerate(r)) + '</a:tr>' for i, r in enumerate(rows))
    W, H = sum(widths), hrow * len(rows)
    return (f'<p:graphicFrame><p:nvGraphicFramePr><p:cNvPr id="{sid}" name="Check Table {sid}"/><p:cNvGraphicFramePr><a:graphicFrameLocks noGrp="1"/></p:cNvGraphicFramePr><p:nvPr/></p:nvGraphicFramePr>'
            f'<p:xfrm><a:off x="{int(x*EMU)}" y="{int(y*EMU)}"/><a:ext cx="{int(W*EMU)}" cy="{int(H*EMU)}"/></p:xfrm><a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/table">'
            f'<a:tbl><a:tblPr firstRow="1" bandRow="1"/><a:tblGrid>{grid}</a:tblGrid>{trs}</a:tbl></a:graphicData></a:graphic></p:graphicFrame>')


BOXES = [
 ('① 실제 10종목에서 강도 측정', ['GARCH-t: 군집(α+β)·꼬리(ν)', '2국면 모형: 전환 빈도·크기', '(2017~2026, 미국 5·한국 5)']),
 ('② 강도 단계 정하기', ['L1: 특성 없음(정규분포)', 'L3: 가장 약한 종목, L4: 중앙값', 'L5: 가장 강한 종목', 'L2: L1과 L3의 중간']),
 ('③ 특성 하나씩 넣어 생성', ['같은 난수 100개 계열', '하루 변동 2.11%·평균 0 고정', 'L1 + 4개 특성 × L2~L5', '= 17개 시나리오']),
 ('④ 생성 검증', ['목표값과 생성 결과 비교', '정답 분포를 아는 오라클 모형의', '커버리지 79.3~80.2%', '→ 의도대로 생성됨']),
]
CHECK = [['확인 항목', '목표', '생성 결과'],
         ['하루 변동 (17개 시나리오)', '2.11%', '2.08~2.19%'],
         ['±3σ 초과일 비율 (꼬리 L5)', '1.379%', '1.386%'],
         ['변동비 (전환 크기 L5)', '3.19배', '3.21배'],
         ['오라클 모형 커버리지', '80%', '79.3~80.2%']]


def apply(x):
    x = D.sub_shape(x, 'name:TextBox 2', D.set_text(['연구 설계 ②: 특성을 하나씩만 넣은 합성 데이터 (강도는 실제 10종목에서 잼)'], 20, b=True))
    x = D.remove(x, 'name:TextBox 7')
    x = D.remove(x, 'name:TextBox 9')
    w, h, y0, gap = 199, 122, 76, 28
    add = []
    for i, (t, ls) in enumerate(BOXES):
        xx = 40 + i * (w + gap)
        add.append(box_xml(200 + i, xx, y0, w, h, t, ls))
        if i < 3:
            add.append(arrow_xml(210 + i, xx + w + 5, y0 + h / 2 - 10))
    # 왼쪽: ② 강도 표, ④ 생성 검증 표 / 오른쪽: ③ 예시 그림
    add.append(text_xml(220, 40, 212, 430, 20, '② 단계별 강도 (L3·L5, 본문 표 3-3)'))
    add.append(text_xml(221, 40, 340, 430, 20, '④ 생성 검증 (본문 표 3-4, 4.1절)'))
    add.append(table_xml(230, 40, 362, [196, 100, 134], CHECK, sz=11, hrow=27))
    add.append(text_xml(222, 488, 212, 430, 20, '③ 생성 예시 (같은 난수, 특성만 다름)'))
    x = x.replace('</p:spTree>', ''.join(add) + '</p:spTree>', 1)
    x = D.sub_shape(x, 'name:Table 8', D.table_rows([[None, None, '전환 빈도 (일)\n평온 / 격변 지속', None],
                                                   ['L3 0.946\nL5 0.996', 'L3 7.64\nL5 3.56', 'L3 275 / 59\nL5 9.5 / 2.0', 'L3 2.50\nL5 3.19']]))
    x = D.sub_shape(x, 'name:Table 8', D.table_rows([[None] * 4, ['L3 0.946\nL5 0.996', 'L3 7.64\nL5 3.56', 'L3 275 / 59\nL5 9.5 / 2.0', 'L3 2.50\nL5 3.19']], sz=12))
    x = D.sub_shape(x, 'name:Table 8', D.geo(40, 234, 430, 96))
    x = D.sub_shape(x, 'name:Table 8', D.heights([40, 52]))
    x = D.sub_shape(x, 'name:Picture 10', D.geo(492, 236, 422, int(422 * 960 / 1520)))
    return x


def main(d):
    pres_p = f'{d}/ppt/presentation.xml'
    pres = open(pres_p).read(); rels = open(f'{d}/ppt/_rels/presentation.xml.rels').read()
    rmap = dict(re.findall(r'Id="(rId\d+)"[^>]*Target="slides/(slide\d+\.xml)"', rels))
    ids = re.findall(r'<p:sldId [^>]*r:id="rId\d+"/>', pres)
    order = [rmap[re.search(r'r:id="(rId\d+)"', s).group(1)] for s in ids]
    f_syn, f_pred = order[5], order[6]          # 지금 6쪽(합성), 7쪽(예측 문제)
    # 합성 데이터 장
    p = f'{d}/ppt/slides/{f_syn}'
    x = apply(open(p, encoding='utf8').read())
    x = x.replace('<a:t>6 / 22</a:t>', '<a:t>7 / 22</a:t>')
    open(p, 'w', encoding='utf8').write(x)
    rel = open(f'{d}/ppt/slides/_rels/{f_syn}.rels').read()
    img = re.search(r'Target="\.\./media/([^"]+)"', rel).group(1)
    shutil.copy(FIG, f'{d}/ppt/media/{img}')
    # 예측 문제 장
    p = f'{d}/ppt/slides/{f_pred}'
    y = open(p, encoding='utf8').read()
    y = D.rep(y, [('연구 설계 ②: TSFM 16개 조건', '연구 설계 ①: TSFM 16개 조건')], 'pred')
    y = y.replace('<a:t>7 / 22</a:t>', '<a:t>6 / 22</a:t>')
    open(p, 'w', encoding='utf8').write(y)
    # 순서 바꾸기
    ids[5], ids[6] = ids[6], ids[5]
    pres = re.sub(r'<p:sldIdLst>.*?</p:sldIdLst>', '<p:sldIdLst>' + ''.join(ids) + '</p:sldIdLst>', pres, flags=re.S)
    open(pres_p, 'w').write(pres)
    print('problems', D.BAD, 'img', img)


if __name__ == '__main__':
    main(sys.argv[1])
