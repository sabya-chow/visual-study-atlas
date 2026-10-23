#!/usr/bin/env python3
"""Export flashcards from a built atlas for Anki (free flashcard app with built-in spaced repetition).
Usage: export_anki.py <app_folder> <out.txt> [--checklist]
Cards come from: definition tables (term -> meaning), self-check <details> Q/A pairs, and scored quiz items (question -> correct answer + why).
--checklist also adds one recall card per coverage-checklist line (front: the item, back: its section and page link).
Import in Anki: File > Import, pick out.txt (tab separated, HTML allowed, tags in column 3)."""
import sys, os, re, html

def txt(s): return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', s))).strip()
def keep(s): return re.sub(r'<(?!/?(b|i|br|ul|li)\b)[^>]+>', '', s).strip()

def cards(page_html, chapter, with_checklist):
    out = []
    for sm in re.finditer(r'<section id="([^"]+)"><div class="sec-n">.*?</div><h2>(.*?)</h2>(.*?)</section>', page_html, re.S):
        sid, title, body = sm.group(1), txt(sm.group(2)), sm.group(3)
        tag = f'{chapter} {sid}'.replace(' ', '_')
        for tb in re.finditer(r'<table>(.*?)</table>', body, re.S):
            heads = [txt(h) for h in re.findall(r'<th>(.*?)</th>', tb.group(1), re.S)]
            for tr in re.findall(r'<tr>(.*?)</tr>', tb.group(1), re.S):
                tds = re.findall(r'<td>(.*?)</td>', tr, re.S)
                if len(tds) < 2 or '<b>' not in tds[0]: continue
                front = txt(tds[0])
                back = keep(tds[1]) if len(tds) == 2 else '<br>'.join(f'<b>{h}:</b> {keep(c)}' for h, c in zip(heads[1:], tds[1:]))
                out.append((f'{front}', back, tag))
        for q, a in re.findall(r'<details><summary>(.*?)</summary><p>(.*?)</p></details>', body, re.S):
            out.append((keep(q), keep(a), tag + '_selfcheck'))
        for qq in re.finditer(r'<div class="qq" data-ans="(\d+)"><p class="qt">(.*?)</p><ul class="qo">(.*?)</ul><div class="qx" hidden><b class="qv"></b>(.*?)</div></div>', body, re.S):
            opts = [txt(o) for o in re.findall(r'<button[^>]*class="qopt"[^>]*>(.*?)</button>', qq.group(3), re.S)]
            front = keep(re.sub(r'^<b>\d+\.</b>\s*', '', qq.group(2))) + '<br><br>' + '<br>'.join(opts)
            out.append((front, '<b>' + opts[int(qq.group(1))] + '</b><br>' + txt(qq.group(4)), tag + '_quiz'))
        if with_checklist:
            for it in re.findall(r'<li>(.*?)</li>', ''.join(re.findall(r'<ul class="covl">(.*?)</ul>', body, re.S)), re.S):
                out.append(('Recall: ' + txt(it), f'See: {title} ({sid})', tag + '_checklist'))
    return out

if __name__ == '__main__':
    app, dst = sys.argv[1], sys.argv[2]; wc = '--checklist' in sys.argv
    allc = []
    for f in sorted(os.listdir(app)):
        m = re.match(r'(ch\d+|appendix)\.html$', f)
        if m: allc += cards(open(os.path.join(app, f), encoding='utf-8').read(), m.group(1), wc)
    with open(dst, 'w', encoding='utf-8') as fh:
        fh.write('#separator:tab\n#html:true\n#tags column:3\n')
        for a, b, c in allc: fh.write(f'{a.replace(chr(9), " ")}\t{b.replace(chr(9), " ").replace(chr(10), " ")}\t{c}\n')
    print(f'{len(allc)} cards -> {dst}')
