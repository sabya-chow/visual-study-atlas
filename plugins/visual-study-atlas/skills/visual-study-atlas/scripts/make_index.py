#!/usr/bin/env python3
"""Rebuild index.html for a built local atlas from its chapter pages (chN.html): one card per chapter (title, lead, section and diagram counts),
a how-to-study block, a map of all sections, and a link to mind_map.html when present. Use after adding chapters.
Usage: make_index.py <app_folder> --title "Atlas name" [--kicker "Study atlas"] [--lead "One sentence under the title"]"""
import sys, os, re, html

def txt(s): return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', s))).strip()

def main():
    a = sys.argv; app = a[1]
    opt = lambda k, d: a[a.index(k) + 1] if k in a else d
    title = opt('--title', 'Study atlas'); kicker = opt('--kicker', 'Study atlas')
    lead = opt('--lead', 'Every concept of each chapter as diagrams, definition tables and a coverage checklist per section, with a scored quiz at the end of each chapter and a click-anywhere ask box.')
    chs = sorted((f for f in os.listdir(app) if re.match(r'ch\d+\.html$', f)), key=lambda f: int(re.sub(r'\D', '', f)))
    rows = toc = ''; style = ''
    for f in chs:
        n = int(re.sub(r'\D', '', f)); h = open(os.path.join(app, f), encoding='utf-8').read()
        if not style: style = re.search(r'<style>.*?</style>', h, re.S).group(0)
        t = txt(re.search(r'<h1>(.*?)</h1>', h, re.S).group(1)); ld = txt(re.search(r'<p class="lead">(.*?)</p>', h, re.S).group(1))
        secs = re.findall(r'<section id="([^"]+)"><div class="sec-n">SECTION \d+</div><h2>(.*?)</h2>', h, re.S)
        ld = ld if len(ld) < 230 else ld[:227] + '...'
        rows += f'<a class="chap" href="{f}"><span class="cn">{n}</span><span class="ct"><b>{html.escape(t)}</b><span>{html.escape(ld)}</span></span><span class="cm">{len(secs)} sections<br>{len(re.findall("<svg", h))} diagrams</span></a>'
        toc += f'<h3 style="margin-top:20px">Chapter {n}: {html.escape(t)}</h3><div class="tw"><table><tbody>' + ''.join(f'<tr><td style="width:70px">{i}</td><td><a href="{f}#{sid}">{txt(st)}</a></td></tr>' for i, (sid, st) in enumerate(secs, 1)) + '</tbody></table></div>'
    mm = '<p style="margin:14px 0 0"><a style="color:var(--ctl);font-weight:600" href="mind_map.html">Open the mind map &rarr;</a></p>' if os.path.exists(os.path.join(app, 'mind_map.html')) or '--mindmap' in a else ''
    body = (f'<header><div class="wrap"><div class="eyebrow">{kicker}</div><h1>{html.escape(title)}</h1><p class="lead">{html.escape(lead)}</p>{mm}'
            '<div class="keys"><span><i class="sw ctl"></i>control / defense</span><span><i class="sw thr"></i>threat / weak point</span><span><i class="sw dat"></i>asset / sensitive item</span><span><i class="sw net"></i>flow / infrastructure</span></div></div></header>'
            f'<div class="wrap"><section id="chapters"><div class="sec-n">CHAPTERS</div><h2>Pick a chapter</h2><p class="claim">Each page: sections with one claim and one picture each, tables that hold every definition, a collapsible coverage checklist, step-through flow diagrams, and a scored quiz with an open-answer self-check at the end.</p><div class="chaps">{rows}</div></section>'
            '<section id="how"><div class="sec-n">HOW TO USE</div><h2>How to study from this</h2><div class="trio"><div class="card"><h3>1. Read the picture first</h3><p style="font-size:14.5px;margin:0">Each section opens with a one-line claim and a diagram; use Step through on flow diagrams, then read the tables.</p></div><div class="card"><h3>2. Tick the checklist</h3><p style="font-size:14.5px;margin:0">Open the coverage checklist at the end of a section and make sure you can explain each item.</p></div><div class="card"><h3>3. Quiz, then ask</h3><p style="font-size:14.5px;margin:0">Take the chapter quiz; click any sentence, table cell or diagram box to ask the local model. Answers cite textbook pages.</p></div></div>'
            '<p class="note">Notes marked &ldquo;Beyond the book &ndash; verify&rdquo; are additions, not from the source. Formulas are given in words only. Chapter end matter (Study Essentials, Written Lab, Review Questions) is not included.</p></section>'
            f'<section id="map"><div class="sec-n">MAP</div><h2>All sections</h2>{toc}</section><footer>Diagrams, checklists and quizzes are a study aid written for this atlas.</footer></div>')
    xcss = ('.chaps{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.chap{display:flex;gap:14px;align-items:flex-start;padding:14px 16px;border:1px solid var(--line);border-radius:10px;background:var(--surface);color:var(--fg);text-decoration:none;min-width:0}'
            '.chap:hover,.chap:focus-visible{border-color:var(--ctl);outline:none}.cn{font:800 28px var(--disp);color:var(--ctl)}.ct{display:flex;flex-direction:column;gap:4px;flex:1;min-width:0}.ct span{font-size:14px;color:var(--muted)}.cm{font:12px var(--mono);color:var(--muted);text-align:right;white-space:nowrap}.tw a{color:var(--ctl)}@media(max-width:760px){.chaps{grid-template-columns:1fr}}')
    shim = ''
    old = os.path.join(app, 'index.html')   # keep the previous index's scripts (ask-box shim and ask script)
    if os.path.exists(old):
        o = open(old, encoding='utf-8').read()
        o_scripts = re.findall(r'<script>.*?</script>', o, re.S)
        shim = ''.join(o_scripts)
    doc = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
           f'<title>{html.escape(title)}</title>' + style.replace('</style>', xcss + '</style>') + '</head><body>' + shim + body + '</body></html>')
    open(old, 'w', encoding='utf-8').write(doc); print(f'index.html: {len(chs)} chapters')
main()
