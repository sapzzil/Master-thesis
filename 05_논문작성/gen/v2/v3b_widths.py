import zipfile,re,html,sys
S=sys.argv[1]
z=zipfile.ZipFile(S+'/dC.docx'); infos=z.infolist(); files={i.filename:z.read(i.filename) for i in infos}; z.close()
x=files['word/document.xml'].decode()
def txt(s): return html.unescape(''.join(re.findall(r'<w:t(?: [^>]*)?>([^<]*)</w:t>',s)))
W={'표 2-1.':[28,24,29,30,14,14],'표 3-1.':[22,46,73],'표 3-3.':[12,30,26,36,36],'표 3-4.':[51,44,44],'표 3-6.':[18,60,47,16],
   '표 3-7.':[16,11,42,36,36],'표 4-4.':[32,32,32,22,22],'표 4-5.':[19,20,10,10,13,13,10,13,13,20],'표 5-4.':[20,23,18,18,11,18,15,18],
   '표 6-2.':[21,23,13,27,11,14,14,17],'표 7-1.':[22,33,56,29],'표 A-2.':[33,38,22,48]}
done=set(); out=[]; last=0
for m in re.finditer(r'<w:tbl>.*?</w:tbl>',x,re.S):
    t=m.group(0)
    caps=re.findall(r'(표 [0-9A-C]-\d+\.)',txt(x[max(0,m.start()-4000):m.start()]))
    cap=caps[-1] if caps else None
    if cap in W and cap not in done:
        grid=[int(g) for g in re.findall(r'<w:gridCol w:w="(\d+)"',t)]
        new=W[cap]; tot=sum(grid); assert len(new)==len(grid),(cap,len(grid))
        nw=[round(v/sum(new)*tot) for v in new]; nw[-1]+=tot-sum(nw)
        t2=re.sub(r'<w:tblGrid>.*?</w:tblGrid>','<w:tblGrid>'+''.join(f'<w:gridCol w:w="{v}"/>' for v in nw)+'</w:tblGrid>',t,flags=re.S)
        def row(rm):
            r=rm.group(0); ci=[0]
            def cell(cm):
                c=cm.group(0); sp=re.search(r'<w:gridSpan w:val="(\d+)"',c); sp=int(sp.group(1)) if sp else 1
                w=sum(nw[ci[0]:ci[0]+sp]); ci[0]+=sp
                return re.sub(r'<w:tcW w:w="\d+" w:type="dxa"/>',f'<w:tcW w:w="{w}" w:type="dxa"/>',c,count=1)
            return re.sub(r'<w:tc>.*?</w:tc>',cell,r,flags=re.S)
        t2=re.sub(r'<w:tr[ >].*?</w:tr>',row,t2,flags=re.S)
        out.append(x[last:m.start()]+t2); last=m.end(); done.add(cap)
x=''.join(out)+x[last:]
print('resized',sorted(done), 'missing',set(W)-done)
# NBSP for "한 달" in table cells only
def nb(m):
    return m.group(0).replace('한 달','한 달')
x=re.sub(r'<w:tbl>.*?</w:tbl>',nb,x,flags=re.S)
# subscript tau: split runs containing "_τ"
def subfix(m):
    r=m.group(0)
    if '_τ' not in r: return r
    rpr=re.search(r'<w:rPr>(.*?)</w:rPr>',r,re.S); inner=rpr.group(1) if rpr else ''
    tm=re.search(r'<w:t(?: [^>]*)?>([^<]*)</w:t>',r); s=tm.group(1)
    parts=s.split('_τ'); res=''
    def run(text,sub=False):
        ii=inner+('<w:vertAlign w:val="subscript"/>' if sub else '')
        return f'<w:r>{"<w:rPr>"+ii+"</w:rPr>" if ii else ""}<w:t xml:space="preserve">{text}</w:t></w:r>'
    for k,pt in enumerate(parts):
        if pt: res+=run(pt)
        if k<len(parts)-1: res+=run('τ',True)
    return res
before=x.count('_τ'); x=re.sub(r'<w:r(?: [^>]*)?>(?:(?!</w:r>).)*?</w:r>',subfix,x,flags=re.S); print('subscript tau',before,'->',x.count('_τ'))
files['word/document.xml']=x.encode()
o=zipfile.ZipFile(S+'/dD.docx','w',zipfile.ZIP_DEFLATED)
for i in infos: o.writestr(i,files[i.filename])
o.close()
