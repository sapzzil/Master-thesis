"""발표 자료 v9 2차(181차): 3쪽 표·쉬운 표현 22곳·내용 수정·가설 판정 장·질의응답 장·결과 장 14pt.
사용: python3 deck_v9b.py <v9.pptx> <out.pptx>"""
import sys, os, re, html, zipfile, tempfile, shutil
sys.path.insert(0, os.path.dirname(__file__))
from pptx_phrase import replace_in_xml, ptext, PAR

EMU = 12700
BAD = []

# ---------- 도우미 ----------
def shapes(x):
    return list(re.finditer(r'<p:(sp|pic|graphicFrame|cxnSp)>.*?</p:\1>', x, re.S))

def find(x, key):
    """도형 찾기: key가 'name:...'이면 이름, 아니면 글자 시작."""
    c = []
    for m in shapes(x):
        s = m.group(0)
        if key.startswith('name:'):
            if re.search(r'<p:cNvPr id="\d+" name="%s"' % re.escape(key[5:]), s): c.append(m)
        else:
            t = ' '.join(ptext(p) for p in re.findall(PAR, s, re.S))
            if t.strip().startswith(key): c.append(m)
    if len(c) != 1:
        BAD.append(('find', key, len(c))); return None
    return c[0]

def sub_shape(x, key, fn):
    m = find(x, key)
    if m is None: return x
    return x[:m.start()] + fn(m.group(0)) + x[m.end():]

def geo(x0, y0, w, h):
    def f(s):
        return re.sub(r'<a:off x="\d+" y="\d+"/><a:ext cx="\d+" cy="\d+"/>',
                      f'<a:off x="{int(x0*EMU)}" y="{int(y0*EMU)}"/><a:ext cx="{int(w*EMU)}" cy="{int(h*EMU)}"/>', s, count=1)
    return f

def set_sz(rpr, sz, b=None):
    rpr = re.sub(r' sz="\d+"', '', rpr)
    rpr = re.sub(r'<a:(rPr|endParaRPr)\b', lambda m: f'<a:{m.group(1)} sz="{int(sz*100)}"', rpr, count=1)
    if b is not None:
        rpr = re.sub(r' b="\d"', '', rpr)
        rpr = re.sub(r'<a:(rPr|endParaRPr)\b', lambda m: f'<a:{m.group(1)} b="{1 if b else 0}"', rpr, count=1)
    return rpr

def color(rpr, rgb):
    if rgb is None: return rpr
    if '<a:solidFill>' in rpr:
        return re.sub(r'<a:solidFill>.*?</a:solidFill>', f'<a:solidFill><a:srgbClr val="{rgb}"/></a:solidFill>', rpr, count=1, flags=re.S)
    if rpr.endswith('/>'):
        return rpr[:-2] + f'><a:solidFill><a:srgbClr val="{rgb}"/></a:solidFill></a:rPr>'
    return rpr.replace('>', f'><a:solidFill><a:srgbClr val="{rgb}"/></a:solidFill>', 1)

def tmpl(p):
    ppr = re.search(r'<a:pPr\b[^>]*/>|<a:pPr\b.*?</a:pPr>', p, re.S)
    rpr = re.search(r'<a:rPr\b[^>]*/>|<a:rPr\b.*?</a:rPr>', p, re.S)
    if rpr is None:
        e = re.search(r'<a:endParaRPr\b[^>]*/>|<a:endParaRPr\b.*?</a:endParaRPr>', p, re.S)
        r = e.group(0).replace('endParaRPr', 'rPr') if e else '<a:rPr lang="ko-KR"/>'
    else:
        r = rpr.group(0)
    return (ppr.group(0) if ppr else ''), r

def build_p(ppr, rpr, text, sz, b=None, rgb=None, spc=None):
    if spc is not None:
        ppr2 = re.sub(r'<a:spcBef>.*?</a:spcBef>', '', ppr, flags=re.S)
        add = f'<a:spcBef><a:spcPts val="{int(spc*100)}"/></a:spcBef>'
        if ppr2 == '': ppr2 = f'<a:pPr>{add}</a:pPr>'
        elif ppr2.endswith('/>'): ppr2 = ppr2[:-2] + f'>{add}</a:pPr>'
        else:
            # spcBef는 lnSpc 다음 자리
            if '</a:lnSpc>' in ppr2: ppr2 = ppr2.replace('</a:lnSpc>', '</a:lnSpc>' + add, 1)
            else: ppr2 = re.sub(r'(<a:pPr\b[^>]*>)', r'\1' + add, ppr2, count=1)
        ppr = ppr2
    runs = []
    parts = text.split('**')
    for i, seg in enumerate(parts):
        if seg == '': continue
        if b is not None: bold = b
        elif len(parts) > 1: bold = (i % 2 == 1)
        else: bold = None
        r = color(set_sz(rpr, sz, bold), rgb)
        for k, ln in enumerate(seg.split('\n')):
            if k: runs.append(f'<a:br>{r}</a:br>')
            if ln: runs.append(f'<a:r>{r}<a:t>{html.escape(ln, quote=False)}</a:t></a:r>')
    end = set_sz(rpr.replace('<a:rPr', '<a:endParaRPr').replace('</a:rPr>', '</a:endParaRPr>'), sz)
    return f'<a:p>{ppr}{"".join(runs)}{end}</a:p>'

