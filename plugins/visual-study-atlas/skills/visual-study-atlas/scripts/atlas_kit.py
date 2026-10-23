"""atlas_kit: helpers for building a diagram-first study atlas from a book.
Copy next to your chapter scripts. Usage: from atlas_kit import *"""
#!/usr/bin/env python3
import html, sys, re, os

E = html.escape
_n = [0]


def defs(n):
    return (f'<defs>'
            f'<marker id="a{n}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path class="mk" d="M0,0 L10,5 L0,10z"/></marker>'
            f'<marker id="r{n}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path class="mkr" d="M0,0 L10,5 L0,10z"/></marker>'
            f'<marker id="c{n}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path class="mkc" d="M0,0 L10,5 L0,10z"/></marker>'
            f'<marker id="d{n}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path class="mkd" d="M0,0 L10,5 L0,10z"/></marker>'
            f'</defs>')


class S:
    """one svg figure"""

    def __init__(self, vb, aria):
        _n[0] += 1
        self.n = _n[0]
        self.vb = vb
        self.aria = aria
        self.parts = []

    def raw(self, s):
        self.parts.append(s)

    def _wrap(self, s0, step):
        """Group everything added since s0 as one animation step (step-through button on the figure)."""
        if step:
            self.steps = max(getattr(self, 'steps', 0), int(step))
            self.parts[s0:] = [f'<g data-step="{int(step)}">' + ''.join(self.parts[s0:]) + '</g>']

    def captions(self, caps):
        """One short sentence per step, shown under the figure while stepping through."""
        self.caps = list(caps)

    def text(self, x, y, s, cls='', anchor='middle'):
        self.parts.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" class="{cls}">{E(html.unescape(s))}</text>')

    def box(self, x, y, w, h, lines, kind='', first_bold=True, rx=8, dash=False, size='sm', step=None):
        s0 = len(self.parts)
        k = f' {kind}' if kind else ''
        d = ' dashed' if dash else ''
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" class="bx{k}{d}"/>')
        n = len(lines)
        lh = 15
        y0 = y + h / 2 - (n - 1) * lh / 2 + 4
        for i, ln in enumerate(lines):
            cls = 'tt' if (i == 0 and first_bold) else size
            self.text(x + w / 2, round(y0 + i * lh, 1), ln, cls)
        self._wrap(s0, step)

    def line(self, pts, kind='', arrow=True, dash=False, step=None):
        s0 = len(self.parts)
        d = 'M' + ' L'.join(f'{a} {b}' for a, b in pts)
        m = {'': 'a', 'thr': 'r', 'ctl': 'c', 'dat': 'd'}[kind]
        me = f' marker-end="url(#{m}{self.n})"' if arrow else ''
        cls = f'ar {kind}' + (' dashed' if dash else '')
        self.parts.append(f'<path d="{d}" class="{cls}"{me}/>')
        self._wrap(s0, step)

    def render(self, caption):
        body = ''.join(self.parts)
        n = getattr(self, 'steps', 0)
        bar = ''
        if n:
            import json as _j
            bar = (f'<div class="stepbar" data-n="{n}" data-caps="{E(_j.dumps(getattr(self, "caps", [])))}"><button type="button" class="sgo">Step through</button>'
                   '<button type="button" class="sprev" hidden>&larr; Back</button><button type="button" class="snext" hidden>Next &rarr;</button>'
                   '<button type="button" class="sall" hidden>Show all</button><span class="scap"></span></div>')
        return (f'<figure class="fig{" stepfig" if n else ""}"><div class="scroll"><svg viewBox="{self.vb}" role="img" aria-label="{E(self.aria)}" '
                f'xmlns="http://www.w3.org/2000/svg">{defs(self.n)}{body}</svg></div>'
                f'{bar}<figcaption>{caption}</figcaption></figure>')



