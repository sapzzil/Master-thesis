# 비교용 '기초 설명 포함' 초고를 만든다. 2장만 gen/variants/03_제2장_기초포함.md로 바꿔 끼워 docx를 만들고, 원래 2장 파일은 되돌린다.
# 먼저 gen/build.py를 실행해 4~6장 원고가 최신인 상태에서 쓴다.
import shutil, subprocess, pathlib
V = pathlib.Path(__file__).resolve().parents[1]
CH2 = V / "03_제2장_관련연구_v4.md"
VAR = V / "gen/variants/03_제2장_기초포함.md"
OUT = "석사학위논문_초고_김승민_기초포함.docx"
bak = CH2.read_bytes()
try:
    shutil.copyfile(VAR, CH2)
    subprocess.run(["node", str(V / "gen/make_docx.js"), OUT], check=True)
    subprocess.run(["python3", str(V / "gen/postfix.py"), str(V / OUT)], check=True)
    subprocess.run(["python3", str(V / "gen/toc_fill.py"), str(V / OUT)], check=True, timeout=300)
finally:
    CH2.write_bytes(bak)
print("ok", OUT)