def set_text(paras, sz, title=None, tsz=None, spc=4, rgb=None, trgb=None, b=False):
    """도형 글자 전체 교체. paras: 문단 목록(**굵게**, \\n 줄바꿈)."""
    def f(s):
        tb = re.search(r'(<p:txBody>.*?)(<a:p>.*</a:p>|<a:p [^>]*>.*</a:p>)(\s*</p:txBody>)', s, re.S)
        ps = re.findall(PAR, tb.group(2), re.S)
        out = []
        withr = [q for q in ps if '<a:r>' in q]
        if title is not None:
            tp, tr = tmpl(ps[0])
            rest = [q for q in ps[1:] if '<a:r>' in q]
            bp, br = tmpl(rest[0] if rest else ps[0])
            out.append(build_p(tp, tr, title, tsz or sz, b=True, rgb=trgb))
        else:
            bp, br = tmpl(withr[0] if withr else ps[0])
        for i, t in enumerate(paras):
            out.append(build_p(bp, br, t, sz, b=(None if '**' in t else b), rgb=rgb, spc=(spc if (i or title is not None) else None)))
        return s[:tb.start(2)] + ''.join(out) + s[tb.end(2):]
    return f

def bump(sz):
    """도형 안 모든 글자 크기를 sz 이상으로."""
    def f(s):
        return re.sub(r' sz="(\d+)"', lambda m: f' sz="{max(int(m.group(1)), int(sz*100))}"', s)
    return f

def table_rows(rows, sz=None, colors=None, bold=None):
    """표 칸 글자 교체. rows[r][c] = 글자 또는 None(그대로)."""
    def f(s):
        trs = list(re.finditer(r'<a:tr\b.*?</a:tr>', s, re.S))
        out = s
        for ri in reversed(range(len(trs))):
            if ri >= len(rows): continue
            tr = trs[ri].group(0)
            tcs = list(re.finditer(r'<a:tc\b.*?</a:tc>', tr, re.S))
            newtr = tr
            for ci in reversed(range(len(tcs))):
                if ci >= len(rows[ri]) or rows[ri][ci] is None: continue
                tc = tcs[ci].group(0)
                ps = re.findall(PAR, tc, re.S)
                pp, rr = tmpl(ps[0])
                cur = int(re.search(r'sz="(\d+)"', rr).group(1)) / 100 if 'sz="' in rr else 12
                rgb = colors.get((ri, ci)) if colors else None
                bb = bold.get((ri, ci)) if bold else None
                newp = build_p(pp, rr, rows[ri][ci], sz or cur, b=bb, rgb=rgb)
                tc2 = re.sub(r'(<a:txBody>.*?<a:lstStyle/>).*(</a:txBody>)', lambda m: m.group(1) + newp + m.group(2), tc, count=1, flags=re.S)
                newtr = newtr[:tcs[ci].start()] + tc2 + newtr[tcs[ci].end():]
            out = out[:trs[ri].start()] + newtr + out[trs[ri].end():]
        return out
    return f

def cols(ws):
    def f(s):
        g = re.search(r'<a:tblGrid>.*?</a:tblGrid>', s, re.S)
        return s[:g.start()] + '<a:tblGrid>' + ''.join(f'<a:gridCol w="{int(w*EMU)}"/>' for w in ws) + '</a:tblGrid>' + s[g.end():]
    return f

def heights(hs):
    def f(s):
        trs = list(re.finditer(r'<a:tr h="\d+"', s))
        for k in reversed(range(len(trs))):
            if k < len(hs) and hs[k]:
                s = s[:trs[k].start()] + f'<a:tr h="{int(hs[k]*EMU)}"' + s[trs[k].end():]
        return s
    return f

def remove(x, key):
    m = find(x, key)
    return x if m is None else x[:m.start()] + x[m.end():]

def rep(x, pairs, n):
    for o, nw in pairs:
        x, k = replace_in_xml(x, o, nw)
        if k != 1: BAD.append(('rep', n, o[:40], k))
    return x

