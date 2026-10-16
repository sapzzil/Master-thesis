# -*- coding: utf-8 -*-
"""차례·표 차례·그림 차례 채우기: docx를 LibreOffice로 열어 목차 필드를 갱신해 항목과 쪽 번호를 얻고,
그 내용을 docx의 목차 필드 결과 자리에 미리 써 넣는다(Word가 필드를 갱신하지 않아도 차례가 보이도록).
Word에서 '필드 업데이트'를 하면 Word 기준 쪽 번호로 다시 맞춰진다.
사용: python3 toc_fill.py 대상.docx [확인용.pdf]"""
import sys, time, subprocess, zipfile, shutil, re, os, tempfile
from xml.sax.saxutils import escape

def lo_entries(docx, pdf=None):
    import uno
    from com.sun.star.beans import PropertyValue
    def P(n, v):
        p = PropertyValue(); p.Name = n; p.Value = v; return p
    port = 2002 + os.getpid() % 500
    proc = subprocess.Popen(["soffice", "--headless", "--invisible", "--norestore", f"--accept=socket,host=localhost,port={port};urp;"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    ctx = None
    for _ in range(90):
        try:
            lc = uno.getComponentContext()
            res = lc.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", lc)
            ctx = res.resolve(f"uno:socket,host=localhost,port={port};urp;StarOffice.ComponentContext"); break
        except Exception: time.sleep(1)
    desk = ctx.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
    doc = desk.loadComponentFromURL(uno.systemPathToFileUrl(os.path.abspath(docx)), "_blank", 0, (P("Hidden", True),))
    idx = doc.getDocumentIndexes()
    for _ in range(2):
        for i in range(idx.getCount()): idx.getByIndex(i).update()
    out = [idx.getByIndex(i).getAnchor().getString() for i in range(idx.getCount())]
    if pdf: doc.storeToURL(uno.systemPathToFileUrl(os.path.abspath(pdf)), (P("FilterName", "writer_pdf_Export"),))
    doc.close(True); proc.terminate()
    return out

def level(t):
    if re.match(r"^\d+\.\d+\.\d+", t): return 3
    if re.match(r"^[A-Z]\.\d+", t): return 3  # 부록 A.1 등은 한 단계 더 들여씀
    if re.match(r"^\d+\.\d+", t): return 2
    return 1

def para(title, page, lvl, width, plain=False):
    ind = {1: 0, 2: 300, 3: 600}[lvl]
    font = '<w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="바탕" w:cs="Times New Roman"/><w:sz w:val="21"/><w:szCs w:val="21"/>'
    b = "<w:b/>" if lvl == 1 and not plain else ""
    return (f'<w:p><w:pPr><w:tabs><w:tab w:val="right" w:leader="dot" w:pos="{width}"/></w:tabs>'
            f'<w:spacing w:before="{160 if (lvl == 1 and not plain) else 0}" w:after="{20 if plain else 40}" w:line="{264 if plain else 300}" w:lineRule="auto"/><w:ind w:left="{ind}" w:right="400" w:hanging="0"/></w:pPr>'
            f'<w:r><w:rPr>{font}{b}</w:rPr><w:t xml:space="preserve">{escape(title)}</w:t></w:r>'
            f'<w:r><w:rPr>{font}</w:rPr><w:tab/><w:t>{escape(page)}</w:t></w:r></w:p>')

def fill(docx, texts):
    tmp = tempfile.mkdtemp()
    with zipfile.ZipFile(docx) as z: z.extractall(tmp)
    dp = os.path.join(tmp, "word/document.xml")
    s = open(dp, encoding="utf-8").read()
    m = re.search(r'<w:pgSz w:w="(\d+)"[^>]*/><w:pgMar w:top="\d+" w:right="(\d+)"[^>]*w:left="(\d+)"', s)
    width = int(m.group(1)) - int(m.group(2)) - int(m.group(3))
    parts = s.split('<w:fldChar w:fldCharType="separate"/></w:r></w:p>')
    assert len(parts) - 1 == len(texts), (len(parts) - 1, len(texts))
    outp = [parts[0]]
    for k, t in enumerate(texts):
        ents = []
        for line in t.split("\n"):
            if "\t" not in line: continue
            title, page = line.rsplit("\t", 1)
            # k = 0: 차례(장·절 단계별 들여쓰기), 1·2: 표·그림 차례(한 단계, 보통 굵기)
            ents.append(para(title.strip(), page.strip(), 1 if k else level(title.strip()), width, plain=k > 0))
        outp.append('<w:fldChar w:fldCharType="separate"/></w:r></w:p>' + "".join(ents) + parts[k + 1])
    open(dp, "w", encoding="utf-8").write("".join(outp))
    out = docx + ".tmp"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(tmp):
            for f in files:
                full = os.path.join(root, f); z.write(full, os.path.relpath(full, tmp))
    shutil.move(out, docx); shutil.rmtree(tmp)

if __name__ == "__main__":
    d = sys.argv[1]; pdf = sys.argv[2] if len(sys.argv) > 2 else None
    texts = lo_entries(d, None)
    fill(d, texts)
    print("toc filled:", [t.count("\n") + 1 for t in texts])
    if pdf: lo_entries(d, pdf)
