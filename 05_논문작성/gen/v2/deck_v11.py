"""발표 v11: 제목을 주제형으로 짧게, 목차 맞춤, 16쪽 폭 문장, 7쪽 생성 검증 보강(강도 표 삭제).
사용: python3 deck_v11.py <풀린 v10 폴더>  (폴더 안을 직접 고친다)"""
import sys, re, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import deck_v9b as D
import slide6_flow as F
EMU = D.EMU

TITLES = {
 3: ('연구 배경 ①: TSFM 예측구간은 VaR로 바로 쓰이므로, 구간이 틀리면 위험 관리도 틀림', '연구 배경 ①: 예측구간과 위험 관리(VaR)'),
 4: ('연구 배경 ②: 명목 커버리지와 실현 커버리지, 그리고 80% 기준', '연구 배경 ②: 명목 커버리지와 실현 커버리지'),
 6: ('연구 설계 ①: TSFM 16개 조건 + 기준 모형 3개에 동일한 80일 절차 적용', '연구 설계 ①: 예측 문제와 비교 모델'),
 7: ('연구 설계 ②: 특성을 하나씩만 넣은 합성 데이터 (강도는 실제 10종목에서 잼)', '연구 설계 ②: 실측 기반 합성 데이터'),
 8: ('연구 설계 ③: 실험 전에 고정한 가설 7개(H1~H6, H3는 a·b로 구분)와 판정 기준', '연구 설계 ③: 가설과 판정 기준'),
 9: ('RQ1 ①: 금융 특성 없는 데이터(L1)에서도 커버리지 75.3~87.6%로 퍼짐', 'RQ1 진단 ①: 특성 없는 데이터(L1)'),
 10: ('RQ1 ②: 라이브러리 기본 설정(top-k=50) 하나로 커버리지 14% 급감 사례', 'RQ1 진단 ②: 라이브러리 기본 설정 사례'),
 11: ('RQ1 ③: 본 실험 범위에서 커버리지 차이의 90%는 모델·설정, 7%는 금융 특성으로 설명됨', 'RQ1 진단 ③: 커버리지 차이 나눠 보기'),
 12: ('RQ1 ④: 두꺼운 꼬리는 80% 커버리지를 높이고 극단 구간(98~99%)은 낮춤', 'RQ1 진단 ④: 두꺼운 꼬리와 구간 수준'),
 13: ('RQ2 ①: 실제 10종목 커버리지는 합성 L1과 평균 1.1%p 차이', 'RQ2 실증 평가 ①: 합성과 실제의 비교'),
 14: ('RQ2 ②: 분포 정확도(분위수 손실)는 단순 기준 모형 대비 이점 없음', 'RQ2 실증 평가 ②: 분포 정확도'),
 15: ('RQ3 ①: 모델 재학습 없이 매일 이탈 기록으로 구간 경계만 조정 (ACI-CQR)', 'RQ3 사후보정 ①: ACI-CQR의 원리'),
 16: ('RQ3 ②: ACI-CQR로 전 조건 평균 80% 복원, 구간 폭은 오라클 대비 5~48% 넓음', 'RQ3 사후보정 ②: 커버리지 복원과 구간 폭'),
 17: ('RQ3 ③ (탐색 분석): 방향 예측 매매에는 효용 없고, 위험 관리 규칙에서는 보정 후 목표에 가까워짐', 'RQ3 사후보정 ③: 투자 규칙 적용 (탐색 분석)'),
 18: ('RQ3 ④: 시기별 격차는 10.1%p → 2.9%p로 축소되었으나 고변동기 한계 잔존', 'RQ3 사후보정 ④: 시기별 커버리지'),
 19: ('결론 ①: 가설 판정 요약과 세 연구 질문의 답', '결론 ①: 가설 판정 요약'),
 20: ('결론 ②: 연구 기여(Contribution) C1~C4 종합 및 실무 도입 권고 절차', '결론 ②: 연구 기여와 실무 도입 절차'),
 21: ('결론 ③: 연구의 한계, 향후 연구 과제 및 연구 의의', '결론 ③: 한계와 향후 과제'),
 23: ('부록 A1: 모델 공개 이후 기간 분리 점검 (학습 데이터 누출 확인)', '부록 A1: 모델 공개 이후 기간 점검'),
 24: ('부록 A2: 종목별 보정 전 커버리지 (미국 5종목 · 한국 5종목)', '부록 A2: 종목별 커버리지'),
 25: ('부록 A3: 추가 민감도 점검 (γ 갱신 속도 · 거래량 공변량 · 출력 헤드 · GARCH-t)', '부록 A3: 추가 민감도 점검'),
 26: ('부록 A4: 일괄 확대 대조군과의 비교 (ACI-CQR 폭 효율과 실무적 가치)', '부록 A4: 일괄 확대 대조군 비교'),
}
TOC = [
 ('TSFM 예측구간과 금융 위험 관리(VaR)의 연결, 커버리지의 정의와 목표 80% 기준', '예측구간과 위험 관리(VaR), 명목 커버리지와 실현 커버리지'),
 ('실측 강도 기반 합성 데이터 설계, 평가 대상(19개 조건)·80일 절차, 사전 고정 가설(H1~H6)', '예측 문제와 비교 모델(19개 조건·80일 절차), 실측 기반 합성 데이터, 가설과 판정 기준'),
 ('실험 결과 — RQ1 (커버리지 차이는 어디에서 커지는가)', '실험 결과 — RQ1 진단'),
 ('특성 없는 데이터(L1) 오차, 기본 설정 14% 사례, 커버리지 차이 나눠 보기(90% 대 7%), 두꺼운 꼬리와 구간 수준', '특성 없는 데이터(L1), 라이브러리 기본 설정 사례, 커버리지 차이 나눠 보기, 두꺼운 꼬리와 구간 수준'),
 ('실험 결과 — RQ2 · RQ3 (실증 및 사후보정)', '실험 결과 — RQ2 실증 평가 · RQ3 사후보정'),
 ('합성과 실제의 비교(평균 1.1%p), 분포 정확도 한계, ACI-CQR 원리·복원·투자 규칙·시기별 격차', '합성과 실제의 비교, 분포 정확도, ACI-CQR의 원리, 커버리지 복원과 구간 폭, 투자 규칙 적용, 시기별 커버리지'),
 ('가설 판정 요약, 연구 기여(C1~C4), 실무 도입 절차, 한계와 의의 (부록 A1~A7 별첨)', '가설 판정 요약, 연구 기여와 실무 도입 절차, 한계와 향후 과제 (부록 A1~A7 별첨)'),
]
S16 = [('• 원래 80%에 가까웠던 조건일수록 폭이 덜 늘어남.', '• 구간 폭은 오라클보다 5~48% 넓고, 원래 80%에 가까운 조건일수록 덜 넓어짐.')]