# ---------- 문구 교체(작은 것) ----------
E = {
 2: [('실험 결과 — RQ1 (오차 원인 진단)', '실험 결과 — RQ1 (커버리지 차이는 어디에서 커지는가)'),
     ('분산 분해(90% vs 7%)', '커버리지 차이 나눠 보기(90% 대 7%)'),
     ('연구 기여(C1~C4) 종합, 실무 도입 절차, 연구의 한계 및 의의 (부록 A1~A7 별첨)', '가설 판정 요약, 연구 기여(C1~C4), 실무 도입 절차, 한계와 의의 (부록 A1~A7 별첨)'),
     ('19~20쪽', '19~21쪽')],
 3: [('구간이 너무 좁거나 넓을 때의 실무 손실 (예시: 기준가 100원, 1억 원 투자, 하루 변동 약 2.1%)',
      '80% 구간이 맞으면, 실제 손실이 구간 아래 끝(손실 한도)을 넘는 날은 10%여야 함 (예: 1억 원 투자, 하루 변동 약 2.1%)'),
     ('실제 주가 변동은 모델 예측과 무관함. 모델이 손실을 작게 예상할수록 실제 손실이 예상선을 넘는 날이 잦아짐.',
      '실제 주가는 모델 예측과 상관없이 움직이므로, 한도를 작게 잡을수록 넘는 날이 잦아짐.')],
 4: [('· 적정 범위(78~82%): 시나리오당 6,000건의 표본 오차(약 ±1%p)보다 큰 실질 기준(±3%p로 넓혀도 결론 같음, 9쪽).',
      '· 적정 범위(78~82%): 6,000건이면 우연히 생기는 흔들림이 약 ±1%p라서, 그보다 넉넉한 ±2%p를 기준으로 삼음(±3%p로 넓혀도 결론 같음, 9쪽).')],
 5: [('Noguer i Alonso 외(2026): 대형주', 'Noguer i Alonso와 Franklin(2026): 대형주'),
     ('점 예측 정확도만 평가', '점 예측 위주, 수익률 구간 미평가'),
     ('수익률 예측구간 커버리지 및', '(Upadhyay는 변동성 구간만 보고)'),
     ('오차 원인(특성 vs 설정) 미분석', '특성·설정에 따른 차이 미분석'),
     ('오차 원인을 특성 vs 설정으로 분리', '특성·설정에 따라 얼마나 달라지는지 비교'),
     ('RQ1 (원인 진단 · ← N1)', 'RQ1 (진단 · ← N1)'),
     ('80% 구간 커버리지 오차의 원인은 금융 특성인가, 모델·입력 설정인가?', '80% 커버리지는 금융 특성과 모델·입력 설정 중 어느 쪽에 따라 더 달라지는가?'),
     ('(정답 분포를 아는 오라클 모형으로 80% 기준을 먼저 확인)', '(오라클 모형으로 80% 기준을 먼저 확인)')],
 6: [('실측 최댓값의 2배으로', '실측 최댓값의 2배로'),
     ('• 100개 계열의 공통 난수를 모든 시나리오가 공유하고 일별 변동 크기(2.11%, 평균 0)를 동일하게 고정해 변동 구조의 차이만 비교함.',
      '• 모든 시나리오가 같은 난수 100개 계열에서 출발하고 일별 변동 크기(2.11%, 평균 0)도 같게 고정함. 그래서 시나리오끼리는 특성 하나만 다름.'),
     ('평온/격변 평균 지속', '국면 평균 지속 일수'),
     ('L3 275 / 59\nL5 9.5 / 2.0', 'L3 평온 275일\n격변 59일\nL5 평온 9.5일\n격변 2.0일')],
 8: [('국면 전환 폭(격변기 변동 크기)이 클수록 커버리지가 하락한다', '국면 전환 크기(격변기/평온기 변동 비)가 클수록 커버리지가 하락한다'),
     ('(시나리오당 6,000건의 표본 오차 약 ±1%p를 상회하는 기준)', '(6,000건의 우연한 흔들림 약 ±1%p보다 넉넉한 기준)')],
 9: [('RQ1 ①: 금융 특성 없는 데이터(L1)에서도 커버리지 75.3~87.6% 분산', 'RQ1 ①: 금융 특성 없는 데이터(L1)에서도 커버리지 75.3~87.6%로 퍼짐'),
     ('   ■ 빨간 테두리: TimesFM-2.5 1년·가격 (전 시나리오 86.8~88.4%)', '   ■ 빨간 테두리: TimesFM-2.5 1년·가격')],
 10: [('부록 A.3, 표 A-2', '논문 부록 A.3, 표 A-2')],
 11: [('RQ1 ③: 본 실험 범위에서 커버리지 차이의 90%는 모델·설정, 7%는 금융 특성', 'RQ1 ③: 본 실험 범위에서 커버리지 차이의 90%는 모델·설정, 7%는 금융 특성으로 설명됨'),
      ('그림 4-2, 부록 A.4', '그림 4-2, 논문 부록 A.4')],
 13: [('그림 5-3, 부록 A.3', '그림 5-3, 논문 부록 A.3')],
 16: [('RQ3 ②: ACI-CQR로 전 조건 평균 80% 복원, 대가는 구간 폭 5~48% 증가', 'RQ3 ②: ACI-CQR로 전 조건 평균 80% 복원, 구간 폭은 오라클 대비 5~48% 넓음')],
 19: [('결론 ①: 연구 기여(Contribution) C1~C4 종합 및 실무 도입 권고 절차', '결론 ②: 연구 기여(Contribution) C1~C4 종합 및 실무 도입 권고 절차'),
      ('실측 강도 기반 합성 실험을 실제 적용 전 사전 점검 절차로 제시', '특성 없는 합성(L1) 점검을 실제 적용 전 사전 점검 절차로 제시'),
      ('(이론 86.6%/RW 86.3%)', '(이론 86.6%, 합성 L5의 RW 1년 86.3%)'),
      ('합성 323(오라클 포함 340)·실제 19개', '합성 323개·실제 19개')],
 20: [('결론 ②: 연구의 한계', '결론 ③: 연구의 한계')],
 21: [('1년·수익률 조건의 커버리지가 공개 후 2.5~5.4%p 하락했으나', '1년·수익률 조건의 커버리지가 공개 후 Chronos-T5·TimesFM·Moirai-2는 2.5~5.4%p(Chronos-2는 0.8%p) 하락했으나')],
 22: [('하이닉스', 'SK하이닉스'), ('한전', '한국전력'), ('모비스', '현대모비스'), ('5.1절, 부록 C,', '5.1절, 논문 부록 C,')],
 23: [('6.5절, 표 6-3, 부록 A.4', '6.5절, 표 6-3, 논문 부록 A.4'),
      ('· 연속 분위수 헤드를 끄면 합성 83.4%·실제 84.3%로 과대가 일부 감소해 출력 헤드가 일부 원인으로 확인됨.',
       '· 출력 헤드는 일부 원인(끄면 합성 87.6% → 83.4%, 4.2%p 감소), 나머지는 미규명.'),
      ('평균 폭 17,318 → 4.87%p 정상화', '평균 폭이 비정상적으로 커졌던 것(17,318%p)이 4.87%p로 돌아옴')],
 24: [('동일 평균 폭 커버리지', '같은 평균 폭일 때의 커버리지'),
      ('불가능 — 필요 배율이 0.8~1.3배(기본 T5는 8~9배)로 모델·조건마다 달라 사전에 알 수 없음', '필요 배율을 사전에 알 수 없음 — 0.8~1.3배(기본 T5는 8~9배)로 모델·조건마다 다름'),
      ('가능 — 배율을 모르는 상태에서 모든 TSFM 출력 뒤에 부착해 80% 수렴', '가능 — 배율을 모르는 상태에서 모든 TSFM 출력 뒤에 붙여 평균 80% 복원'),
      ('고정 배율 적용이 불가능함', '고정 배율을 미리 정할 수 없음'),
      ('온라인으로 평균 80%에 도달하는 데', '평균 80%로 복원하는 데')],
 25: [('· 분산 분해: 커버리지 차이의 90%는 모델·조건, 7%는 시나리오', '· 커버리지 차이를 나눠 보면 90%는 모델·조건, 7%는 시나리오')],
 27: [('6.3~6.6절, 부록 A.2~A.3', '6.3~6.6절, 논문 부록 A.2~A.3'),
      ('배율(0.8~1.3배)을 미리 알 수 없어 실무에서는 쓸 수 없음.', '필요 배율(0.8~1.3배)을 사전에 알 수 없음.'),
      ('· 준비 20일만으로 정한 고정 배율 대조군은 다음 판에서 비교.', '· 준비 20일만으로 정한 고정 배율 대조군과의 비교는 향후 과제.'),
      ('해제 전 결과도 부록에 병기.', '해제 전 결과도 논문 부록 A.3에 병기.'),
      ('· 끄면 과대가 일부만 줄어(합성 87.6% → 83.4%) 이 설정이 출력을 왜곡한다고 볼 근거가 없음. 나머지 원인은 향후 연구.',
       '· 출력 헤드는 일부 원인(끄면 4.2%p 감소), 나머지는 미규명. 권장 방식이라 본 실험에서는 그대로 둠.')],
}

