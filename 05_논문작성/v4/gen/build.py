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
tabs["TABE1"] = "**표 5-4. 방향 매매 결과 (10종목 동일비중 포트폴리오)**\n\n| 전략 | 조건 | 연수익률 % (비용 반영) | 연수익률 % (비용 0) | 샤프 | 최대 낙폭 % | 평균 비중 | 연 회전율(배) |\n|---|---|---|---|---|---|---|---|\n" + "\n".join(rows)
e2 = pd.read_csv(E / "E2_voltarget.csv"); rows = []
for n in sorted(e2["전략"].unique(), key=key):
    g = e2[e2["전략"] == n].set_index("구간"); m, c = split(n)
    if n == "계속 보유":
        r = g.iloc[0]; rows.append(f"| 계속 보유 | - | {r['샤프']:.2f} | | {r['최대낙폭%']:.1f} | | {r['실현변동/목표']:.2f} | | |"); continue
    o, k = g.loc["원래"], g.loc["보정"]
    def d(r):
        if pd.isna(r["샤프차_vsRW"]): return "기준"
        s = f"{r['샤프차_vsRW']:+.2f} [{r['차_lo']:+.2f}, {r['차_hi']:+.2f}]"
        return s + (" ✕" if r["차_hi"] < 0 else (" ○" if r["차_lo"] > 0 else ""))
    rows.append(f"| {m} | {c} | {o['샤프']:.2f} | {k['샤프']:.2f} | {o['최대낙폭%']:.1f} | {k['최대낙폭%']:.1f} | {o['실현변동/목표']:.2f} | {k['실현변동/목표']:.2f} | {d(o)} / {d(k)} |")
tabs["TABE2"] = "**표 5-5. 비중 조절(변동성 목표 1%) 결과 (비용 반영)**\n\n| 전략 | 조건 | 샤프 (원래) | 샤프 (보정) | 최대 낙폭 % (원래) | 최대 낙폭 % (보정) | 실현변동/목표 (원래) | 실현변동/목표 (보정) | RW 대비 샤프 차 [95% 구간] (원래 / 보정) |\n|---|---|---|---|---|---|---|---|---|\n" + "\n".join(rows) + "\n\n주: RW 대비는 같은 과거 길이의 RW 구간을 쓴 같은 전략과 비교(달력 월 블록 부트스트랩 2,000회). ✕ = 95% 구간이 0보다 작음(RW보다 나쁨), ○ = 0보다 큼(해당 없음). 계속 보유의 실현변동/목표는 참고값."
e3 = pd.read_csv(E / "E3_var.csv"); rows = []
for n in sorted(e3["모델·조건"].unique(), key=key):
    g = e3[e3["모델·조건"] == n].set_index("구간"); m, c = split(n); o, k = g.loc["원래"], g.loc["보정"]
    rows.append(f"| {m} | {c} | {o['위반율%']:.1f} → {k['위반율%']:.1f} | {int(o['Kupiec통과(10종목중)'])} → {int(k['Kupiec통과(10종목중)'])} | {int(o['독립성통과(10종목중)'])} → {int(k['독립성통과(10종목중)'])} |")
tabs["TABE3"] = "**표 5-6. 위험 한도(VaR 10%) 백테스트 (보정 전 → 보정 후)**\n\n| 모델 | 조건 | 위반율 % (목표 10) | 위반율 검정 통과 종목 (10개 중) | 독립성 검정 통과 종목 (10개 중) |\n|---|---|---|---|---|\n" + "\n".join(rows)
for t, out in [("05_제4장_template.md", "05_제4장_금융특성의_영향_v4.md"), ("06_제5장_template.md", "06_제5장_실증평가_v4.md"), ("07_제6장_template.md", "07_제6장_사후보정_v4.md")]:
    s = (V / "gen/templates" / t).read_text(encoding="utf-8")
    for k2, v in tabs.items(): s = s.replace("{{" + k2 + "}}", v)
    assert "{{" not in s, re.findall(r"\{\{\w+\}\}", s)
    (V / out).write_text(s, encoding="utf-8")
order = ["01_초록_및_목차_v4.md", "02_제1장_서론_v4.md", "03_제2장_관련연구_v4.md", "04_제3장_연구설계_v4.md", "05_제4장_금융특성의_영향_v4.md",
         "06_제5장_실증평가_v4.md", "07_제6장_사후보정_v4.md", "08_제7장_결론_v4.md", "09_참고문헌_v4.md", "10_부록A_실험절차이력_v4.md"]
full = "\n\n---\n\n".join((V / f).read_text(encoding="utf-8").strip() for f in order) + "\n"
(V / "00_학위논문_초고_통합본_v4.md").write_text(full, encoding="utf-8")
try:
    subprocess.run(["pandoc", "00_학위논문_초고_통합본_v4.md", "-f", "markdown-yaml_metadata_block", "-o", "00_학위논문_초고_통합본_v4.docx"], cwd=V, check=True)
    subprocess.run(["pandoc", "지도교수_요약본_v4.md", "-f", "markdown-yaml_metadata_block", "-o", "지도교수_요약본_v4.docx"], cwd=V, check=True)
except Exception as ex: print("docx 생략:", ex)
print("ok")
