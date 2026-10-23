#!/usr/bin/env python3
"""Turn any source into plain text for reading and retrieval.
  extract_text.py <file-or-url> <out.txt>
Handles: .pdf (pdftotext), .txt/.md, .srt/.vtt (timestamps removed), .html/URL, .ipynb (cells), .py (module outline)."""
import sys, re, subprocess, json, os, urllib.request
from html.parser import HTMLParser
src, out = sys.argv[1], sys.argv[2]
class T(HTMLParser):
    def __init__(s): super().__init__(); s.o = []; s.k = 0
    def handle_starttag(s, t, a):
        if t in ('script', 'style'): s.k += 1
        if t in ('p', 'li', 'h1', 'h2', 'h3', 'br', 'tr'): s.o.append('\n')
    def handle_endtag(s, t):
        if t in ('script', 'style'): s.k = max(0, s.k - 1)
    def handle_data(s, d):
        if not s.k: s.o.append(d)
if src.startswith('http'):
    h = urllib.request.urlopen(urllib.request.Request(src, headers={'User-Agent': 'Mozilla/5.0'})).read().decode('utf-8', 'ignore'); p = T(); p.feed(h); txt = ''.join(p.o)
else:
    ext = os.path.splitext(src)[1].lower()
    if ext == '.pdf': txt = subprocess.run(['pdftotext', '-layout', src, '-'], capture_output=True, text=True).stdout
    elif ext in ('.srt', '.vtt'): txt = re.sub(r'\d\d:\d\d:\d\d[.,]\d+ --> .*|^\d+$|WEBVTT', '', open(src, errors='ignore').read(), flags=re.M)
    elif ext in ('.html', '.htm'): p = T(); p.feed(open(src, errors='ignore').read()); txt = ''.join(p.o)
    elif ext == '.ipynb': nb = json.load(open(src)); txt = '\n\n'.join(('# [markdown]\n' if c['cell_type'] == 'markdown' else '# [code]\n') + ''.join(c['source']) for c in nb['cells'])
    else: txt = open(src, errors='ignore').read()
txt = '\n'.join(l.rstrip() for l in txt.splitlines() if l.strip())
open(out, 'w').write(txt); print(f'{len(txt)} chars, {len(txt.split())} words -> {out}')