GREEN, RED, NAVY = '15803D', 'C0262D', '1B365D'

# ---------- 도형 단위 다시 쓰기 ----------
def S3(x):
    x = sub_shape(x, 'name:Table 15', table_rows([
        [None, '하루 손실 한도 금액', '실제로 넘은 날 (목표 10%)', '결과'],
        ['한도 적정', None, '10%', '목표대로 맞음'],
        ['너무 작게 잡음', None, '24%', '한도를 넘는 손실이 목표보다 2.4배 잦음'],
        ['너무 크게 잡음', None, '0.9%', '위험을 너무 크게 봐서 투자를 지나치게 줄임']]))
    return x

def S9(x):
    x = sub_shape(x, 'name:TextBox 7', bump(14))
    x = sub_shape(x, 'name:TextBox 9', set_text([
        '• 특성이 없는 L1에서도 TSFM 16개 중 **8개가 적정 범위(78~82%)를 벗어남**(±3%p로 넓히면 5개).',
        '• 같은 TimesFM-2.5 1년도 **가격 입력 87.6%, 수익률 입력 78.8%**로 입력 형태만으로 8.8%p 차이.',
        '• 색은 행(특성 강도)보다 **열(모델·입력 조건)**에 따라 달라짐.'], 14, spc=9))
    x = sub_shape(x, 'L1(특성 없음) 모델별', set_text([
        'Chronos-T5  75.3~78.6%', 'Chronos-2  78.8~81.5%', 'TimesFM-2.5  77.2~87.6%', 'Moirai-2  76.6~81.0%',
        'RW 77.6~79.4%', 'GARCH-t 78.7% · 오라클 79.8%'], 14, title='L1(특성 없음) 모델별 커버리지', tsz=14, spc=0))
    x = sub_shape(x, 'L1(특성 없음) 모델별', geo(652, 318, 270, 178))
    x = sub_shape(x, 'name:TextBox 9', geo(652, 84, 270, 228))
    return x

def S10(x):
    boxes = [('1. Chronos-T5 출력 방식', '1. Chronos-T5 출력 방식', '값을 4,096칸 눈금으로 나눠 예측'),
             ('2. 라이브러리 기본값', '2. 라이브러리 기본값', '확률 높은 50칸 안에서만 뽑음(top-k = 50)'),
             ('3. 수익률 입력 시 충돌', '3. 수익률 입력', '80% 구간에 수백 칸이 필요한데 50칸으로 양 끝이 잘림'),
             ('4. 결과: 구간이 지나치게 좁아짐', '4. 결과', '구간이 지나치게 좁아짐(합성 L1 커버리지 14%)')]
    for key, t, b in boxes:
        x = sub_shape(x, key, set_text([b], 14, title=t, tsz=14, spc=3))
    x = sub_shape(x, 'name:TextBox 15', bump(14))
    x = sub_shape(x, 'name:Table 16', table_rows([[None, '기본 설정\n(top-k=50)', None]]))
    x = sub_shape(x, 'name:Table 16', bump(14))
    x = sub_shape(x, 'name:TextBox 17', set_text([
        '• 가격은 하루 변동이 가격 수준에 비해 작아 몇 칸 안에 들어가므로 영향이 없었음(차이 0.01%p).',
        '• 점검 중 발견해 이 설정만 해제(top-k = 4,096)하고 같은 과제·시드·평가 코드로 재계산함. 해제 전 결과도 논문 부록 A.3에 실음.',
        '• 실제 주가의 오차(17%)가 **특성 없는 합성 L1에서도 같은 수준(14%)으로 나타남**.'], 14, spc=9))
    return x

