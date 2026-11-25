"""발표 자료 v9: v8_복원 pptx를 원고 v3(168~179차)에 맞춰 고치고, 질의 대비 부록 A5~A7을 추가한다.
사용: python3 deck_v9.py <v8_복원.pptx> <out.pptx>"""
import sys, os, re, shutil, zipfile, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pptx_phrase import replace_in_xml, ptext, PAR

E = {
 1: [('오차의 출처와 재학습 없는 사후보정', '커버리지 오차의 원인 진단과 재학습 없는 사후보정')],
 2: [('두꺼운 꼬리의 역설', '두꺼운 꼬리와 구간 수준'),
     ('실제 10종목 대응(1.1%p)', '합성과 실제의 비교(평균 1.1%p)'),
     ('부록 A1~A4 별첨', '부록 A1~A7 별첨')],
 3: [('최근 21일(1개월)', '최근 21일(한 달)')],
 4: [('를 상회하는 실질 기준.', '보다 큰 실질 기준(±3%p로 넓혀도 결론 같음, 9쪽).')],
 5: [('Rahimikia 외(2025): 94개국 R²·방향\nNoguer i Alonso·Franklin(2026):\n미국 대형주 5종목 중앙값 MAE', 'Rahimikia 외(2025): 94개국 R²·방향\nNoguer i Alonso 외(2026): 대형주\nUpadhyay(2026): 지수선물'),
     ('예측구간 커버리지 및', '수익률 예측구간 커버리지 및')],
 6: [('4축×L2~L5 = 17개 시나리오', '4개 특성×L2~L5 = 17개 시나리오, 전환 L4 두 개는 같은 데이터'),
     ('L2는 L1과 L3의 중간', 'L2는 L1과 L3의 중간, 전환 빈도 L5만 실측 최댓값의 2배'),
     ('채점 절차', '평가 절차')],
 7: [('채점 60일(모든 지표 산출)', '평가 60일(모든 지표 산출)'),
     ('80일 에피소드 채점 절차', '80일 에피소드 평가 절차'),
     ('실제값 채점 (t+1일)', '실제값 평가 (t+1일)'),
     ('× 채점 60일', '× 평가 60일'),
     ('(채점 17,700건', '(평가 17,700건'),
     ('21거래일(1개월)', '21거래일(한 달)'),
     ('과거 변동 기준선(Random Walk, RW):', '과거 변동 기준선(랜덤워크 가정, RW):'),
     ('1개월·1년 과거 평균·표준편차 기반 정규분포', '한 달·1년 과거 평균·표준편차 기반 정규분포\n   (선행연구의 수익률 0 예측과 다름)')],
 8: [('실험 전 git 커밋으로 고정한', '실험 전에 고정한'),
     ('특성을 강화했을 때 커버리지 하락 폭이 특성마다 다르다', '강한 단계(L4·L5)에서 특성마다 커버리지가 다르다'),
     ('Holm 보정 적용 후', 'Holm 다중비교 보정 후')],
 9: [('적정 범위(78~82%)를 이탈함.', '적정 범위(78~82%)를 이탈함(±3%p로 넓히면 5개).'),
     ('커버리지 수준이 결정되는 패턴이 뚜렷함.', '커버리지 수준이 달라지는 패턴이 뚜렷함.'),
     ('수준이 달라지는 패턴이 뚜렷함.', '수준이 달라지는 패턴이 뚜렷함.\n• 한 달 조건(Chronos-2 제외)은 21일 정규분포 이론값 77.5% 근처.')],
 10: [('동일 과제·시드·채점으로', '동일 과제·시드·평가 코드로')],
 11: [('커버리지 변동의 90%는 모델·설정, 7%만 금융 특성으로 설명', '본 실험 범위에서 커버리지 차이의 90%는 모델·설정, 7%는 금융 특성'),
      ('커버리지 변동 이원 분산 분해', '커버리지 변동 이원 분산 분해 (TimesFM 1년·가격을 빼도 76% 대 18%)'),
      ('실측 최강(L5)까지', '가장 강한 단계(L5, 전환 빈도만 실측의 2배)까지')],
 12: [('극단값 빈도 증가로', '꼬리 쪽 극단값의 영향이 커져'),
      ('(0.6~1.0%p) 하락.', '(0.6~1.0%p) 하락(90% 구간은 조건마다 다름).')],
 13: [('정밀 예측보다는', '작은 차이(2%p 이내)까지 맞히지는 못하므로(80% 고정 예측보다 가까운 조건 12/19, p = 0.07), 정밀 예측보다는')],
 14: [('H5 미지지', 'H5 지지 안 됨'),
      ('9개 분위수 전체 오차(분위수 손실)', '0.1~0.9 분위수 범위의 분포 오차(분위수 손실)')],
 15: [('동일하게 부착 가능.', '동일하게 부착 가능.\n· 양 끝을 함께 조정하므로 하단(VaR) 위반율만 따로 맞추지는 않음.')],
 16: [('과거 1개월 조건', '과거 한 달 조건')],
 17: [('① 방향 매매', '① 방향 예측 매매'),
      ('→ 방향 예측에는 쓸 수 없고, 위험 크기 측정에 쓰는 것이 맞음.', '→ 방향 예측에는 쓸 수 없음.'),
      ('변동성 목표 비중 조절', '목표 변동성 비중 조절'),
      ('1.05~1.14배로 목표에 수렴.', '1.05~1.14배로 목표에 수렴. 낙폭 축소는 RW 구간으로도 같음(TSFM 우위 없음).')],
 18: [('TSFM 1개월', 'TSFM 한 달'),
      ('1개월·가격 조건은', '한 달·가격 조건은'),
      ('안정적으로 통과함.', '안정적으로 통과함. 단, 독립성 검정은 전날과의 관계만 보므로 여러 날 몰림은 잘 잡지 못함.')],
 19: [('실제 적용 전 사전 점검 절차로 제시', '실제 적용 전 사전 점검 절차로 제시(크게 어긋나는 설정 선별)'),
      ('단일 구간(80%) 커버리지로 꼬리 위험을 판단할 때의 오판 가능성 제시', '꼬리 효과가 구간 수준에 따라 반대가 된다는 이론 계산을 TSFM 구간에서 확인'),
      ('24,132건 평가 ·', '예측 24,132건(평가 17,700건) ·'),
      ('3단계 · 위험 측정 용도로 한정', '3단계 · 용도와 한계 인식'),
      ('방향 예측(수익 추구)이 아닌 VaR 한도·', '방향 예측(수익 추구)에는 쓰지 않고,'),
      ('변동성 목표 비중 조절 등 위험 측정에 활용', '위험 측정도 정확도는 RW 수준임을 전제')],
 20: [('· 98% 극단 구간은 해당 분위수를 지원하는 Chronos-2 단독으로 확인.', '· 98% 극단 구간은 Chronos-2 단독으로 확인. VaR 10%도 실무(1~5%)보다 덜 극단적.'),
      ('종가 단변량 입력 범위.', '종가 단변량 입력 범위. 특성 강도는 평가 기간을 포함한 자료로 측정, 레버리지 효과 미포함.'),
      ('· 고변동기 위반 몰림과 오라클 대비 구간 폭 증가(5~48%) 과제 잔존.', '· 하단 위반율을 따로 맞추지 않으며(양 끝 함께 조정), 고변동기 위반 몰림과 구간 폭 증가(5~48%)가 남음.'),
      ('오차가 발생하는 원인을 분리 진단하고', '오차가 어디에서 커지는지 진단하고')],
 21: [('시장 변동 상황의 영향이 큼.', '시장 변동 상황의 영향이 큼(중복 영향이 일부 있을 수 있으나 기간이 짧아 가려내기 어려움).')],
 23: [('· RW 대비 손실 개선율:', '· RW 대비 손실 개선율(예측 24,132건 기준, 본문 표 5-2는 평가 17,700건 기준 +0.9%):')],
 24: [('채점 기간 평균 보정폭과 같아지도록', '평가 기간의 보정 후 구간 평균 폭과 같아지도록')],
}

