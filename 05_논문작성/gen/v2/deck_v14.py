"""발표 v14: v13 위에 (1) 4쪽을 '선행연구 대비 새로운 점'(Novelty N1~N3)으로, (2) 5쪽 연구 질문 표에 '이어지는 기여' 칸,
(3) 부록 B7 그림 위쪽 제목·범례를 PowerPoint 글자로 덮어쓰고 용어를 '변동성이 적은 달/큰 달'로 통일. 결정로그 195차.
사용: python3 deck_v14.py <v13.pptx> <out_v14.pptx>
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import deck_v12 as D
from deck_v12 import shape, para, table, add_xml, set_text, by_name, NAVY, BODY, MUTED, ORANGE
from pptx import Presentation
from pptx.util import Pt


def drop(slide, names):
    for sh in list(slide.shapes):
        if sh.name in names:
            sh._element.getparent().remove(sh._element)


def replace_runs(slide, pairs):
    for sh in slide.shapes:
        frames = []
        if sh.has_text_frame:
            frames.append(sh.text_frame)
        if getattr(sh, 'has_table', False) and sh.has_table:
            frames += [c.text_frame for r in sh.table.rows for c in r.cells]
        for tf in frames:
            for p in tf.paragraphs:
                for r in p.runs:
                    t = r.text
                    for a, b in pairs:
                        t = t.replace(a, b)
                    if t != r.text:
                        r.text = t


def main(src, out):
    prs = Presentation(src)
    S = list(prs.slides)
    # ---- 4쪽: 선행연구 대비 새로운 점 ----
    s4 = S[3]
    set_text(by_name(s4, 'TextBox 2'), '선행연구 대비 새로운 점')
    set_text(by_name(s4, 'v12 9'), '기존 연구가 다루지 않은 사전학습 TSFM 금융 예측구간의 커버리지를 진단·평가·보정한다')
    drop(s4, {'v12 table 100', 'v12 101'})
    N = lambda k, t: [[(k + ' ', 14, True, ORANGE), (t, 14, True, BODY)]]
    ref = lambda t, r: [[(t, 14, True, NAVY)], [(r, 11, False, MUTED)]]
    rows = [['연구 갈래', '기존 연구가 다룬 것', '다루지 않은 것', '본 연구 (Novelty)'],
            [ref('합성 데이터 진단', 'FinStressTS(Sun 외, 2026)'), '금융 구조를 조절한 합성 데이터로 학습형 모델 진단', '사전학습 TSFM, 예측구간의 커버리지', N('N1', '실측 강도 합성 데이터로 TSFM 구간 진단')],
            [ref('금융 TSFM 평가', 'Rahimikia 외(2025), Noguer i Alonso·Franklin(2026), Upadhyay(2026)'), '금융 수익률 점 예측 정확도', '수익률 예측구간의 커버리지', N('N2', 'TSFM 예측구간의 커버리지 평가')],
            [ref('사후보정', 'CQR(Romano 외, 2019), ACI(Gibbs·Candès, 2021)'), '모델과 무관하게 커버리지를 맞추는 방법', '금융 TSFM 예측구간에 적용·검증', N('N3', '재학습 없는 보정의 효과·비용 검증')]]
    add_xml(s4, [table(100, 40, 112, [190, 230, 210, 250], rows, [36, 104, 104, 104], sz=14, aligns=['l', 'l', 'l', 'l']),
                 shape(101, 40, 470, 880, 24, [para(('N1~N3에서 각각 RQ1(진단), RQ2(실증), RQ3(사후보정)이 나온다 → 다음 쪽', 12.5, False, MUTED))], ins=(0, 0, 0, 0))])
    # ---- 5쪽: 연구 질문 + 이어지는 기여 ----
    s5 = S[4]
    drop(s5, {'v12 table 100', 'v12 101'})
    C = lambda *xs: [[(x, 13.5, False, BODY)] for x in xs]
    rows = [['연구 질문', '질문', '쓰는 데이터', '이어지는 기여'],
            [[[('RQ1 진단', 15, True, NAVY)], [('← N1', 12, False, ORANGE)]], '금융 특성(변동성 군집, 두꺼운 꼬리, 국면 전환의 빈도와 크기)이 강해질수록 TSFM 80% 예측구간의 커버리지가 떨어지는가, 아니면 모델과 입력 설정에서 이미 오차가 생기는가?', '합성 데이터',
             C('C1 방법론', 'C2 평가 관점')],
            [[[('RQ2 실증', 15, True, NAVY)], [('← N2', 12, False, ORANGE)]], '실제 미국·한국 대형주에서 TSFM 예측구간의 커버리지와 분포 정확도는 어떠하며, 단순 기준 모형(RW)보다 나은가?', '실제 10종목',
             C('C1 방법론', '(합성과 실제 비교)')],
            [[[('RQ3 사후보정', 15, True, NAVY)], [('← N3', 12, False, ORANGE)]], '모델을 재학습하지 않는 사후보정(ACI-CQR)으로 커버리지를 80%로 복원할 수 있는가? 그 대가로 구간은 얼마나 넓어지는가?', '두 데이터 모두',
             C('C4 실무', '(점검 → 보정 → 용도 제한)')]]
    add_xml(s5, [table(100, 40, 112, [140, 470, 120, 150], rows, [36, 112, 100, 100], sz=14, aligns=['ctr', 'l', 'ctr', 'ctr']),
                 shape(101, 40, 462, 880, 34, [para(('C3 실증(최신 TSFM 4종, 미국·한국 대형주, 실험 전 고정한 기준)은 세 질문 전체에서 나온다. 기여의 근거 숫자는 19쪽', 12.5, False, MUTED)),
                                               para(('RW: 과거 수익률의 평균과 표준편차로 만든 정규분포(과거변동 기준선). ACI-CQR: 적응형 콘포멀 분위수 보정', 12, False, MUTED))], ins=(0, 0, 0, 0))])
    # ---- 2쪽 목차의 4쪽 제목 ----
    replace_runs(S[1], [('금융 TSFM 연구에서 확인되지 않은 것', '선행연구 대비 새로운 점')])
    # ---- 부록 B7(28쪽): 그림 위쪽 덮기 + 용어 통일 ----
    b7 = S[27]
    pic = next(sh for sh in b7.shapes if sh.shape_type == 13)
    x, y, w = pic.left / D.EMU, pic.top / D.EMU, pic.width / D.EMU
    h_cover = w * 235 / 1872
    leg = [para([('수익률 변동성이 적은 달과 변동성이 큰 달의 커버리지', 12, True, NAVY)], 'ctr', aft=3),
           para([('보정 전 ', 10.5, True, BODY), ('○ 왼쪽 = 변동성이 큰 달, 오른쪽 = 변동성이 적은 달', 10.5, False, BODY)], 'ctr'),
           para([('보정 후 ', 10.5, True, BODY), ('● ', 10.5, True, 'B91C1C'), ('변동성이 큰 달   ', 10.5, False, BODY), ('■ ', 10.5, True, NAVY), ('변동성이 적은 달   ', 10.5, False, BODY),
                 ('옅은 띠 = 적정 범위(78~82%)', 10.5, False, MUTED)], 'ctr')]
    add_xml(b7, [shape(120, x, y, w, h_cover, leg, 'rect', 'FFFFFF', None, anchor='ctr', ins=(2, 1, 2, 1))])
    pairs = [('평온한 달과 변동이 큰 달의 차이', '변동성이 적은 달과 큰 달의 차이'), ('평온한 달', '변동성이 적은 달'), ('변동이 큰 달', '변동성이 큰 달'),
             ('변동성이 적은 달 = 종목·월별 변동성 하위 20%, 변동성이 큰 달 = 상위 20%', '변동성이 적은 달 = 종목·월별 수익률 변동성 하위 20%, 변동성이 큰 달 = 상위 20%')]
    replace_runs(b7, pairs)
    set_text(by_name(b7, 'v12 9'), '보정 후 변동성이 적은 달과 큰 달의 차이는 10.1%p에서 2.9%p로 줄었지만, 1년 조건은 변동성이 큰 달에 76~79%로 남았다')
    replace_runs(S[33], pairs)   # B13
    prs.save(out)
    print('ok')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