def S11(x):
    x = sub_shape(x, 'name:TextBox 7', set_text([
        '커버리지 차이를 나눠 보면 모델·조건 차이가 90%, 특성 차이가 7%를 설명함 (TimesFM 1년·가격을 빼도 76% 대 18%)'], 14, b=True))
    x = sub_shape(x, 'name:TextBox 7', geo(40, 69, 878, 24))
    x = sub_shape(x, 'name:Picture 8', geo(153, 95, 651, 81))
    x = sub_shape(x, 'name:Picture 9', geo(165, 180, 628, 199))
    x = sub_shape(x, 'name:TextBox 10', set_text([
        '• 특성을 가장 강한 단계(L5)까지 올려도 TSFM의 커버리지 변화는 대부분 3%p 이내. 같은 데이터에서 RW 1년은 7.0%p까지 움직여, 특성 강도는 충분했음.',
        '• 커버리지를 낮춘 특성은 **변동성 군집뿐**이었고, 꼬리·잦은 전환은 80% 구간에서 오히려 커버리지를 높임.',
        '• 98% 같은 극단 구간에서는 꼬리와 국면 전환이 커버리지를 낮춤(12쪽).'], 14, spc=3))
    x = sub_shape(x, 'name:TextBox 10', geo(40, 382, 878, 120))
    return x

def S12(x):
    x = sub_shape(x, 'name:TextBox 8', bump(14))
    x = sub_shape(x, 'name:Picture 9', geo(85, 102, 428, 181))
    x = sub_shape(x, 'name:Table 10', geo(40, 292, 518, 133))
    x = sub_shape(x, 'name:Table 10', table_rows([
        ['분포 (분산 같음)', '80% 구간', '95% 구간', '99% 구간'],
        ['정규분포 (L1)', '80.0%', '95.0%', '99.0%\n(벗어남 1.0%)'],
        ['두꺼운 꼬리\n(L5, ν=3.56)', '86.6%\n(+6.6%p)', '95.2%', '97.8%\n(벗어남 2.2%)']], sz=14))
    x = sub_shape(x, 'name:Table 10', heights([30, 48, 48]))
    x = sub_shape(x, 'name:TextBox 11', set_text([
        '• 분산이 같으면 꼬리가 두꺼울수록 값이 평균 근처에 더 많이 몰려, **80% 구간의 이론 커버리지가 86.6%로 올라감**(합성 L5의 RW 1년 86.3%).',
        '• 반대로 99% 구간은 꼬리 쪽 극단값의 영향이 커져 **97.8%로 내려감**(벗어나는 비율 1.0% → 2.2%). Chronos-2의 98% 구간에서도 꼬리·국면 전환이 커버리지를 낮춤.',
        '• 따라서 **80% 구간 하나만 보고 꼬리 위험 대응력을 판단하면 잘못 볼 수 있음**.'], 14, spc=10))
    return x

def S13(x):
    x = sub_shape(x, 'name:Rounded Rectangle 9', bump(14))
    x = sub_shape(x, 'name:Rounded Rectangle 9', geo(232, 108, 216, 56))
    x = sub_shape(x, 'name:Right Arrow 10', geo(450, 140, 11, 13))
    x = sub_shape(x, 'name:Rounded Rectangle 11', set_text([
        '실제 커버리지 차이의 92%는 모델·조건, 종목 차이는 1%'], 14, title='합성 L1과 실제의 차이: 평균 1.1%p', tsz=16, spc=2))
    x = sub_shape(x, 'name:TextBox 12', set_text([
        '• 실제 10종목의 커버리지(76~88%)도 특성 없는 합성 L1과 평균 1.1%p 차이. 가장 많이 다른 것은 RW 1년(3.6%p).',
        '• TimesFM 1년·가격(87.6% → 87.7%), 기본 설정 Chronos-T5(14% → 17%)처럼 **크게 어긋나는 설정은 합성 L1에서 미리 드러남**.',
        '• 다만 작은 차이까지 맞히지는 못함: "전부 80%일 것"이라고 찍는 것보다 확실히 낫다고 할 수 없음(19개 중 12개만 더 가까움, p = 0.07).'], 14, spc=8))
    x = sub_shape(x, 'name:TextBox 12', geo(572, 178, 346, 318))
    return x

def S14(x):
    x = sub_shape(x, 'name:Picture 8', geo(32, 110, 500, 347))
    x = sub_shape(x, 'name:Table 9', table_rows([
        ['RW 대비 손실 개선율\n(+면 TSFM이 나음)', '조건 수', '개선율 범위'],
        ['RW보다 유의하게 나쁨', '12개', '-0.8 ~ -9.8%'],
        ['통계적 차이 없음', '3개', '-0.1 ~ +0.3%'],
        ['통계적으로는 나으나\n차이 2% 미만', '1개', '+0.9%']], sz=14))
    x = sub_shape(x, 'name:Table 9', geo(548, 80, 372, 190))
    x = sub_shape(x, 'name:Table 9', cols([196, 72, 104]))
    x = sub_shape(x, 'name:Table 9', heights([48, 30, 30, 48]))
    x = sub_shape(x, 'name:TextBox 10', set_text([
        '• 실질 기준(2%)을 넘어 **RW보다 나은 TSFM 조건은 없음**(H5 지지 안 됨). 모델 공개 이후 기간도 같음(부록 A1).',
        '• 손실이 가장 작은 것은 **GARCH-t 1년**이며, TSFM 1년 8개 조건 모두 그보다 0.4~5.1% 큼.',
        '• 일별 수익률은 방향보다 변동 크기가 중요해, 단순 기준 모형도 강함.'], 14, spc=8))
    x = sub_shape(x, 'name:TextBox 10', geo(548, 290, 372, 208))
    return x

