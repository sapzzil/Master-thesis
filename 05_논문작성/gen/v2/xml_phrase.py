"""docx 문단 안에서 여러 run에 걸친 구절을 찾아 바꾼다(첫 run의 서식 유지).
NBSP(\xa0)는 일반 공백과 같은 것으로 보고 찾는다."""
import re

def _runs(p):
    # (start, end, text) for each <w:t>
    out = []
    for m in re.finditer(r'(<w:t(?: [^>]*)?>)([^<]*)(</w:t>)', p):
        out.append(m)
    return out

def replace_in_para(p, old, new, cond=None, maxn=100):
    """p: <w:p> xml. 모든 등장을 바꾼다. 반환 (새 xml, 횟수)"""
    n = 0
    while True:
        ms = _runs(p)
        texts = [m.group(2) for m in ms]
        full = ''.join(texts)
        norm = full.replace('\xa0', ' ')
        i = norm.find(old.replace('\xa0', ' '))
        if i < 0 or n >= maxn or (cond and not cond(full)):
            return p, n
        j = i + len(old)
        # locate runs
        pos = 0; first = last = None; fo = lo = 0
        for k, t in enumerate(texts):
            if first is None and i < pos + len(t) or (first is None and i == pos + len(t) and len(t) == 0 and False):
                first, fo = k, i - pos
            if first is not None and j <= pos + len(t):
                last, lo = k, j - pos
                break
            pos += len(t)
        if first is None or last is None:
            return p, n
        newt = list(texts)
        if first == last:
            newt[first] = texts[first][:fo] + new + texts[first][lo:]
        else:
            newt[first] = texts[first][:fo] + new
            for k in range(first + 1, last):
                newt[k] = ''
            newt[last] = texts[last][lo:]
        # rebuild
        out = []; prev = 0
        for k, m in enumerate(ms):
            out.append(p[prev:m.start()])
            tag = m.group(1)
            if newt[k] != newt[k].strip() and 'xml:space' not in tag:
                tag = tag.replace('<w:t', '<w:t xml:space="preserve"', 1)
            out.append(tag + newt[k] + m.group(3))
            prev = m.end()
        out.append(p[prev:])
        p = ''.join(out); n += 1

def para_text(p):
    return ''.join(m.group(2) for m in _runs(p))
