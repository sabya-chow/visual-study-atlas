#!/usr/bin/env python3
"""Retrofit step-through onto figures that are already built (no rebuild of the chapter).
Usage: add_steps.py <page.html> <spec.json>
spec.json: {"figures": {"<text found in the figure's aria-label>": ["title of box 1", "title of box 2", ...]}}
The list gives the reading order of the boxes by the start of each box's first line of text. Arrows are revealed together with the later of the two boxes
they connect; labels stay visible. Adds the Step-through bar and the .stepfig class (the page also needs steps.js and the step CSS from atlas_kit.EXTRA)."""
import sys, re, json, html

def parse_svg(svg):
    head, inner = re.match(r'(<svg[^>]*>)(.*)</svg>', svg, re.S).groups()
    defs = ''
    m = re.search(r'<defs>.*?</defs>', inner, re.S)
    if m: defs = m.group(0); inner = inner.replace(defs, '', 1)
    els = re.findall(r'<rect[^>]*?/>|<text[^>]*>.*?</text>|<path[^>]*?/>|<circle[^>]*?/>|<line[^>]*?/>|<g[^>]*>.*?</g>', inner, re.S)
    return head, defs, els

def num(s, k): m = re.search(rf'\b{k}="([-\d.]+)"', s); return float(m.group(1)) if m else None

def process(svg, order):
    head, defs, els = parse_svg(svg)
    boxes = []  # (start_idx, rect geometry, title, members)
    for i, e in enumerate(els):
        if e.startswith('<rect') and re.search(r'class="bx', e) and num(e, 'width') and num(e, 'width') > 60:
            boxes.append({'i': i, 'x': num(e, 'x'), 'y': num(e, 'y'), 'w': num(e, 'width'), 'h': num(e, 'height'), 'members': [i], 'title': ''})
    for b in boxes:
        for j in range(b['i'] + 1, len(els)):
            e = els[j]
            if e.startswith('<text'):
                cx, cy = num(e, 'x'), num(e, 'y')
                if cx is not None and b['x'] - 2 <= cx <= b['x'] + b['w'] + 2 and b['y'] <= cy <= b['y'] + b['h'] + 2:
                    b['members'].append(j)
                    if not b['title']: b['title'] = html.unescape(re.sub(r'<[^>]+>', '', e)).strip()
            if e.startswith('<rect') and j != b['i'] and re.search(r'class="bx', e): break
    step_of = {}
    for n, t in enumerate(order, 1):
        b = next((x for x in boxes if x['title'].lower().startswith(t.lower())), None)
        if not b: print('  WARN no box titled', t); continue
        b['step'] = n
    stepped = [b for b in boxes if 'step' in b]
    if not stepped: return None
    for b in stepped:
        for j in b['members']: step_of[j] = b['step']
    def at(px, py, tol=8):
        for b in stepped:
            if b['x'] - tol <= px <= b['x'] + b['w'] + tol and b['y'] - tol <= py <= b['y'] + b['h'] + tol: return b['step']
    for i, e in enumerate(els):
        if e.startswith('<path') and 'class="ar' in e:
            pts = re.findall(r'[ML]\s*(-?[\d.]+)\s+(-?[\d.]+)', re.search(r'd="([^"]+)"', e).group(1))
            if len(pts) < 2: continue
            a = at(float(pts[0][0]), float(pts[0][1])); b_ = at(float(pts[-1][0]), float(pts[-1][1]))
            s = max([x for x in (a, b_) if x] or [len(order)])
            step_of[i] = s
    out = []
    for i, e in enumerate(els):
        out.append(f'<g data-step="{step_of[i]}">{e}</g>' if i in step_of else e)
    caps = [next((b['title'] for b in stepped if b['step'] == n), '') for n in range(1, len(order) + 1)]
    return head + defs + ''.join(out) + '</svg>', len(order), caps

def main():
    page, spec = sys.argv[1], json.load(open(sys.argv[2]))
    t = open(page, encoding='utf-8').read(); done = 0
    def fig(m):
        nonlocal done
        block = m.group(0)
        if 'stepfig' in block: return block
        al = re.search(r'aria-label="([^"]*)"', block).group(1)
        for key, order in spec['figures'].items():
            if key.lower() in html.unescape(al).lower():
                r = process(re.search(r'<svg.*?</svg>', block, re.S).group(0), order)
                if not r: return block
                svg, n, caps = r; done += 1
                bar = (f'<div class="stepbar" data-n="{n}" data-caps="{html.escape(json.dumps(caps))}"><button type="button" class="sgo">Step through</button>'
                       '<button type="button" class="sprev" hidden>&larr; Back</button><button type="button" class="snext" hidden>Next &rarr;</button>'
                       '<button type="button" class="sall" hidden>Show all</button><span class="scap"></span></div>')
                block = block.replace(re.search(r'<svg.*?</svg>', block, re.S).group(0), svg).replace('<figure class="fig"', '<figure class="fig stepfig"', 1)
                return block.replace('<figcaption>', bar + '<figcaption>', 1)
        return block
    t = re.sub(r'<figure class="fig".*?</figure>', fig, t, flags=re.S)
    open(page, 'w', encoding='utf-8').write(t); print(f'{page}: {done} figure(s) now step-through')
main()