def S15(x):
    boxes = [('① TSFM 원래 구간', '① TSFM 원래 구간', '모델은 그대로 두고 10%·90% 분위수 출력 사용'),
             ('② 이탈 점수 계산', '② 이탈 점수 계산', '실제값이 구간 밖으로 나간 거리 ÷ 폭(구간 안이면 음수)'),
             ('③ 구간 경계 조정', '③ 구간 경계 조정', '과거 이탈 기록으로 80%를 맞추려면 얼마나 넓혀야 하는지 계산해 경계를 옮김'),
             ('⑥ 목표 이탈률', '⑥ 목표 이탈률 갱신', '어제 구간 밖이면 오늘은 조금 넓게, 안이면 조금 좁게(조정 속도 γ = 0.05)'),
             ('⑤ 다음 날 실제값 확인', '⑤ 다음 날 실제값 확인', '보정 구간 밖이면 1, 안이면 0으로 기록'),
             ('④ 보정 구간 사용', '④ 보정 구간 사용', '조정된 80% 구간으로 그날의 VaR·투자 비중 결정')]
    for key, t, b in boxes:
        x = sub_shape(x, key, set_text([b], 14, title=t, tsz=14, spc=3))
    x = sub_shape(x, '단순 일괄 확대', set_text([
        '· 결과를 보기 전에는 구간을 몇 배로 키워야(또는 줄여야) 80%가 맞는지 알 수 없음(필요 배율 0.8~1.3배, 모델마다 다름).'],
        14, title='단순 일괄 확대(배율 곱하기)의 한계', tsz=14, spc=4))
    x = sub_shape(x, 'ACI-CQR 적용의 장점', set_text([
        '· 그날까지의 이탈 기록만으로 구간을 넓히거나 좁혀 평균 80%로 복원.',
        '· 재학습 없이 어떤 TSFM 출력 뒤에도 붙일 수 있음.',
        '· 양 끝을 함께 조정해, 하단(VaR) 위반율만 따로 맞추지는 않음.'], 14, title='ACI-CQR 적용의 장점', tsz=14, spc=0))
    x = sub_shape(x, '단순 일괄 확대', geo(47, 356, 421, 142))
    x = sub_shape(x, 'ACI-CQR 적용의 장점', geo(493, 352, 421, 148))
    return x

def S16(x):
    x = sub_shape(x, 'name:Table 9', table_rows([
        ['조건 (합성 기준)', '오라클 대비 폭', '비고'],
        ['1년 조건', '1.05 ~ 1.24배', '비교적 좁음'],
        ['한 달 조건', '1.14 ~ 1.48배', '더 넓어짐']], sz=14))
    x = sub_shape(x, 'name:TextBox 10', set_text([
        '• 합성 17개 시나리오 × 19개 모델·조건(323개)과 실제 19개가 모두 77~83% 안으로 들어옴(H6 지지).',
        '• 좁은 구간은 넓히고 넓은 구간은 좁힘(TimesFM 1년·가격: 구간을 0.83배로 좁혀 87.7% → 80.2%).',
        '• 원래 80%에 가까웠던 조건일수록 폭이 덜 늘어남.'], 14, spc=3))
    x = sub_shape(x, 'name:TextBox 10', geo(436, 368, 482, 130))
    return x

def S17(x):
    x = remove(x, '※ 일 변동 1% 목표')
    x = sub_shape(x, 'name:Picture 7', geo(146, 70, 669, 240))
    x = sub_shape(x, '① 방향 예측 매매', set_text([
        '· 거래비용을 넣으면 모든 TSFM(연 -1.0~16.4%)이 계속 보유(연 25.4%)보다 낮음.',
        '· 방향 적중률 49.3~51.6%, 잦은 매매로 비용 누적.',
        '→ 방향 예측에는 쓸 수 없음.'], 14, title='① 방향 예측 매매 (중앙값 > 0이면 보유)', tsz=14, spc=3))
    x = sub_shape(x, '② 위험 관리 규칙', set_text([
        '· 비중 조절(일 변동 1% 목표): 실제 변동이 목표의 1.05~1.14배로 가까워짐. 최대 낙폭 축소(-33.5% → -17~-25%)는 RW 구간으로도 같음.',
        '· VaR 10%: 10종목 중 8종목 이상에서 위반율 검정을 통과한 모델·조건이 19개 중 8개 → 14개.'],
        14, title='② 위험 관리 규칙 (목표 변동성 비중 조절 · VaR 10%)', tsz=14, spc=3))
    x = sub_shape(x, '① 방향 예측 매매', geo(40, 318, 428, 180))
    x = sub_shape(x, '② 위험 관리 규칙', geo(486, 318, 433, 180))
    return x