CSS = r'''
:root{
  /* layout: a long-scroll study guide; each section = one claim, one diagram, two lenses (set LENS_TITLES; pass empty lists to omit) */
  --bg:#f2f5f8; --surface:#ffffff; --fg:#12202c; --muted:#4d6176; --line:#c3cfda;
  --ctl:#0b7a75; --ctl-bg:#dcf2ef; --thr:#b8321b; --thr-bg:#fbe5df;
  --dat:#9a5b00; --dat-bg:#fcefd0; --net:#2457b8; --net-bg:#e1ebfb; --zone:#eaf0f5;
  --sans:'IBM Plex Sans',system-ui,-apple-system,'Segoe UI',sans-serif;
  --mono:'IBM Plex Mono',ui-monospace,Menlo,monospace;
  --disp:'Archivo',var(--sans);
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --bg:#0d151c; --surface:#16212b; --fg:#e5edf4; --muted:#9bacbd; --line:#2e4152;
  --ctl:#4fd1c5; --ctl-bg:#0e2e2c; --thr:#ff8f78; --thr-bg:#3a1b15;
  --dat:#f2b24c; --dat-bg:#33260b; --net:#86adff; --net-bg:#13233f; --zone:#111c26; color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#0d151c; --surface:#16212b; --fg:#e5edf4; --muted:#9bacbd; --line:#2e4152;
  --ctl:#4fd1c5; --ctl-bg:#0e2e2c; --thr:#ff8f78; --thr-bg:#3a1b15;
  --dat:#f2b24c; --dat-bg:#33260b; --net:#86adff; --net-bg:#13233f; --zone:#111c26; color-scheme:dark}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--fg);font-family:var(--sans);font-size:16px;line-height:1.6;
  padding-block:0 64px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
.wrap{max-width:1000px;margin:0 auto}
header{padding:48px 0 24px;border-bottom:2px solid var(--fg)}
.eyebrow{font-family:var(--mono);font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
h1{font-family:var(--disp);font-weight:800;font-size:clamp(34px,6vw,60px);line-height:1.02;margin:10px 0 14px;letter-spacing:-.02em;text-wrap:balance}
.lead{font-size:18px;max-width:62ch;color:var(--fg)}
.keys{display:flex;flex-wrap:wrap;gap:10px 18px;margin-top:20px;font-size:13px}
.keys span{display:inline-flex;align-items:center;gap:8px}
.sw{width:16px;height:16px;border-radius:4px;border:1.5px solid}
.sw.ctl{background:var(--ctl-bg);border-color:var(--ctl)}.sw.thr{background:var(--thr-bg);border-color:var(--thr)}
.sw.dat{background:var(--dat-bg);border-color:var(--dat)}.sw.net{background:var(--net-bg);border-color:var(--net)}
nav.jump{display:flex;flex-wrap:wrap;gap:8px;margin:22px 0 0}
nav.jump a{font-family:var(--mono);font-size:12px;padding:6px 10px;border:1px solid var(--line);border-radius:6px;color:var(--fg);text-decoration:none;background:var(--surface)}
nav.jump a:hover,nav.jump a:focus-visible{border-color:var(--ctl);outline:none;color:var(--ctl)}
section{padding:44px 0 8px;border-bottom:1px solid var(--line)}
h2{font-family:var(--disp);font-weight:800;font-size:clamp(24px,3.6vw,34px);letter-spacing:-.01em;margin:0 0 6px;text-wrap:balance}
.sec-n{font-family:var(--mono);font-size:12px;color:var(--muted);letter-spacing:.08em}
p.claim{font-size:17px;max-width:68ch;margin:6px 0 18px}
.fig{margin:0 0 20px}
.scroll{overflow-x:auto;border:1px solid var(--line);border-radius:10px;background:var(--surface);padding:10px}
.scroll svg{display:block;width:100%;min-width:640px;height:auto}
figcaption{font-size:14px;color:var(--muted);margin-top:8px;max-width:76ch}
.trio{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin-bottom:12px}
.trio .scroll svg{min-width:0}
.card{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:14px 16px;min-width:0}
.card h3{font-size:15px;margin:0 0 6px;font-family:var(--disp);font-weight:700}
.card ul{margin:6px 0 0;padding-left:18px;font-size:14.5px}
.card li{margin:3px 0}
.tag{font-family:var(--mono);font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}
.lenses{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;margin:8px 0 28px}
.lens{border-radius:10px;padding:14px 16px;border:1px solid;min-width:0}
.lens.c{background:var(--net-bg);border-color:var(--net)}
.lens.i{background:var(--ctl-bg);border-color:var(--ctl)}
.lens h3{margin:0 0 6px;font-size:13px;font-family:var(--mono);letter-spacing:.06em;text-transform:uppercase}
.lens.c h3{color:var(--net)}.lens.i h3{color:var(--ctl)}
.lens ul{margin:0;padding-left:18px;font-size:14.5px}.lens li{margin:4px 0}
table{border-collapse:collapse;width:100%;font-size:14.5px;background:var(--surface)}
th,td{border:1px solid var(--line);padding:9px 11px;text-align:left;vertical-align:top}
th{font-family:var(--mono);font-size:12px;letter-spacing:.05em;text-transform:uppercase;background:var(--zone)}
.tw{overflow-x:auto;border-radius:10px}
.pill{font-family:var(--mono);font-size:11.5px;padding:2px 7px;border-radius:5px;background:var(--net-bg);color:var(--net);border:1px solid var(--net);white-space:nowrap}
details{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:12px 16px;margin:10px 0}
summary{cursor:pointer;font-weight:600}
summary:focus-visible{outline:2px solid var(--ctl);outline-offset:3px}
details p{margin:8px 0 0;color:var(--muted)}
.note{font-size:14px;color:var(--muted);max-width:76ch;border-left:3px solid var(--dat);padding-left:12px;margin:18px 0}
footer{padding-top:28px;font-size:13px;color:var(--muted)}
/* svg parts */
svg text{font-family:var(--sans);font-size:12px;fill:var(--fg)}
svg .tt{font-weight:700;font-size:12.5px}svg .sm{font-size:11px;fill:var(--fg)}
svg .smr{font-size:11px;fill:var(--thr);font-weight:600}svg .smw{font-size:11px;fill:var(--surface);font-weight:700}
svg .lab{font-family:var(--mono);font-size:10px;letter-spacing:.06em;fill:var(--muted)}
svg .lgt,svg .numt{font-size:9px;font-weight:700;fill:var(--surface)}
svg .bx{fill:var(--surface);stroke:var(--line);stroke-width:1.5}
svg .bx.ctl{fill:var(--ctl-bg);stroke:var(--ctl)}svg .bx.thr{fill:var(--thr-bg);stroke:var(--thr)}
svg .bx.dat{fill:var(--dat-bg);stroke:var(--dat)}svg .bx.net{fill:var(--net-bg);stroke:var(--net)}
svg .dashed{stroke-dasharray:5 4}
svg .zone{fill:var(--zone);stroke:var(--muted);stroke-width:1.2;stroke-dasharray:6 4}
svg .ar{fill:none;stroke:var(--muted);stroke-width:1.7}svg .ar.ctl{stroke:var(--ctl)}svg .ar.thr{stroke:var(--thr)}svg .ar.dat{stroke:var(--dat)}
svg .ar.dashed{stroke-dasharray:4 4}
svg .mk{fill:var(--muted)}svg .mkr{fill:var(--thr)}svg .mkc{fill:var(--ctl)}svg .mkd{fill:var(--dat)}
svg .lg{fill:var(--net)}svg .num{fill:var(--fg)}svg .thrfill{fill:var(--thr)}
svg .gate{fill:var(--ctl);stroke:var(--surface);stroke-width:1.5}
@media (max-width:760px){.trio,.lenses{grid-template-columns:1fr}}
@media (prefers-reduced-motion:no-preference){nav.jump a{transition:border-color .15s,color .15s}}
'''

