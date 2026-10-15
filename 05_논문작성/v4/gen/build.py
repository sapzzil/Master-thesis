# -*- coding: utf-8 -*-
"""v4 초고 빌드: (1) 4~6장 템플릿의 {{표}} 자리에 gen/tables.md·경제 분석 표를 채워 05~07 파일 생성
(2) 01~10 파일을 이어 붙여 00_학위논문_초고_통합본_v4.md 생성 (3) pandoc 있으면 docx 생성.
사용: python 05_논문작성/v4/gen/build.py   (표를 다시 만들려면 먼저 gen/tables.py 실행)"""
import re, subprocess, pathlib, pandas as pd
V = pathlib.Path(__file__).resolve().parents[1]; R = V.parents[1]
E = R / "04_실험코드/results_v4_econ"
tabs = {}
for blk in (V / "gen/tables.md").read_text(encoding="utf-8").split("\n\n"):
    k, v = blk.split("\n", 1); tabs[k.strip()] = v
NMO = ["Chronos-T5", "Chronos-2", "TimesFM-2.5", "Moirai-2", "과거변동(RW)", "GARCH-t"]
def key(n):
    m = [i for i, x in enumerate(NMO) if n.startswith(x)]
    return (m[0] if m else -1, 0 if "한 달" in n else 1, 0 if "수익률" in n else 1)
def split(n):
    for x in NMO:
        if n.startswith(x): return x, n[len(x) + 1:]
    return n, "-"
e1 = pd.read_csv(E / "E1_direction.csv"); a = e1[e1["비용"] == "있음"].set_index("전략"); b = e1[e1["비용"] == "없음"].set_index("전략")
rows = []
for n in sorted(a.index, key=key):
    r = a.loc[n]; m, c = split(n)
    rows.append(f"| {m} | {c} | {r['연수익률%']:.1f} | {b.loc[n,'연수익률%']:.1f} | {r['샤프']:.2f} | {r['최대낙폭%']:.1f} | {r['평균비중']:.2f} | {r['연회전율']:.0f} |")
tabs["TABE1"] = "**표 5-4. 방향 매매 결과 (10종목 동일비중 포트폴리오)**\n\n| 전략 | 조건 | 연수익률(%)<br>(비용 반영) | 연수익률(%)<br>(비용 제외) | 샤프 | 최대낙폭(%) | 평균 비중 | 연회전율(배) |\n|---|---|---|---|---|---|---|---|\n" + "\n".join(rows)
e2 = pd.read_csv(E / "E2_voltarget.csv"); rows = []
for n in sorted(e2["전략"].unique(), key=key):
    g = e2[e2["전략"] == n].set_index("구간"); m, c = split(n)
    if n == "계속 보유":
        r = g.iloc[0]; rows.append(f"| 계속 보유 | - | {r['샤프']:.2f} | {r['최대낙폭%']:.1f} | {r['실현변동/목표']:.2f} | - |"); continue
    o, k = g.loc["원래"], g.loc["보정"]
    if pd.isna(k["샤프차_vsRW"]): d = "비교 기준(한 달)" if "한 달" in c else "비교 기준(1년)"
    else:
        d = f"{k['샤프차_vsRW']:+.2f} [{k['차_lo']:+.2f}, {k['차_hi']:+.2f}]" + (" ✕" if k["차_hi"] < 0 else (" ○" if k["차_lo"] > 0 else ""))
    rows.append(f"| {m} | {c} | {o['샤프']:.2f} / {k['샤프']:.2f} | {o['최대낙폭%']:.1f} / {k['최대낙폭%']:.1f} | {o['실현변동/목표']:.2f} / {k['실현변동/목표']:.2f} | {d} |")