# 질의 대비 부록: 부록 A3(슬라이드 23, 4칸 구성)을 복제해 글자만 바꾼다
NEW = [
 ('부록 A5: 질의 대비 ① "원인 진단"은 무엇을 검정했는가', '본문 3.6.2절, 4.2절, 4.4절, 5.4절', '부록 A5', [
   ('① 직접 검정한 것: 특성의 효과(H1~H4)',
    '· 같은 난수에서 특성 하나만 L1→L5로 바꿨을 때 커버리지가 떨어지는지 검정(Wilcoxon, Holm 다중비교 보정).\n· 군집만 일부 조건에서 하락, 꼬리·전환 빈도는 반대(상승), 전환 크기는 변화 없음.'),
   ('② 모델·설정 쪽 근거: 기술통계',
    '· 특성이 없는 L1에서 이미 16개 중 8개가 78~82%를 벗어남.\n· 분산 분해: 커버리지 차이의 90%는 모델·조건, 7%는 시나리오(TimesFM 1년·가격을 빼도 76% 대 18%).'),
   ('③ 기준을 바꿔도 같은가',
    '· ±3%p로 넓히면 벗어난 조건은 5개(Chronos-T5 3개, TimesFM 1년·가격, Moirai-2 한 달·수익률).\n· 한 달 조건(Chronos-2 제외)은 21일 표본 정규분포의 이론값 77.5%와 비슷하거나 조금 낮음. 목표는 80% 유지(t분포 구간은 21일로도 80%).'),
   ('④ 그래서 결론의 범위는',
    '· "원인을 증명했다"가 아니라 "본 실험 범위(16개 조건, 17개 시나리오, 80% 구간, 10종목)에서 모델·설정에 따라 더 크게 달라졌다".\n· 합성과 실제가 가까운 것(평균 1.1%p)은 크게 어긋나는 설정을 미리 가려내는 데 쓰고, 작은 차이(p = 0.07)까지 맞힌다고 주장하지 않음.')]),
 ('부록 A6: 질의 대비 ② 꼬리 가설(H2)을 왜 "하락"으로 세웠는가', '본문 2.1.2절, 3.6.2절, 4.3.2절, 표 4-3, 표 4-4', '부록 A6', [
   ('① 가설을 세운 이유',
    '· H1~H3b는 "금융 특성은 예측 모델에 불리하다"는 선행연구(FinStressTS 등)의 관점을 그대로 가설로 둔 것.\n· 이 관점이 사전학습 TSFM의 80% 예측구간에도 성립하는지 확인하는 것이 RQ1의 목적.'),
   ('② 이론: 분산이 같으면 구간 수준에 따라 방향이 반대',
    '· 꼬리가 두꺼우면 값이 평균 근처에 더 모여 정규 기준 80% 구간은 86.6%로 상승.\n· 꼬리 쪽 극단값의 영향이 커져 99% 구간은 97.8%로 하락(초과 1% → 2.2%).'),
   ('③ 관측: TSFM에서도 같은 방향',
    '· 80% 구간: 16개 조건 중 11개에서 유의한 상승(6개는 2%p 이상), 하락은 0개.\n· 98% 구간(Chronos-2): 꼬리 3/4 조건, 국면 전환 8/8 조건에서 0.6~1.0%p 하락. 90% 구간은 조건마다 다름.'),
   ('④ 기여의 성격',
    '· 새 이론의 발견이 아니라, 알려진 이론 계산을 TSFM 예측구간에 적용해 확인한 것.\n· 실무 함의: 80% 구간 하나의 커버리지만 보고 꼬리 위험 대응력을 판단하면 잘못된 결론에 이를 수 있음.')]),
 ('부록 A7: 질의 대비 ③ 사후보정의 의미와 Chronos-T5 재실행', '본문 3.4절, 3.5절, 6.3~6.6절, 부록 A.2~A.3', '부록 A7', [
   ('① ACI는 원래 평균을 맞추게 설계된 방법인데?',
    '· 맞음. 평균 80% 복원(H6) 자체보다 그 대가와 한계가 핵심.\n· 대가: 이상적인 구간보다 폭 5~48% 증가. 한계: 시기별 격차 10.1→2.9%p로 줄었으나 고변동기 76~79%, 한 달·가격은 위반 몰림 잔존.'),
   ('② 현실에서 쓸 수 있는 대조군은?',
    '· 결과를 본 뒤 정한 배율로 일괄 확대하면 같은 폭에서 81~86%로 폭 효율은 더 좋지만, 배율(0.8~1.3배)을 미리 알 수 없어 실무에서는 쓸 수 없음.\n· 준비 20일만으로 정한 고정 배율 대조군은 다음 판에서 비교.'),
   ('③ Chronos-T5만 다시 돌린 이유',
    '· 라이브러리 기본값 top-k = 50이 수익률 입력의 분포 양 끝을 잘라 커버리지 14~18%(모델의 예측이 아니라 샘플링 설정의 문제).\n· 같은 과제·시드·평가 코드로 이 설정만 해제해 재계산, 해제 전 결과도 부록에 병기. 다른 모델의 가설 판정은 불변.'),
   ('④ TimesFM 출력 헤드는 왜 그대로 두었나',
    '· 라이브러리가 제공하는 두 출력 방식 가운데 권장 방식.\n· 끄면 과대가 일부만 줄어(합성 87.6% → 83.4%) 이 설정이 출력을 왜곡한다고 볼 근거가 없음. 나머지 원인은 향후 연구.')]),
]

