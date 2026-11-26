"""발표 v15: 사용자가 PowerPoint로 고친 v14(11쪽 메시지) 위에 196차 수정을 적용한다.
3쪽 '아래 끝' → '하단' 통일, 7쪽 오라클 정의, 11쪽 그림 이름표, 12·13·16·17쪽 메시지, 17쪽 읽는 법, 18쪽 아래 상자, 19쪽 C2, 20쪽 카드 재구성.
사용: python3 deck_v15.py <PC의 v14.pptx> <out_v15.pptx>
"""
import sys, os, copy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import deck_v12 as D
from deck_v12 import shape, para, add_xml, set_text, by_name, note, pic, NAVY, BODY, MUTED, ORANGE, FILL, V12
from deck_v14 import drop, replace_runs
from pptx import Presentation
from pptx.util import Pt


def set_paras(shp, lines):
    """도형의 단락 수를 유지하며 단락별 글자만 바꾼다(첫 run 서식 유지)."""
    ps = shp.text_frame.paragraphs
    for p, t in zip(ps, lines):
        if p.runs:
            p.runs[0].text = t
            for r in p.runs[1:]:
                r._r.getparent().remove(r._r)


def main(src, out):
    prs = Presentation(src)
    S = list(prs.slides)
    # 3쪽
    s = S[2]
    set_text(by_name(s, 'v12 9'), 'TSFM이 낸 80% 예측구간의 하단은 VaR 10%로 쓰이므로, 실제값이 구간에 80% 들어오는지(커버리지)가 중요하다')
    set_paras(by_name(s, 'v12 104'), ['VaR 10%', '구간의 하단', '(손실이 더 클 확률 10%)'])
    replace_runs(s, [('아래 끝', '하단')])
    # 7쪽: 오라클 정의
    s = S[6]
    n = by_name(s, 'v12 121'); n.top = Pt(428); n.height = Pt(66)
    p0 = n.text_frame.paragraphs[0]._p
    p1 = copy.deepcopy(p0)
    r = p1.findall('{%s}r' % D.NS['a'])
    r[0].find('{%s}t' % D.NS['a']).text = '오라클 모형: 데이터를 만든 실제 분포로 낸 구간(정답 구간). 생성 검증과 구간 폭 비교의 기준'
    p0.addnext(p1)
    # 11쪽: 그림 교체(이름표)
    s = S[10]
    old = next(sh for sh in s.shapes if sh.shape_type == 13)
    x, y, w = old.left, old.top, old.width
    old._element.getparent().remove(old._element)
    s.shapes.add_picture(f'{V12}/p11_분해.png', x, y, w, None)
    # 12쪽
    s = S[11]
    set_text(by_name(s, 'v12 9'), '미국은 선행연구의 5종목을 그대로 쓰고, 한국은 같은 시점(2017년 초)의 시가총액 상위 5종목을 골랐다')
    replace_runs(s, [('평가 시작일(2017-01-02) KOSPI 보통주 시가총액 순. ', '평가 시작일(2017-01-02) KOSPI 보통주 시가총액 순(거래 이력 1년 이상, 우선주 제외). ')])
    # 13쪽
    set_text(by_name(S[12], 'v12 9'), '실제 10종목의 커버리지는 합성 L1과 평균 1.1%p 달랐고, 명목 커버리지에서 크게 벗어난 두 설정은 합성 데이터에서도 같은 값이 나왔다')
    # 16쪽
    set_text(by_name(S[15], 'v12 9'), '합성·실제 모든 모델·조건에서 평균 커버리지가 80%로 돌아왔지만, 보정 후 구간은 정답 구간(오라클)보다 5~48% 넓었다(합성 데이터)')
    m = by_name(S[15], 'v12 9'); m.top = Pt(66); m.height = Pt(40)
    for r in m.text_frame.paragraphs[0].runs:
        r.font.size = Pt(14)
    replace_runs(S[15], [('오라클 = 데이터를 만든 실제 분포로 낸 구간(80%를 맞추는 가장 좁은 구간)', '오라클 = 데이터를 만든 실제 분포로 낸 정답 구간')])
    fg = next(sh for sh in S[15].shapes if sh.shape_type == 13)
    fg.top = Pt(112); fg.height = Pt(345); fg.width = Pt(575)
    # 17쪽
    s = S[16]
    set_text(by_name(s, 'v12 9'), '보정 후 VaR 10% 검정을 통과한 조건이 8개에서 14개로 늘었다')
    drop(s, {'v12 100'})
    add_xml(s, [note(100, 696, 112, 224, 376, ['통과 = 10종목 중 8종목 이상에서 위반율 검정 통과 (VaR 10% = 80% 예측구간의 하단)',
                                                '빈 점 → 찬 점: 보정 전 → 후 위반율, 세로선 = 목표 10%',
                                                '오른쪽 숫자: 통과 종목 수, 굵게 = 8종목 이상',
                                                [('이미 10% 근처이던 Chronos-T5·TimesFM-2.5 한 달·가격은 보정 후 8.6~9.0%로 낮아져 통과 종목이 줄었음(5.5.3절)', 13, False, ORANGE)],
                                                [('위반율 검정 = Kupiec 검정. 투자 규칙에 적용한 탐색 분석', 12, False, MUTED)]], title='읽는 법', sz=13)])
    # 18쪽
    s = S[17]
    drop(s, {'v12 120'})
    add_xml(s, [shape(120, 40, 390, 880, 90, [para([('모델의 출력만 쓰는 절차', 14.5, True, NAVY)], aft=3),
                                              para(('이 절차는 모델이 낸 분위수만 쓰므로 내부 구조를 알 수 없는 사전학습 모델에도 그대로 적용할 수 있고, 금융기관의 모형 도입 전 검증과 VaR 사후 점검에 그대로 넣을 수 있다.', 14, False, BODY))],
                      'roundRect', FILL, '94A3B8', 0.8, 'ctr', (12, 6, 12, 6))])
    # 19쪽 C2
    set_paras(by_name(S[18], 'v12 131'), ['C2 평가 관점', '꼬리 위험은 구간 수준별로 커버리지를 봐야 판단할 수 있음 (80%에서는 오르고 98~99%에서는 내려감)'])
    # 20쪽
    s = S[19]
    drop(s, {'Rounded Rectangle 7', 'Rounded Rectangle 8', 'Rounded Rectangle 9', 'Rounded Rectangle 10'})
    set_text(by_name(s, 'TextBox 5'), '본문 7.3~7.4절')
    C = [('① 구간 수준', '80% 구간 중심, 98% 구간은 Chronos-2로만 확인', '극단 분위수(1% VaR 등)를 내는 모델로 확대'),
         ('② 데이터·입력', '다음 날 예측, 대형주 10종목, 종가만 입력, 미세조정 제외', 'N일 예측, 중소형주·채권·암호화폐, 거래량·거시 변수 입력'),
         ('③ 사후보정', '평균 커버리지만 맞춤. 분포 정확도는 그대로, 변동성이 큰 달의 위반 몰림과 폭 증가(5~48%)가 남음', '변동성 국면에 맞춘 보정, 폭 효율 개선')]
    f = []
    for i, (t, lim, fut) in enumerate(C):
        xx = 40 + i * 300
        f.append(shape(200 + i, xx, 116, 280, 300, [para((t, 17, True, NAVY), 'l', aft=14),
                                                    para(('한계', 13, True, ORANGE), 'l', aft=4), para((lim, 15, False, BODY), 'l', aft=18),
                                                    para(('향후 과제', 13, True, '1F6FB2'), 'l', aft=4), para((fut, 15, False, BODY), 'l')],
                       'roundRect', FILL, '94A3B8', 0.9, 't', (14, 16, 14, 12)))
    add_xml(s, f)
    # 덱 전체 '아래 끝' → '하단'
    for sl in S:
        replace_runs(sl, [('구간의 아래 끝', '구간의 하단'), ('아래 끝', '하단')])
    prs.save(out)
    print('ok')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