tabs["TABE2"] = "**표 5-5. 비중 조절(변동성 목표 1%) 결과 (비용 반영, 원래 구간 / 보정 구간)**\n\n| 전략 | 조건 | 샤프 | 최대낙폭(%) | 실현변동/목표 | RW 대비 샤프 차(보정) [95% 구간] |\n|---|---|---|---|---|---|\n" + "\n".join(rows) + "\n\n주: 각 칸은 '원래 구간 / 보정 구간'. RW 대비는 같은 과거 길이의 RW 보정 구간을 쓴 같은 전략과 비교(달력 월 블록 부트스트랩 2,000회). ✕ = 95% 구간이 0보다 작음(RW보다 낮음), ○ = 0보다 큼(해당 없음). 원래 구간끼리의 비교에서 유의하게 낮은 경우는 Chronos-T5 한 달·가격 1건이다. 계속 보유의 실현변동/목표는 참고값."
e3 = pd.read_csv(E / "E3_var.csv"); rows = []
for n in sorted(e3["모델·조건"].unique(), key=key):
    g = e3[e3["모델·조건"] == n].set_index("구간"); m, c = split(n); o, k = g.loc["원래"], g.loc["보정"]
    rows.append(f"| {m} | {c} | {o['위반율%']:.1f} → {k['위반율%']:.1f} | {int(o['Kupiec통과(10종목중)'])} → {int(k['Kupiec통과(10종목중)'])} | {int(o['독립성통과(10종목중)'])} → {int(k['독립성통과(10종목중)'])} |")
tabs["TABE3"] = "**표 5-6. 위험 한도(VaR 10%) 백테스트 (보정 전 → 보정 후)**\n\n| 모델 | 조건 | 위반율(%)<br>(목표 10%) | 위반율 검정 통과<br>(종목 수) | 독립성 검정 통과<br>(종목 수) |\n|---|---|---|---|---|\n" + "\n".join(rows) + "\n\n주: 검정 통과 종목 수는 10개 종목 중 유의수준 5%에서 기각되지 않은 종목의 수. 위반율 검정은 Kupiec, 독립성 검정은 Christoffersen."
for t, out in [("05_제4장_template.md", "05_제4장_금융특성의_영향_v4.md"), ("06_제5장_template.md", "06_제5장_실증평가_v4.md"), ("07_제6장_template.md", "07_제6장_사후보정_v4.md")]:
    s = (V / "gen/templates" / t).read_text(encoding="utf-8")
    for k2, v in tabs.items(): s = s.replace("{{" + k2 + "}}", v)
    assert "{{" not in s, re.findall(r"\{\{\w+\}\}", s)
    (V / out).write_text(s, encoding="utf-8")

# 부록 B·C 생성
T = R / "04_실험코드/results_v4/tables"
NM = {"chronos_t5_base": "Chronos-T5", "chronos2": "Chronos-2", "timesfm25": "TimesFM-2.5", "moirai2": "Moirai-2", "rw": "과거변동(RW)", "garch_t": "GARCH-t"}
ORD = list(NM)
def lab(m, L, k): return f"{NM[m]} | {'한 달' if L == 21 else '1년'}·{'수익률' if k == 'return' else '가격'}"
t2 = pd.read_csv(T / "T2_H1_H3_levels.csv"); t2 = t2[t2.comparison == "L5-L3"].copy()
t2["_o"] = t2.model.map({m: i for i, m in enumerate(ORD)}); t2 = t2.sort_values(["_o", "L", "input"], ascending=[True, True, False])
rows = []
for (m, L, k), g in t2.groupby(["model", "L", "input"], sort=False):
    c = []
    for h in ["H1", "H2", "H3a", "H3b"]:
        r = g[g.hyp == h].iloc[0]; sym = ""
        if not pd.isna(r.p_holm) and r.p_holm < 0.05:
            sym = ("▼" if abs(r.dcov) >= 0.02 else "▽") if r.dcov < 0 else ("▲" if abs(r.dcov) >= 0.02 else "△")
        v = f"{100*r.dcov:+.1f}"; v = "0.0" if v in ("+0.0", "-0.0") else v  # 반올림 0.0은 부호 없이
        c.append(f"{v}{sym}")
    rows.append(f"| {lab(m, L, k)} | " + " | ".join(c) + " |")
B = ("# 부록 B. 특성 강도 비교(L5 − L3)\n\n제4장 표 4-2와 같은 방식으로, 각 특성을 실측 범위의 가장 약한 값(L3)에서 가장 강한 값(L5)으로 바꿨을 때의 커버리지 변화(%p)를 제시한다. "
     "표시는 표 4-2와 같다(▼▽ 가설 방향 유의, ▲△ 반대 방향 유의, 큰 기호는 2%p 이상, Holm 보정 16개 묶음). 기준 모형은 서술용이다.\n\n"
     "**표 B-1. 특성을 L3에서 L5로 강하게 설정했을 때의 커버리지 변화 (L5 − L3, %p)**\n\n| 모델 | 조건 | H1 군집 | H2 꼬리 | H3a 전환빈도 | H3b 전환크기 |\n|---|---|---|---|---|---|\n" + "\n".join(rows) + "\n\n주: 2%p 이상이지만 기호가 없는 칸(예: Chronos-2 1년·가격 H3a +2.4, Holm 보정 p = 0.060)은 보정 후 유의하지 않은 경우이다.")
