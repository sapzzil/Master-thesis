"""새 원고의 숫자가 옛 원고 어딘가에 있는지 확인. usage: nums.py old_dir new_dir [file]"""
import sys,re,glob,os
old,new=sys.argv[1:3]; only=sys.argv[3] if len(sys.argv)>3 else None
def toks(s):
    s=s.replace('−','-')
    return set(re.findall(r'\d+(?:[.,]\d+)*(?:~\d+(?:\.\d+)?)?',s))
O=set();[O.update(toks(open(f,encoding='utf-8').read())) for f in glob.glob(old+'/*.md')]
# 옛 원고의 개별 숫자도 허용(범위 끝값 등)
O2=set(); [O2.update(re.findall(r'\d+(?:\.\d+)?',t)) for t in O]
bad=0
for f in sorted(glob.glob(new+'/*.md')):
    if only and only not in f: continue
    for t in sorted(toks(open(f,encoding='utf-8').read())-O):
        parts=re.findall(r'\d+(?:\.\d+)?',t)
        if all(p in O2 for p in parts) and '~' not in t: continue
        print(os.path.basename(f),t); bad+=1
print('new numbers:',bad)
