# -*- coding: utf-8 -*-
"""docx 후처리: 어절 단위 줄바꿈을 명시적으로 켬.
w:wordWrap은 'Latin(Word 한글판에서는 한글 포함) 단어를 줄 끝에서 글자 단위로 쪼갤지'를 정하는 속성으로,
값이 0(off)이면 단어 중간에서 쪼개고(=Word의 '한글 단어 잘림 허용' 체크), 1(on)이면 단어 단위로 넘긴다.
docx 생성 라이브러리는 0만 쓸 수 있어, 생성 후 1로 바꾼다.
사용: python3 postfix.py 파일.docx [...]"""
import sys, zipfile, os, shutil, tempfile

def fix(path):
    tmp = tempfile.mkdtemp()
    with zipfile.ZipFile(path) as z: z.extractall(tmp); names = z.namelist()
    n = 0
    for part in ["word/document.xml", "word/styles.xml"]:
        p = os.path.join(tmp, part)
        s = open(p, encoding="utf-8").read()
        n += s.count('<w:wordWrap w:val="0"/>')
        s = s.replace('<w:wordWrap w:val="0"/>', '<w:wordWrap w:val="1"/>')
        open(p, "w", encoding="utf-8").write(s)
    out = path + ".tmp"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for nm in names: z.write(os.path.join(tmp, nm), nm)
    shutil.move(out, path); shutil.rmtree(tmp)
    print("wordWrap on:", path, n)

for f in sys.argv[1:]: fix(f)
