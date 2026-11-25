import zipfile,re,html,sys
S=sys.argv[1]
z=zipfile.ZipFile(S+'/dB.docx'); infos=z.infolist(); files={i.filename:z.read(i.filename) for i in infos}; z.close()
x=files['word/document.xml'].decode()
def ptext(p): return html.unescape(''.join(re.findall(r'<w:t(?: [^>]*)?>([^<]*)</w:t>',p))).replace('\xa0',' ').strip()
P=re.compile(r'<w:p[ >](?:(?!</w:p>).)*?</w:p>',re.S)
rep={'① 로그수익률':'로그수익률','② 가격 그대로':'가격 그대로','① 군집 α+β':'군집 α+β','② 꼬리 ν':'꼬리 ν','③ 전환 빈도':'전환 빈도','④ 전환 크기: 변동비':'전환 크기: 변동비',
     '0.946 (한국전력)':'0.946','0.982 (중앙값)':'0.982','4.39 (중앙값)':'4.39','35.6 / 7.6 (중앙값)':'35.6 / 7.6','2.70 (중앙값)':'2.70','0.996 (GOOG)':'0.996','3.56 (META)':'3.56','3.19 (삼성전자)':'3.19','꼬리 L2~L5의 ±3σ 초과일 비율':'꼬리 L2~L5의 ±3σ 초과일 비율(%)','0.676 / 0.879 / 1.264 / 1.379% (이론)':'0.676 / 0.879 / 1.264 / 1.379 (이론)','0.663 / 0.877 / 1.268 / 1.386%':'0.663 / 0.877 / 1.268 / 1.386','폭 배율(연속)':'폭 배율 (연속)'}
delete={'(SK하이닉스)','(최대 이탈확률×2)'}
cnt={};dcnt={}
def fix(m):
    p=m.group(0); t=ptext(p)
    if t in rep:
        cnt[t]=cnt.get(t,0)+1
        runs=re.findall(r'<w:r(?: [^>]*)?>.*?</w:r>',p,re.S)
        rpr=re.search(r'<w:rPr>.*?</w:rPr>',runs[0],re.S); rpr=rpr.group(0) if rpr else ''
        head=p[:p.find(runs[0])]; tail=p[p.rfind(runs[-1])+len(runs[-1]):]
        return head+f'<w:r>{rpr}<w:t xml:space="preserve">{rep[t]}</w:t></w:r>'+tail
    if t in delete:
        dcnt[t]=dcnt.get(t,0)+1; return ''
    return p
x=P.sub(fix,x)
print('rep',cnt,'del',dcnt)
missing=[k for k in rep if k not in cnt]; print('missing',missing)
files['word/document.xml']=x.encode()
out=zipfile.ZipFile(S+'/dC.docx','w',zipfile.ZIP_DEFLATED)
for i in infos: out.writestr(i,files[i.filename])
out.close()