HEAD = '''<title>Study Atlas</title>
<meta name="claude:viewport-fit-sides" content="cover">
'''


LENS_TITLES = ("Exam lens", "Practitioner asks")  # set per project from requirements.json; pass lens() empty lists to omit


def lens(a, b):
    """Two closing panels per section. Titles come from LENS_TITLES."""
    if not a and not b:
        return ''
    ca = ''.join(f'<li>{x}</li>' for x in a)
    cb = ''.join(f'<li>{x}</li>' for x in b)
    return (f'<div class="lenses"><div class="lens c"><h3>{LENS_TITLES[0]}</h3><ul>{ca}</ul></div>'
            f'<div class="lens i"><h3>{LENS_TITLES[1]}</h3><ul>{cb}</ul></div></div>')


def sec(id_, n, title, claim, body):
    return f'<section id="{id_}"><div class="sec-n">{n}</div><h2>{title}</h2><p class="claim">{claim}</p>{body}</section>'



BOOK = "TITLE OF SOURCE"  # set per project
CREDIT = ""        # e.g. author names; shown in the footer
ATLAS_NAME = "Study Atlas"
LAST_CHAPTER = 10   # chapters after this one get no 'next' link (set to the last BUILT chapter)
FOOT_NOTE = "Diagrams, checklists and self-checks are a study aid written for this page; items marked 'Beyond the book' are added and need verification."

