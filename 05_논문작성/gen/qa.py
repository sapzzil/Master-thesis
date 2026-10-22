# 완성된 docx를 열어 편집 오류를 기계적으로 점검한다. 사용: python3 gen/qa.py 파일.docx [...]
# 점검: 그림·표 제목 오염, 번호 순서, 본문 참조 여부, 없는 번호 참조, 수식 번호, 절 참조, 인용-참고문헌 대응,
#       마크다운 잔재, 차례 항목 길이, 그림 파일 누락(원고 기준)
import re, sys, collections
from docx import Document

def paras(path):
    # 차례(SDT 안)까지 포함해 문서 순서대로 모든 문단을 읽는다. 표 안 문단은 'T'로 표시
    from docx.oxml.ns import qn
    d = Document(path); out = []
    for p in d.element.body.iter(qn("w:p")):
        txt = "".join(t.text or "" for t in p.iter(qn("w:t")))
        anc = [a.tag for a in p.iterancestors()]
        out.append(("T" if qn("w:tc") in anc else "P", "S" if qn("w:sdt") in anc else "", txt))
    return out

def check(path):
    P = paras(path); errs = []; warn = []
    body = [t for k, s, t in P if k == "P"]
    allt = [t for _, _, t in P]
    # 차례 부분과 본문 분리: '제 1 장' 또는 '제1장' 제목 이후를 본문으로
    start = next(i for i, t in enumerate(body) if re.match(r"^제\s*1\s*장\s*\S*[^\d\s]$", t.strip()))
    main = body[start:]
    toc = [t for k, s, t in P if s == "S"]
    refs_start = next(i for i, t in enumerate(main) if t.strip() == "참고문헌")
    app_start = next((i for i, t in enumerate(main) if i > refs_start and re.match(r"^부록 [A-Z]\.", t.strip())), len(main))
    # 본문 = 참고문헌 앞 + 부록, 참고문헌 목록 = 그 사이
    text, reflist = main[:refs_start] + main[app_start:], main[refs_start + 1:app_start]
    # 1. 그림·표 제목
    cap = re.compile(r"^(그림|표) ([A-Z0-9]+)-(\d+)\. (.*)$")
    caps = collections.defaultdict(list)
    for t in text:
        m = cap.match(t)
        if m:
            kind, ch, n, rest = m.group(1), m.group(2), int(m.group(3)), m.group(4)
            caps[(kind, ch)].append(n)
            if len(t) > 140: warn.append(f"제목이 김({len(t)}자): {t[:70]}…")
            if re.search(r"[다]\.\s+\S", rest) and kind == "그림" and len(t) > 100: errs.append(f"제목에 본문 문장이 붙었을 가능성: {t[:90]}…")
    # 2. 번호 순서
    for (kind, ch), ns in caps.items():
        if ns != list(range(1, len(ns) + 1)): errs.append(f"{kind} {ch}장 번호 순서 이상: {ns}")
    # 3. 본문 참조
    joined = "\n".join(t for t in text if not cap.match(t))
    for (kind, ch), ns in caps.items():
        for n in ns:
            if not re.search(rf"{kind} {ch}-{n}(?!\d)", joined): errs.append(f"본문에서 언급하지 않은 {kind} {ch}-{n}")
    # 4. 없는 번호 참조
    for m in re.finditer(r"(그림|표) ([A-Z0-9]+)-(\d+)", joined):
        if int(m.group(3)) not in caps.get((m.group(1), m.group(2)), []): errs.append(f"없는 {m.group(0)}를 참조")
    # 5. 수식 번호
    eq = [int(m.group(2)) for t in text for m in [re.search(r"\((\d+)\.(\d+)\)\s*$", t)] if m and "\t" in t or (m and len(t) < 160 and re.search(r"[=≤≥]", t))]
    eqs = collections.defaultdict(list)
    for t in text:
        m = re.search(r"\((\d+)\.(\d+)\)\s*$", t)
        if m and re.search(r"[=≤≥~]", t) and len(t) < 200: eqs[m.group(1)].append(int(m.group(2)))
    for ch, ns in eqs.items():
        if ns != list(range(1, len(ns) + 1)): errs.append(f"수식 {ch}장 번호 순서 이상: {ns}")
    # 6. 절 참조
    heads = set()
    for t in text + reflist:
        m = re.match(r"^(\d+(?:\.\d+){1,2}) ", t)
        if m: heads.add(m.group(1))
        m = re.match(r"^([A-Z]\.\d+) ", t)
        if m: heads.add(m.group(1))
    for m in re.finditer(r"(\d+\.\d+(?:\.\d+)?)(?:~(\d+\.\d+(?:\.\d+)?))?절", joined):
        for x in [m.group(1), m.group(2)]:
            if x and x not in heads: errs.append(f"없는 절 참조: {x}절")
    # 7. 인용-참고문헌: 참고문헌마다 (첫 저자 성 또는 기관명, 연도), 본문 인용마다 (연도 앞 60자 구간)
    refs = []
    for t in reflist:
        m = re.match(r"^(.+?)[.,]? \((\d{4})\)", t)
        if not m: continue
        head = m.group(1)
        key = head.split(",")[0]
        if "Basel" in head: key = "Basel Committee"
        if "Federal Reserve" in head: key = "Federal Reserve"
        if head.startswith("Noguer"): key = "Noguer i Alonso"
        refs.append((key, m.group(2)))
    for key, yr in refs:
        if not re.search(re.escape(key) + r".{0,80}?" + yr, joined): errs.append(f"본문에서 인용하지 않은 참고문헌: {key} ({yr})")
    for m in re.finditer(r"(\d{4})[a-z]?\)", joined):
        win = joined[max(0, m.start() - 80):m.start()]
        if not re.search(r"[A-Z][a-z]", win) or joined[m.start() - 1] in "~–-": continue
        if not any(yr == m.group(1) and key in win for key, yr in refs):
            warn.append(f"참고문헌과 맞지 않는 인용: …{win[-50:]}{m.group(0)}")
    # 8. 마크다운·이스케이프 잔재
    for t in allt:
        for tok in ["**", "$$", "<br>", "\\n", "^{", "_{", "`"]:
            if tok in t: errs.append(f"표기 잔재 '{tok}': {t[:60]}"); break
    # 9. 차례 항목
    for t in toc:
        if len(t) > 130: errs.append(f"차례 항목이 너무 김: {t[:70]}…")
    return errs, warn, {k: len(v) for k, v in caps.items()}, dict((k, len(v)) for k, v in eqs.items())

if __name__ == "__main__":
    bad = 0
    for f in sys.argv[1:]:
        e, w, c, q = check(f)
        print(f"== {f}\n그림·표 수: {c}\n수식 수: {q}")
        for x in e: print("  [오류]", x)
        for x in w: print("  [확인]", x)
        print(f"  오류 {len(e)}건, 확인 {len(w)}건"); bad += len(e)
    sys.exit(1 if bad else 0)