def S18(x):
    x = sub_shape(x, 'name:Picture 11', geo(32, 110, 500, 330))
    x = sub_shape(x, '평온기–고변동기 격차', set_text([
        '(19개 모델·조건 평균, 보정 전 최대 22.8%p)'], 14, title='평온기–고변동기 격차: 10.1%p → 2.9%p', tsz=16, spc=2))
    x = sub_shape(x, '평온기–고변동기 격차', geo(548, 78, 372, 62))
    x = sub_shape(x, 'name:Table 9', bump(14))
    x = sub_shape(x, 'name:Table 9', geo(548, 150, 372, 170))
    x = sub_shape(x, 'name:Table 9', cols([124, 124, 124]))
    x = sub_shape(x, 'name:TextBox 10', set_text([
        '• 80% 복원은 전체 기간 평균 기준(시기마다 맞춰 주지는 않음)이라, 1년 조건은 변동 큰 달에 76~79%로 조금 낮음.',
        '• 한 달·가격 조건은 보정 후에도 위반이 몰리는 날이 남음(Christoffersen 검정 통과 0~3종목). 이 검정은 전날과의 관계만 봐서 여러 날 몰림은 잘 못 잡음.'],
        14, spc=8))
    x = sub_shape(x, 'name:TextBox 10', geo(548, 328, 372, 170))
    return x

def S6(x):
    x = sub_shape(x, 'name:Table 8', geo(40, 350, 414, 102))
    return x

FUN = {6: S6, 3: S3, 9: S9, 10: S10, 11: S11, 12: S12, 13: S13, 14: S14, 15: S15, 16: S16, 17: S17, 18: S18}

# ---------- 새 장: 가설 판정 요약(슬라이드 8 복제) ----------
VERDICT = [
 ['질문', '가설', '판정', '핵심 발견'],
 ['RQ1', 'H1 군집 → 하락', '일부 지지', '2개 조건에서 2%p 이상 하락(−2.0~−2.5%p). 커버리지를 낮춘 특성은 군집뿐'],
 ['RQ1', 'H2 꼬리 → 하락', '지지 안 됨 (반대)', '11개 조건에서 유의한 상승. 꼬리가 두꺼운 분포의 모양 때문(98% 구간에서는 하락)'],
 ['RQ1', 'H3a 전환 빈도 → 하락', '지지 안 됨 (반대)', '7개 조건에서 작은 상승. 국면이 섞이면 전체 분포의 꼬리가 두꺼워짐'],
 ['RQ1', 'H3b 전환 크기 → 하락', '지지 안 됨', '유의한 변화 없음'],
 ['RQ1', 'H4 특성마다 다름', '16개 중 10개 지지', '10개 모두 군집이 가장 불리'],
 ['RQ2', 'H5 TSFM이 RW보다 정확', '지지 안 됨', '12개 RW보다 손실 큼, 3개 차이 없음, 1개 작은 우위(2% 미만). 1년 조건 모두 GARCH-t보다 손실 큼'],
 ['RQ3', 'H6 보정 후 80% 복원', '지지', '합성 323개·실제 19개 모두 77~83%. 평균 기준이며 위반 몰림은 일부 조건에 남음'],
]
VCOL = {'일부 지지': 'B45309', '지지 안 됨 (반대)': RED, '지지 안 됨': RED, '16개 중 10개 지지': GREEN, '지지': GREEN}

def make_verdict(x8):
    x = x8
    x = rep(x, [('연구 설계 ③: 실험 전에 고정한 가설 7개(H1~H6, H3는 a·b로 구분)와 판정 기준', '결론 ①: 가설 판정 요약과 세 연구 질문의 답'),
                ('본문 3.6.2절, 표 3-7, 3.7절', '본문 7.1절, 표 7-1')], 'V')
    x = remove(x, '1. 통계적 유의성 기준')
    x = remove(x, '2. 실질적 크기 기준')
    def tbl(s):
        s = s.replace('<a:gridCol w="822960"/><a:gridCol w="777240"/><a:gridCol w="5852160"/>',
                      f'<a:gridCol w="{65*EMU}"/><a:gridCol w="{205*EMU}"/><a:gridCol w="{160*EMU}"/><a:gridCol w="{451*EMU}"/>')
        def row(m):
            tr = m.group(0)
            tcs = re.findall(r'<a:tc\b.*?</a:tc>', tr, re.S)
            tr = tr.replace(tcs[1], tcs[1] + tcs[1], 1)
            return re.sub(r'<a:tr h="\d+"', '<a:tr h="420000"', tr)
        s = re.sub(r'<a:tr\b.*?</a:tr>', row, s, flags=re.S)
        return s
    x = sub_shape(x, 'name:Table 7', tbl)
    colors = {(r, 2): VCOL[VERDICT[r][2]] for r in range(1, 8)}
    bold = {(r, 2): True for r in range(1, 8)}
    rows = [list(r) for r in VERDICT]
    x = sub_shape(x, 'name:Table 7', table_rows(rows, sz=13, colors=colors, bold=bold))
    x = sub_shape(x, 'name:Table 7', geo(40, 74, 881, 310))
    x = sub_shape(x, 'name:Table 7', heights([26, 30, 42, 30, 30, 30, 42, 42]))
    x = sub_shape(x, '3. H6 (사후보정 복원) 판정 기준', set_text([
        '**RQ1**  본 실험 범위에서 커버리지는 금융 특성보다 모델·입력 설정에 따라 더 크게 달라짐',
        '**RQ2**  실제 주가에서 분포 정확도는 RW 수준이며 GARCH-t보다 낮음',
        '**RQ3**  재학습 없는 사후보정으로 평균 80% 복원, 대가는 구간 폭 증가'], 13.5, title='세 연구 질문의 답', tsz=14, spc=2))
    x = sub_shape(x, '세 연구 질문의 답', geo(40, 392, 881, 108))
    return x