def set_para_text(p, text):
    """문단의 글자를 text 하나로 바꾼다(첫 run 서식 유지, 나머지 run 비움)."""
    import html
    ms = list(re.finditer(r'(<a:t>)([^<]*)(</a:t>)', p))
    out = []; prev = 0
    for k, m in enumerate(ms):
        out.append(p[prev:m.start()]); out.append(m.group(1) + (html.escape(text, quote=False) if k == 0 else '') + m.group(3)); prev = m.end()
    out.append(p[prev:]); return ''.join(out)

def main(src, dst):
    tmp = tempfile.mkdtemp(); z = zipfile.ZipFile(src); z.extractall(tmp)
    sl = lambda n: os.path.join(tmp, f'ppt/slides/slide{n}.xml')
    bad = 0
    for n, pairs in E.items():
        x = open(sl(n), encoding='utf8').read()
        for o, nw in pairs:
            x, k = replace_in_xml(x, o, nw)
            if k != 1: print('BAD', n, o[:40]); bad += 1
        open(sl(n), 'w', encoding='utf8').write(x)
    # 새 부록 슬라이드
    base = open(sl(23), encoding='utf8').read()
    pres = open(os.path.join(tmp, 'ppt/presentation.xml'), encoding='utf8').read()
    rels = open(os.path.join(tmp, 'ppt/_rels/presentation.xml.rels'), encoding='utf8').read()
    ct = open(os.path.join(tmp, '[Content_Types].xml'), encoding='utf8').read()
    nslides = len([f for f in os.listdir(os.path.join(tmp, 'ppt/slides')) if re.fullmatch(r'slide\d+\.xml', f)])
    maxid = max(int(i) for i in re.findall(r'<p:sldId id="(\d+)"', pres))
    maxr = max(int(i) for i in re.findall(r'Id="rId(\d+)"', rels))
    for t, (title, foot, tag, boxes) in enumerate(NEW, 1):
        x = base
        paras = list(re.finditer(PAR, x, flags=re.S))
        def P(start):
            c = [m for m in re.finditer(PAR, x, flags=re.S) if ptext(m.group(0)).startswith(start)]
            assert len(c) == 1, (start, len(c)); return c[0]
        repl = [('부록 A3: 추가 민감도 점검', title), ('추가 검증', '질의 대비'), ('김승민 · 석사학위논문 심사 발표', '김승민 · 석사학위논문 심사 발표  |  ' + foot), ('부록 A3', tag)]
        for start, new in repl:
            m = P(start); x = x[:m.start()] + set_para_text(m.group(0), new) + x[m.end():]
        heads = ['① 사후보정 갱신 속도', '② 거래량 공변량', '③ TimesFM-2.5 1년·가격', '④ GARCH-t 비정상']
        bodies = ['· γ = 0.005', '· 종가 단변량 외에', '· 입력 정규화 해제', '· 합성 136,000건']
        for (h, b), (nh, nb) in zip(zip(heads, bodies), boxes):
            m = P(h); x = x[:m.start()] + set_para_text(m.group(0), nh) + x[m.end():]
            m = P(b); x = x[:m.start()] + set_para_text(m.group(0), nb) + x[m.end():]
        k = nslides + t
        open(sl(k), 'w', encoding='utf8').write(x)
        shutil.copy(os.path.join(tmp, 'ppt/slides/_rels/slide23.xml.rels'), os.path.join(tmp, f'ppt/slides/_rels/slide{k}.xml.rels'))
        rid = f'rId{maxr + t}'
        rels = rels.replace('</Relationships>', f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{k}.xml"/></Relationships>')
        pres = pres.replace('</p:sldIdLst>', f'<p:sldId id="{maxid + t}" r:id="{rid}"/></p:sldIdLst>')
        ct = ct.replace('</Types>', f'<Override PartName="/ppt/slides/slide{k}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/></Types>')
    open(os.path.join(tmp, 'ppt/presentation.xml'), 'w', encoding='utf8').write(pres)
    open(os.path.join(tmp, 'ppt/_rels/presentation.xml.rels'), 'w', encoding='utf8').write(rels)
    open(os.path.join(tmp, '[Content_Types].xml'), 'w', encoding='utf8').write(ct)
    if os.path.exists(dst): os.remove(dst)
    with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as zo:
        names = z.namelist()
        extra = [f'ppt/slides/slide{nslides + t}.xml' for t in range(1, len(NEW) + 1)] + [f'ppt/slides/_rels/slide{nslides + t}.xml.rels' for t in range(1, len(NEW) + 1)]
        for nm in ['[Content_Types].xml'] + [n for n in names if n != '[Content_Types].xml'] + extra:
            zo.write(os.path.join(tmp, nm), nm)
    print('done, bad', bad, 'slides', nslides, '+', len(NEW))

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
