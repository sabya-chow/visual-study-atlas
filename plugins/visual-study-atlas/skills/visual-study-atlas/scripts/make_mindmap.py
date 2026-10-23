#!/usr/bin/env python3
"""Build mind_map.html for a built atlas (no model needed): root -> chapters -> sections; click a section to read its coverage checklist
in the side panel and jump to it. Adds a link to index.html. Usage: make_mindmap.py <app_folder> [--title "Atlas name"]"""
import sys, os, re, html, json

def txt(s): return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', s))).strip()

def main():
    app = sys.argv[1]; title = sys.argv[sys.argv.index('--title') + 1] if '--title' in sys.argv else 'Study atlas'
    chapters = []
    for f in sorted(os.listdir(app), key=lambda x: (len(x), x)):
        m = re.match(r'(ch\d+|appendix)\.html$', f)
        if not m: continue
        h = open(os.path.join(app, f), encoding='utf-8').read()
        ct = txt(re.search(r'<h1>(.*?)</h1>', h, re.S).group(1))
        secs = []
        for sm in re.finditer(r'<section id="([^"]+)"><div class="sec-n">(.*?)</div><h2>(.*?)</h2>(.*?)</section>', h, re.S):
            items = [txt(i) for i in re.findall(r'<li>(.*?)</li>', ''.join(re.findall(r'<ul class="covl">(.*?)</ul>', sm.group(4), re.S)), re.S)]
            secs.append({'id': sm.group(1), 'title': txt(sm.group(3)), 'items': items})
        chapters.append({'file': f, 'title': ct, 'secs': secs})
    style = re.search(r'<style>.*?</style>', open(os.path.join(app, 'index.html'), encoding='utf-8').read(), re.S).group(0)
    rowh, y = 30, 20; nodes = []; links = []; chy = []
    for ci, ch in enumerate(chapters):
        ys = []
        for s in ch['secs']: ys.append(y); y += rowh
        ch['ys'] = ys; ch['cy'] = (ys[0] + ys[-1]) / 2 if ys else y; y += 16
    H = y; rootY = H / 2
    W = 1000; svg = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Mind map of {html.escape(title)}: chapters and their sections" xmlns="http://www.w3.org/2000/svg">']
    svg.append(f'<rect x="10" y="{rootY - 22}" width="150" height="44" rx="22" class="bx ctl"/><text x="85" y="{rootY + 5}" text-anchor="middle" class="tt">{html.escape(title[:22])}</text>')
    data = {}
    for ch in chapters:
        svg.append(f'<path d="M160 {rootY} C 200 {rootY}, 200 {ch["cy"]}, 240 {ch["cy"]}" class="ar"/>')
        short = ch['title'] if len(ch['title']) < 34 else ch['title'][:31] + '...'
        svg.append(f'<a href="{ch["file"]}"><rect x="240" y="{ch["cy"] - 18}" width="230" height="36" rx="8" class="bx net"/><text x="355" y="{ch["cy"] + 4}" text-anchor="middle" class="tt">{html.escape(short)}</text></a>')
        for s, sy in zip(ch['secs'], ch['ys']):
            svg.append(f'<path d="M470 {ch["cy"]} C 500 {ch["cy"]}, 500 {sy + 12}, 530 {sy + 12}" class="ar"/>')
            nm = s['title'] if len(s['title']) < 62 else s['title'][:59] + '...'
            data[s['id']] = {'t': s['title'], 'f': ch['file'] + '#' + s['id'], 'i': s['items']}
            svg.append(f'<g class="sn" data-id="{s["id"]}" tabindex="0"><rect x="530" y="{sy}" width="460" height="24" rx="6" class="bx"/><text x="540" y="{sy + 16}" class="sm">{html.escape(nm)}</text></g>')
    svg.append('</svg>')
    body = (f'<header><div class="wrap"><div class="eyebrow">Mind map</div><h1>{html.escape(title)}: mind map</h1><p class="lead">Chapters and sections at a glance. Click a section to see its checklist and open it.</p>'
            '<nav class="jump"><a href="index.html">All chapters</a></nav></div></header><div class="wrap"><div class="mm"><div class="scroll">' + ''.join(svg) + '</div>'
            '<aside class="card" id="mmside"><h3>Pick a section</h3><p style="font-size:14.5px;margin:0">Its checklist appears here.</p></aside></div></div>')
    css = '.mm{display:grid;grid-template-columns:minmax(0,2fr) minmax(0,1fr);gap:16px;margin-top:20px}.mm .scroll svg{min-width:900px}.sn{cursor:pointer}.sn:hover rect,.sn:focus-visible rect,.sn.on rect{stroke:var(--ctl);fill:var(--ctl-bg)}#mmside{position:sticky;top:12px;align-self:start;max-height:80vh;overflow:auto}#mmside ul{font-size:14px;padding-left:18px}@media(max-width:900px){.mm{grid-template-columns:1fr}}'
    js = ('<script>var D=' + json.dumps(data).replace('</', '<\\/') + ';var side=document.getElementById("mmside");function pick(g){document.querySelectorAll(".sn").forEach(function(x){x.classList.remove("on")});g.classList.add("on");var d=D[g.dataset.id];'
          'side.innerHTML="<h3></h3><p style=\\"margin:0 0 8px\\"><a href=\\"\\">Open this section</a></p><ul></ul>";side.querySelector("h3").textContent=d.t;side.querySelector("a").href=d.f;'
          'd.i.forEach(function(t){var li=document.createElement("li");li.textContent=t;side.querySelector("ul").appendChild(li)})}'
          'document.querySelectorAll(".sn").forEach(function(g){g.addEventListener("click",function(){pick(g)});g.addEventListener("keydown",function(e){if(e.key==="Enter")pick(g)})});</script>')
    page = f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}: mind map</title>{style.replace("</style>", css + "</style>")}</head><body>{body}{js}</body></html>'
    open(os.path.join(app, 'mind_map.html'), 'w', encoding='utf-8').write(page)
    ip = os.path.join(app, 'index.html'); ih = open(ip, encoding='utf-8').read()
    if 'mind_map.html' not in ih:
        ih = ih.replace('<div class="keys">', '<p style="margin:14px 0 0"><a style="color:var(--ctl);font-weight:600" href="mind_map.html">Open the mind map &rarr;</a></p><div class="keys">', 1) if '<div class="keys">' in ih else ih.replace('</header>', '<p class="wrap"><a style="color:var(--ctl);font-weight:600" href="mind_map.html">Open the mind map &rarr;</a></p></header>', 1)
        open(ip, 'w', encoding='utf-8').write(ih)
    print('mind_map.html written;', sum(len(c['secs']) for c in chapters), 'sections')
main()