def fix_verdict_align(x):
    """가설·판정 칸 가운데 정렬, 핵심 발견 칸 왼쪽 정렬."""
    m = find(x, 'name:Table 7'); s = m.group(0)
    def row(mr):
        tr = mr.group(0)
        tcs = list(re.finditer(r'<a:tc\b.*?</a:tc>', tr, re.S))
        out = tr
        for ci in reversed(range(len(tcs))):
            al = 'l' if ci in (1, 3) else 'ctr'
            tc = re.sub(r'<a:pPr algn="\w+"', f'<a:pPr algn="{al}"', tcs[ci].group(0))
            out = out[:tcs[ci].start()] + tc + out[tcs[ci].end():]
        return out
    trs = list(re.finditer(r'<a:tr\b.*?</a:tr>', s, re.S))
    s2 = s
    for k in reversed(range(1, len(trs))):
        s2 = s2[:trs[k].start()] + row(trs[k]) + s2[trs[k].end():]
    return x[:m.start()] + s2 + x[m.end():]

# ---------- 새 장: 질의응답(슬라이드 1 복제) ----------
def make_qa(x1):
    x = x1
    x = sub_shape(x, 'name:TextBox 3', set_text(['감사합니다', '질의응답'], 34, spc=0, b=True))
    x = sub_shape(x, '실측 기반 합성 데이터', set_text(['부록 A1~A7: 공개 이후 기간 점검 · 종목별 커버리지 · 민감도 · 대조군 · 질의 대비 3장'], 16))
    return x

# ---------- 실행 ----------
def main(src, dst):
    tmp = tempfile.mkdtemp(); z = zipfile.ZipFile(src); z.extractall(tmp)
    sl = lambda n: os.path.join(tmp, f'ppt/slides/slide{n}.xml')
    rd = lambda n: open(sl(n), encoding='utf8').read()
    def wr(n, s): open(sl(n), 'w', encoding='utf8').write(s)
    x8, x1 = rd(8), rd(1)
    for n in range(1, 28):
        x = rd(n)
        if n in E: x = rep(x, E[n], n)
        if n in FUN: x = FUN[n](x)
        if 9 <= n <= 18:
            x = re.sub(r' sz="(\d+)"', lambda m: m.group(0) if int(m.group(1)) in (950,) or int(m.group(1)) >= 1400 else ' sz="1400"', x)
        wr(n, x)
    v = fix_verdict_align(make_verdict(x8)); q = make_qa(x1)
    # 새 슬라이드 파일
    pres = open(os.path.join(tmp, 'ppt/presentation.xml'), encoding='utf8').read()
    rels = open(os.path.join(tmp, 'ppt/_rels/presentation.xml.rels'), encoding='utf8').read()
    ct = open(os.path.join(tmp, '[Content_Types].xml'), encoding='utf8').read()
    maxid = max(int(i) for i in re.findall(r'<p:sldId id="(\d+)"', pres))
    maxr = max(int(i) for i in re.findall(r'Id="rId(\d+)"', rels))
    new = {28: (v, 8), 29: (q, 1)}
    rid_of = {}
    for t, (k, (xml, base)) in enumerate(new.items(), 1):
        wr(k, xml)
        shutil.copy(os.path.join(tmp, f'ppt/slides/_rels/slide{base}.xml.rels'), os.path.join(tmp, f'ppt/slides/_rels/slide{k}.xml.rels'))
        rid = f'rId{maxr + t}'; rid_of[k] = (rid, maxid + t)
        rels = rels.replace('</Relationships>', f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{k}.xml"/></Relationships>')
        ct = ct.replace('</Types>', f'<Override PartName="/ppt/slides/slide{k}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/></Types>')
    # 순서: 1~18, 판정(28), 19, 20, 질의응답(29), 21~27
    rmap = dict(re.findall(r'Id="(rId\d+)"[^>]*Target="slides/slide(\d+)\.xml"', rels))
    rmap = {int(v): r for r, v in rmap.items()}
    ids = dict((r, i) for i, r in re.findall(r'<p:sldId id="(\d+)" r:id="(rId\d+)"/>', pres))
    order = list(range(1, 19)) + [28, 19, 20, 29] + list(range(21, 28))
    lst = []
    for n in order:
        if n in rid_of: rid, sid = rid_of[n]
        else: rid = rmap[n]; sid = ids[rid]
        lst.append(f'<p:sldId id="{sid}" r:id="{rid}"/>')
    pres = re.sub(r'<p:sldIdLst>.*?</p:sldIdLst>', '<p:sldIdLst>' + ''.join(lst) + '</p:sldIdLst>', pres, flags=re.S)
    # 쪽 번호
    total = 22
    for pos, n in enumerate(order, 1):
        if pos > total: break
        x = rd(n)
        x2 = re.sub(r'<a:t>\d+ / 20</a:t>', f'<a:t>{pos} / {total}</a:t>', x)
        wr(n, x2)
    open(os.path.join(tmp, 'ppt/presentation.xml'), 'w', encoding='utf8').write(pres)
    open(os.path.join(tmp, 'ppt/_rels/presentation.xml.rels'), 'w', encoding='utf8').write(rels)
    open(os.path.join(tmp, '[Content_Types].xml'), 'w', encoding='utf8').write(ct)
    if os.path.exists(dst): os.remove(dst)
    with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as zo:
        names = [n for n in z.namelist() if n != '[Content_Types].xml']
        extra = [f'ppt/slides/slide{k}.xml' for k in new] + [f'ppt/slides/_rels/slide{k}.xml.rels' for k in new]
        for nm in ['[Content_Types].xml'] + names + extra:
            zo.write(os.path.join(tmp, nm), nm)
    print('done; problems:', BAD if BAD else 0)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
