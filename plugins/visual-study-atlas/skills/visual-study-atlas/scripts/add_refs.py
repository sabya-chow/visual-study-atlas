#!/usr/bin/env python3
"""Add "Textbook" page links (+ sub-topic chips) and "Video" links to every section of a built local atlas.
Run AFTER make_local.py:   add_refs.py <app_folder> <refs.json> [--no-verify]
Needs pypdf (pip install pypdf) and internet for video verification.

refs.json
{
 "pdf": "/path/source.pdf",                 # copied into the app as textbook.pdf (served inline by server.py)
 "ranges": {"ch1": [87, 156], "ch2": [156, 260]},   # PDF page range (1-based, inclusive start, exclusive end) of each chapter
 "end_marker": "Summary",                   # optional: last section of a chapter ends at the page holding this heading
 "sections": {
   "ch1-s1": {"heading": "Security 101",               # exact heading LINE in the PDF text (long headings: prefix match)
              "chips": ["Confidentiality", ["label", "Exact Heading"]],   # optional sub-topic page chips
              "videos": [["YouTubeID", "Channel", "Title"]]},              # optional
   ...}
}
Section keys must match the section ids in the pages (chN-sM). Sections listed in order per chapter.
Page numbers are PDF page numbers (viewer page box), not printed numbers. Links land on the page where a heading starts."""
import sys, os, re, json, html, shutil, urllib.request

def main():
    app, spec_path = sys.argv[1], sys.argv[2]
    verify = '--no-verify' not in sys.argv
    from pypdf import PdfReader
    spec = json.load(open(spec_path))
    d = PdfReader(spec['pdf'])
    lines = [[l.strip() for l in (pg.extract_text() or '').split('\n')] for pg in d.pages]
    hit = lambda h, l: l == h or (len(h) > 25 and l.startswith(h))
    by_ch = {}
    for key, v in spec['sections'].items():
        m = re.match(r'(ch\d+)-s(\d+)$', key); by_ch.setdefault(m.group(1), []).append((int(m.group(2)), key, v))
    refs = {}
    for ch, secs in by_ch.items():
        secs.sort(); lo, hi = spec['ranges'][ch]; last = lo - 1; starts = []
        for _, key, v in secs:
            p = next((q for q in range(max(last - 1, lo - 1), hi - 1) if any(hit(v['heading'], l) for l in lines[q])), None)
            if p is None: print('WARN heading not found:', key, v['heading']); p = last + 1
            starts.append(p + 1); last = p + 1
        for i, (_, key, v) in enumerate(secs):
            a = starts[i]; b = starts[i + 1] if i + 1 < len(secs) else hi - 1
            if i + 1 == len(secs) and spec.get('end_marker'):
                b = next((q + 1 for q in range(a - 1, hi - 1) if spec['end_marker'] in lines[q]), b)
            ln = lambda p, t: f'<a href="textbook.pdf#page={p}" target="_blank" rel="noopener">{t}</a>'
            h = '<div class="refs"><span class="rk">Textbook</span> ' + ln(a, f'open at p.{a}') + (f' <span class="rs">(this section: pp. {a}&ndash;{b})</span>' if b > a else '')
            chips = []
            for c in v.get('chips', []):
                lab, head = (c, c) if isinstance(c, str) else c
                for q in range(a - 1, b):
                    if any(hit(head, l) for l in lines[q]): chips.append(ln(q + 1, f'{html.escape(lab)} p.{q + 1}')); break
            if chips: h += '<span class="rc">' + ' '.join(chips) + '</span>'
            h += '</div>'
            vids = v.get('videos', [])
            if vids:
                for vid, ch_, tt in vids:
                    if verify:
                        try:
                            j = json.load(urllib.request.urlopen(f'https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={vid}&format=json', timeout=10))
                            print('video ok', vid, '|', j['author_name'], '|', j['title'])
                        except Exception as e: print('WARN video not verified', vid, e)
                h += '<div class="refs vid"><span class="rk">Video</span> ' + ' '.join(f'<a href="https://www.youtube.com/watch?v={vid}" target="_blank" rel="noopener">&#9654; {html.escape(tt)} <span class="rs">({html.escape(c)})</span></a>' for vid, c, tt in vids) + '</div>'
            refs[key] = h
    css = ('.refs{display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 12px;margin:0 0 14px;font-size:13.5px}.refs .rk{font-family:var(--mono);font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}'
           '.refs a{color:var(--ctl);text-decoration:none;border-bottom:1px solid var(--line)}.refs a:hover,.refs a:focus-visible{border-bottom-color:var(--ctl);outline:none}.refs .rs{color:var(--muted)}'
           '.refs .rc{display:flex;flex-wrap:wrap;gap:4px 10px}.refs.vid a{border-bottom:0;padding:2px 8px;border:1px solid var(--line);border-radius:999px}')
    n = [0]
    for f in sorted(os.listdir(app)):
        if not f.endswith('.html'): continue
        t = open(os.path.join(app, f), encoding='utf-8').read(); t0 = t
        def sub(m):
            k = m.group(2)
            if k in refs and 'class="refs"' not in m.group(0): n[0] += 1; return m.group(1) + refs[k]
            return m.group(0)
        t = re.sub(r'(<section id="(ch\d+-s\d+)"><div class="sec-n">.*?</h2><p class="claim">.*?</p>)', sub, t, flags=re.S)
        if t != t0 and '.refs{' not in t: t = t.replace('</style>', css + '</style>', 1)
        if t != t0: open(os.path.join(app, f), 'w', encoding='utf-8').write(t)
    shutil.copy(spec['pdf'], os.path.join(app, 'textbook.pdf'))
    # page-labelled text for retrieval, so ask-box answers can cite 'Textbook p.N' (only the built chapter ranges)
    first = min(r[0] for r in spec['ranges'].values()); lastp = max(r[1] for r in spec['ranges'].values())
    os.makedirs(os.path.join(app, 'book'), exist_ok=True)
    pj = [{'p': q + 1, 't': ' '.join(lines[q])} for q in range(first - 1, min(lastp, len(d.pages)))]
    json.dump(pj, open(os.path.join(app, 'book', 'textbook.pages.json'), 'w'))
    print(f'patched {n[0]} sections; textbook.pdf copied into {app}')
main()