(V / "11_부록B_특성강도비교_v4.md").write_text(B + "\n", encoding="utf-8")
c6 = pd.read_csv(T / "T6c_real_coverage_by_stock.csv"); c6["_o"] = c6.model.map({m: i for i, m in enumerate(ORD)})
c6 = c6.sort_values(["_o", "L", "input"], ascending=[True, True, False])
cols = ["AAPL", "AMZN", "GOOG", "JPM", "META", "005930", "000660", "005380", "015760", "012330"]
names = {"005930": "삼성전자", "000660": "SK하이닉스", "005380": "현대차", "015760": "한국전력", "012330": "현대모비스"}
# 12개 열을 한 표에 넣으면 글자가 너무 작아지므로 미국·한국 종목으로 나눔
def ctab(no, title, cs):
    rows = [f"| {lab(r.model, r.L, r.input)} | " + " | ".join(f"{100*r[c]:.1f}" for c in cs) + " |" for _, r in c6.iterrows()]
    return (f"**표 {no}. {title}**\n\n| 모델 | 조건 | " + " | ".join(names.get(c, c) for c in cs) + " |\n|---|---|" + "---|" * len(cs) + "\n" + "\n".join(rows))
C = ("# 부록 C. 종목별 실제 커버리지\n\n표 5-1의 보정 전 커버리지를 종목별로 구분하여 제시한다(%, 종목당 채점 1,740~1,800건). 표 C-1은 미국 5종목, 표 C-2는 한국 5종목이다.\n\n"
     + ctab("C-1", "미국 종목별 보정 전 커버리지 (%)", cols[:5]) + "\n\n" + ctab("C-2", "한국 종목별 보정 전 커버리지 (%)", cols[5:]))
(V / "12_부록C_종목별커버리지_v4.md").write_text(C + "\n", encoding="utf-8")
order = ["01_표지_차례_국문요지_v4.md", "02_제1장_서론_v4.md", "03_제2장_관련연구_v4.md", "04_제3장_연구설계_v4.md", "05_제4장_금융특성의_영향_v4.md",
         "06_제5장_실증평가_v4.md", "07_제6장_사후보정_v4.md", "08_제7장_결론_v4.md", "09_참고문헌_v4.md", "10_부록A_실험절차이력_v4.md", "11_부록B_특성강도비교_v4.md", "12_부록C_종목별커버리지_v4.md", "13_ABSTRACT_v4.md"]
full = "\n\n---\n\n".join((V / f).read_text(encoding="utf-8").strip() for f in order) + "\n"
(V / "00_학위논문_초고_통합본_v4.md").write_text(full, encoding="utf-8")
# 결과 docx는 작업용 번호·버전 없이 논문 파일 이름으로 같은 폴더에 둔다(초고 → 심사본 → 최종본으로 이어서 사용)
DOC_T = "석사학위논문_초고_김승민.docx"; DOC_S = "석사학위논문_초고_요약_김승민.docx"
try:
    subprocess.run(["node", str(V / "gen/make_docx.js"), DOC_T], check=True)
    subprocess.run(["node", str(V / "gen/make_docx.js"), "--plain", DOC_S, "지도교수_요약본_v4.md"], check=True)
    subprocess.run(["python3", str(V / "gen/postfix.py"), str(V / DOC_T), str(V / DOC_S)], check=True)
    # 차례·표 차례·그림 차례를 미리 채움(LibreOffice 필요). 없으면 Word에서 필드 업데이트로 채워짐
    try: subprocess.run(["python3", str(V / "gen/toc_fill.py"), str(V / DOC_T)], check=True, timeout=300)
    except Exception as ex: print("차례 채우기 생략:", ex)
except Exception as ex: print("docx 생략:", ex)
print("ok")
