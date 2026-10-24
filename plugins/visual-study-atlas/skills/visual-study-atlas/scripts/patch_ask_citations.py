#!/usr/bin/env python3
"""Upgrade the ask-box script already embedded in built pages so 'Textbook p.N' in answers becomes a link (no rebuild).
Usage: patch_ask_citations.py <app_folder>    (safe to run twice)"""
import sys, os, re
HELP = """  function show(el, text) {
    // 'Textbook p.N' in an answer becomes a link to that page when the atlas has a local textbook copy
    el.textContent = '';
    var has = !!document.querySelector('a[href^="textbook.pdf"]'), re = /Textbook p\\.(\\d+)/g, last = 0, m;
    if (!has) { el.textContent = text; return; }
    while ((m = re.exec(text))) {
      el.appendChild(document.createTextNode(text.slice(last, m.index)));
      var a = document.createElement('a'); a.href = 'textbook.pdf#page=' + m[1]; a.target = '_blank'; a.rel = 'noopener'; a.textContent = m[0]; el.appendChild(a); last = m.index + m[0].length;
    }
    el.appendChild(document.createTextNode(text.slice(last)));
  }
"""
n = 0
for f in sorted(os.listdir(sys.argv[1])):
    if not f.endswith('.html'): continue
    p = os.path.join(sys.argv[1], f); t = open(p, encoding='utf-8').read()
    if 'function show(el, text)' in t or 'out.textContent = u.text;' not in t: continue
    t = t.replace('out.textContent = u.text;', 'show(out, u.text);').replace('out.textContent = r.text;', 'show(out, r.text);')
    t = t.replace('  function msg(cls, text)', HELP + '  function msg(cls, text)', 1)
    open(p, 'w', encoding='utf-8').write(t); n += 1
print(f'patched {n} page(s)')