EXTRA = '.pager{display:flex;gap:14px;margin-top:14px;font-family:var(--mono);font-size:12px}.pager a{color:var(--ctl)}svg .grid{stroke:var(--line);stroke-width:1}svg .bar.thrb{fill:var(--thr-bg);stroke:var(--thr);stroke-width:1.5}svg .bar.datb{fill:var(--dat-bg);stroke:var(--dat);stroke-width:1.5}svg .chip{fill:var(--surface);stroke:var(--line);stroke-width:1.5}svg .chip.on{fill:var(--ctl-bg);stroke:var(--ctl)}svg .chipt{font-weight:700;font-size:11px;fill:var(--muted)}svg .chipt.on{fill:var(--ctl)}svg .big{font-size:26px;font-weight:800;fill:var(--thr)}'

def page(n, title, intro, body_sections, pages='', label=None):
    """body_sections: list of section html strings (from sec())."""
    nav = ''
    for m in re.finditer(r'<section id="(s\d+)"><div class="sec-n">SECTION (\d+)</div><h2>(.*?)</h2>', ''.join(body_sections)):
        short = re.sub(r'<.*?>', '', m.group(3))
        short = short if len(short) < 34 else short[:31] + '...'
        nav += f'<a href="#{m.group(1)}">{m.group(2)} {short}</a>'
    label = label or f'Chapter {n}'
    prev = f'<a href="ch{n-1}.html">&larr; Ch {n-1}</a>' if n > 1 else ''
    nxt = (f'<a href="ch{n+1}.html">Ch {n+1} &rarr;</a>' if n < LAST_CHAPTER else '')
    head = (f'<header><div class="wrap"><div class="eyebrow">{E(BOOK)} &middot; {label}{(" &middot; pp. " + pages) if pages else ""}</div>'
            f'<h1>{title}</h1><p class="lead">{intro}</p>'
            '<div class="keys"><span><i class="sw ctl"></i>control / defense</span><span><i class="sw thr"></i>threat / weak point</span>'
            '<span><i class="sw dat"></i>asset / sensitive item</span><span><i class="sw net"></i>flow / infrastructure</span></div>'
            f'<nav class="jump" aria-label="Sections"><a href="index.html">All chapters</a>{prev}{nxt}</nav>'
            f'<nav class="jump" aria-label="On this page">{nav}</nav></div></header><div class="wrap">')
    foot = (f'<footer>Source: {E(CREDIT) + ", " if CREDIT else ""}<i>{E(BOOK)}</i>, {label}. {FOOT_NOTE}'
            f'<div class="pager"><a href="index.html">Index</a>{prev}{nxt}</div></footer></div>')
    extra = EXTRA
    doc = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
           + HEAD.replace('Study Atlas', f'{ATLAS_NAME} {label}') + '<style>' + CSS + EXTRA + '</style></head><body>' + head + ''.join(body_sections) + foot + '</body></html>')
    return doc

def write(path, html):
    open(path, 'w').write(html)


def cards(items):
    h = '<div class="trio">'
    for t, lis in items:
        h += f'<div class="card"><h3>{t}</h3><ul>' + ''.join(f'<li>{x}</li>' for x in lis) + '</ul></div>'
    return h + '</div>'


def table(headers, rows):
    th = ''.join(f'<th>{h}</th>' for h in headers)
    tr = ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows)
    return f'<div class="tw"><table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'


def quad(s, x0, y0, w, h, cells):
    for (dx, dy, k, t) in cells:
        s.raw(f'<rect x="{x0 + dx * w / 2}" y="{y0 + dy * h / 2}" width="{w / 2}" height="{h / 2}" class="bx {k}"/>')
        for i, ln in enumerate(t):
            s.text(x0 + dx * w / 2 + w / 4, y0 + dy * h / 2 + h / 4 - 8 + 16 * i, ln, 'tt' if i == 0 else 'sm')



# ---- helpers added for dense / exam-style books (coverage checklists, definition tables, beyond-the-book notes) ----
def check(items, title='Coverage checklist: what the source says here'):
    """Collapsible checklist closing a section: one line per item the source covers (completeness proof)."""
    li = ''.join(f'<li>{x}</li>' for x in items)
    return f'<details class="cov"><summary>{title} ({len(items)} items)</summary><ul class="covl">{li}</ul></details>'

