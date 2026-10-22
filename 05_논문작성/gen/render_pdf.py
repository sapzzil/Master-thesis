# 확인용: docx를 LibreOffice로 열어 차례·표 차례·그림 차례 필드를 갱신한 뒤 PDF로 저장
# 사용: python3 render_pdf.py 입력.docx 출력.pdf
import uno,sys,time,subprocess
from com.sun.star.beans import PropertyValue
def P(n,v):
    p=PropertyValue();p.Name=n;p.Value=v;return p
proc=subprocess.Popen(['soffice','--headless','--invisible','--norestore','--accept=socket,host=localhost,port=2002;urp;'])
ctx=None
for _ in range(60):
    try:
        lc=uno.getComponentContext()
        res=lc.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver",lc)
        ctx=res.resolve("uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext");break
    except Exception: time.sleep(1)
desk=ctx.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop",ctx)
doc=desk.loadComponentFromURL(uno.systemPathToFileUrl(sys.argv[1]),"_blank",0,(P("Hidden",True),))
idx=doc.getDocumentIndexes(); print("indexes",idx.getCount())
for _ in range(2):
    for i in range(idx.getCount()): idx.getByIndex(i).update()
doc.storeToURL(uno.systemPathToFileUrl(sys.argv[2]),(P("FilterName","writer_pdf_Export"),))
doc.close(True); proc.terminate()
