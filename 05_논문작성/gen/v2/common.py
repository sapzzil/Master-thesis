import re, html, zipfile
SUBRE = re.compile(r'_\{((?:[^{}]|\{[^{}]*\})*)\}|_([A-Za-z0-9ν]+)|\^\{((?:[^{}]|\{[^{}]*\})*)\}')
PREV_OK = re.compile(r'[A-Za-zͰ-Ͽ²)\]∫Σ̂]')
def pieces(text):
    """md inline -> [(text, kind)] kind in '', 'sub', 'sup', 'b', 'i'"""
    out = []
    re2 = re.compile(r'(`[^`]+`|\*\*[^*]+\*\*|\*[^*\s][^*]*\*)')
    def plain(t, k=''):
        last = 0
        for m in SUBRE.finditer(t):
            isSup = m.group(3) is not None
            prev = t[m.start()-1] if m.start() > 0 else ''
            if not isSup and not PREV_OK.match(prev or ' '):
                continue
            if m.start() > last: out.append((t[last:m.start()], k))
            v = (m.group(3) if isSup else (m.group(1) if m.group(1) is not None else m.group(2)))
            v = re.sub(r'_\{?|\}', '', v)
            out.append((v, 'sup' if isSup else 'sub'))
            last = m.end()
        if last < len(t): out.append((t[last:], k))
    last = 0
    for m in re2.finditer(text):
        if m.start() > last: plain(text[last:m.start()])
        t = m.group(0)
        if t.startswith('`'): out.append((t[1:-1], ''))
        elif t.startswith('**'): plain(t[2:-2], 'b')
        else: plain(t[1:-1], 'i')
        last = m.end()
    if last < len(text): plain(text[last:])
    return out
def display(line):
    l = line.strip()
    l = re.sub(r'^[-*]\s+', '', l)
    l = re.sub(r'^#+\s+', '', l)
    return ''.join(t for t, _ in pieces(l))
PARA = re.compile(r'<w:p[ >](?:(?!</w:p>).)*?</w:p>', re.S)
def ptext(p):
    return html.unescape(''.join(re.findall(r'<w:t(?: [^>]*)?>([^<]*)</w:t>', p)))