def defs_table(rows, heads=('Term', 'Meaning')):
    """rows: [(term, meaning)] or [(term, [col2, col3...])]."""
    return table(list(heads), [[f'<b>{a}</b>'] + (list(b) if isinstance(b, (list, tuple)) else [b]) for a, b in rows])

def beyond(text):
    """Visible flag for anything not in the source."""
    return f'<div class="note beyond"><b>Beyond the book &ndash; verify:</b> {text}</div>'

def qa(qs):
    return ''.join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q, a in qs)

EXTRA += '.cov{margin:14px 0}.cov summary{color:var(--ctl)}.covl{columns:2;column-gap:28px;font-size:14px;margin:8px 0 0;padding-left:18px}.covl li{margin:3px 0;break-inside:avoid}.beyond{border-left-color:var(--net)}@media(max-width:760px){.covl{columns:1}}'


def quiz(items, qid='quiz', title='Quiz'):
    """Scored multiple choice. items: [{'q': text, 'opts': [4 strings], 'ans': index, 'why': explanation, 'ref': optional '#section-id'}].
    Write the questions in the quiz style chosen in the questionnaire (see references/quiz-styles.md). Vary the position of the answer."""
    out = [f'<div class="quiz" data-qid="{qid}"><div class="qhead"><b>{title}</b><span class="qscore">Score 0 / {len(items)}</span>'
           '<button type="button" class="qretry" hidden>Retry missed</button><button type="button" class="qreset">Reset</button></div>']
    for n, it in enumerate(items, 1):
        opts = ''.join(f'<li><button type="button" class="qopt" data-i="{i}"><span class="ql">{chr(65 + i)}</span> {o}</button></li>' for i, o in enumerate(it['opts']))
        ref = f' <a href="{it["ref"]}">Review the section</a>' if it.get('ref') else ''
        out.append(f'<div class="qq" data-ans="{it["ans"]}"><p class="qt"><b>{n}.</b> {it["q"]}</p><ul class="qo">{opts}</ul>'
                   f'<div class="qx" hidden><b class="qv"></b> {it["why"]}{ref}</div></div>')
    return ''.join(out) + '</div>'

EXTRA += (".quiz{margin:12px 0}.qhead{display:flex;flex-wrap:wrap;gap:8px 16px;align-items:center;margin-bottom:10px}.qscore{font-family:var(--mono);font-size:13px;color:var(--ctl)}"
          ".qhead button{font:12px var(--mono);padding:4px 10px;border:1px solid var(--line);border-radius:6px;background:var(--surface);color:var(--fg);cursor:pointer}"
          ".qq{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:12px 16px;margin:10px 0}.qt{margin:0 0 8px}"
          ".qo{list-style:none;margin:0;padding:0;display:grid;gap:6px}.qopt{width:100%;text-align:left;font:inherit;font-size:14.5px;padding:8px 10px;border:1px solid var(--line);border-radius:8px;background:var(--bg);color:var(--fg);cursor:pointer}"
          ".qopt:hover:not(:disabled),.qopt:focus-visible{border-color:var(--ctl);outline:none}.qopt:disabled{cursor:default}.qopt.ok{background:var(--ctl-bg);border-color:var(--ctl)}.qopt.bad{background:var(--thr-bg);border-color:var(--thr)}"
          ".ql{font-family:var(--mono);font-weight:700;margin-right:6px}.qx{margin-top:8px;font-size:14px;border-left:3px solid var(--line);padding-left:10px;color:var(--muted)}.qx.good{border-color:var(--ctl)}.qx.miss{border-color:var(--thr)}")

EXTRA += (".stepbar{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:8px 0 0}.stepbar button{font:12px var(--mono);padding:4px 10px;border:1px solid var(--ctl);border-radius:6px;background:var(--surface);color:var(--fg);cursor:pointer}"
          ".stepbar .scap{font-size:14px;color:var(--muted);flex:1;min-width:200px}[data-step]{transition:opacity .25s}.stepping [data-step].dim{opacity:.1}.stepping [data-step].cur rect{stroke-width:3.5}.stepping [data-step].cur path{stroke-width:3}"
          "@media (prefers-reduced-motion:reduce){[data-step]{transition:none}}")