CHECK = [['확인 항목', '목표', '생성 결과'],
         ['하루 변동 (17개 시나리오)', '2.11%', '2.08~2.19%'],
         ['±3σ 초과일 비율 (꼬리 L5)', '1.379%', '1.386%'],
         ['변동비 (전환 크기 L5)', '3.19배', '3.21배'],
         ['격변 일수 비율 (국면 전환)', '17.6%', '16.6~17.7%'],
         ['오라클 모형 커버리지', '80%', '79.3~80.2%']]


def note_box(sid, x, y, w, h, title, body):
    r = F.run
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{sid}" name="Oracle Note {sid}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="{int(x*EMU)}" y="{int(y*EMU)}"/>'
            f'<a:ext cx="{int(w*EMU)}" cy="{int(h*EMU)}"/></a:xfrm><a:prstGeom prst="roundRect"><a:avLst><a:gd name="adj" fmla="val 8000"/></a:avLst></a:prstGeom><a:solidFill><a:srgbClr val="F4F6F9"/></a:solidFill>'
            f'<a:ln w="9525"><a:solidFill><a:srgbClr val="94A3B8"/></a:solidFill></a:ln></p:spPr><p:txBody><a:bodyPr wrap="square" lIns="90000" tIns="54000" rIns="90000" bIns="54000" anchor="ctr"/><a:lstStyle/>'
            f'<a:p><a:pPr algn="l"/>{r(title, 11.5, True, "1B365D")}{r(body, 11, False, "1E293B")}</a:p></p:txBody></p:sp>')


def slide7(x):
    x = D.remove(x, 'name:Table 8')
    x = D.remove(x, 'name:Caption 220')
    x = D.remove(x, 'name:Check Table 230')
    x = D.sub_shape(x, 'name:Caption 221', D.set_text(['④ 생성 검증 (본문 3.2.6절 표 3-4, 4.1절)'], 12.5, b=True))
    x = D.sub_shape(x, 'name:Caption 221', D.geo(40, 212, 430, 20))
    add = [F.text_xml(223, 40, 234, 430, 18, '100개 계열 전체(시나리오당 33,200일)로 목표값과 생성 결과를 비교', sz=11),
           F.table_xml(231, 40, 256, [196, 100, 134], CHECK, sz=11, hrow=24),
           note_box(232, 40, 408, 430, 92, '오라클 모형: ',
                    '데이터를 만들 때 쓴 실제 분포로 구간을 낸 기준 모형. 군집은 그날의 변동성을 아는 정규분포, 꼬리는 분산을 맞춘 t분포, '
                    '국면 전환은 어제 국면을 아는 혼합정규분포를 씀. 이 모형이 80%를 맞추므로 데이터 생성과 평가 코드가 맞게 짝지어져 있음.')]
    x = x.replace('</p:spTree>', ''.join(add) + '</p:spTree>', 1)
    # 캡션 223은 왼쪽 정렬·보통 글씨로
    x = D.sub_shape(x, 'name:Caption 223', lambda s: s.replace('algn="ctr"', 'algn="l"').replace(' b="1"', ' b="0"').replace('val="1B365D"', 'val="1E293B"'))
    return x


def main(d):
    pres = open(f'{d}/ppt/presentation.xml').read(); rels = open(f'{d}/ppt/_rels/presentation.xml.rels').read()
    rmap = dict(re.findall(r'Id="(rId\d+)"[^>]*Target="slides/(slide\d+\.xml)"', rels))
    order = [rmap[r] for r in re.findall(r'<p:sldId [^>]*r:id="(rId\d+)"', pres)]
    def edit(pos, fn):
        p = f'{d}/ppt/slides/{order[pos-1]}'; x = open(p, encoding='utf8').read(); open(p, 'w', encoding='utf8').write(fn(x))
    for pos, pair in TITLES.items():
        edit(pos, lambda x, pair=pair, pos=pos: D.rep(x, [pair], pos))
    edit(2, lambda x: D.rep(x, TOC, 2))
    edit(16, lambda x: D.rep(x, S16, 16))
    edit(16, lambda x: D.sub_shape(D.sub_shape(D.sub_shape(x, 'name:Picture 8', D.geo(209, 70, 542, 272)), 'name:Table 9', D.geo(40, 354, 378, 115)), 'name:TextBox 10', D.geo(436, 350, 482, 150)))
    edit(7, slide7)
    print('problems', D.BAD)


if __name__ == '__main__':
    main(sys.argv[1])
