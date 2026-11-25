"""pptx 슬라이드 XML에서 문단(<a:p>) 안의 구절을 run 경계와 관계없이 바꾼다(첫 run 서식 유지)."""
import re, html
PAR = r'<a:p>.*?</a:p>|<a:p [^>]*>.*?</a:p>'
RUN = r'(<a:t>)([^<]*)(</a:t>)'
def ptext(p): return html.unescape(''.join(m.group(2) for m in re.finditer(RUN, p)))
def replace_in_para(p, old, new, maxn=1):
    n = 0
    while n < maxn:
        ms = list(re.finditer(RUN, p)); texts = [html.unescape(m.group(2)) for m in ms]
        full = ''.join(texts); i = full.find(old)
        if i < 0: break
        j = i + len(old); pos = 0; first = last = None; fo = lo = 0
        for k, t in enumerate(texts):
            if first is None and i < pos + len(t): first, fo = k, i - pos
            if first is not None and j <= pos + len(t): last, lo = k, j - pos; break
            pos += len(t)
        newt = list(texts)
        if first == last: newt[first] = texts[first][:fo] + new + texts[first][lo:]
        else:
            newt[first] = texts[first][:fo] + new
            for k in range(first + 1, last): newt[k] = ''
            newt[last] = texts[last][lo:]
        out = []; prev = 0
        for k, m in enumerate(ms):
            out.append(p[prev:m.start()]); out.append(m.group(1) + html.escape(newt[k], quote=False) + m.group(3)); prev = m.end()
        out.append(p[prev:]); p = ''.join(out); n += 1
    return p, n
def replace_in_xml(x, old, new, maxn=1):
    out = []; prev = 0; total = 0
    for m in re.finditer(PAR, x, flags=re.S):
        pp, k = replace_in_para(m.group(0), old, new, maxn - total) if total < maxn else (m.group(0), 0)
        total += k; out.append(x[prev:m.start()]); out.append(pp); prev = m.end()
    out.append(x[prev:]); return ''.join(out), total
