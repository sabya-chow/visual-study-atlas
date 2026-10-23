import re, sys, os, json
D = sys.argv[1]
REQ = json.load(open(sys.argv[2])) if len(sys.argv) > 2 else {}
def body(p):
    s = open(os.path.join(D, p)).read()
    return re.search(r'<body>(.*)</body>', s, re.S).group(1), s
views = []
idx_body, idx_full = body('index.html')
css = re.search(r'<style>(.*?)</style>', idx_full, re.S).group(1)
head = re.search(r'<title>.*?</title>.*?(?=<style>)', idx_full, re.S).group(1 - 1) if False else None
head_txt = re.search(r'(<title>.*?)<style>', idx_full, re.S).group(1)
idx_body = idx_body.replace('<h2>Pick a chapter</h2>', '<h2>Pick a chapter</h2><p id="asktip" class="asktip" hidden><b>Ask anything.</b> Click any sentence, table cell or diagram box, or select a few words, and a small box opens: type your doubt and get a compact answer, with an example when it helps. Toggle it with the pill at the bottom left.</p>')
def fix_nav(h):
    h = re.sub(r'href="index\.html"', 'href="#index"', h)
    h = re.sub(r'href="(ch\d+|appendix)\.html"', r'href="#\1"', h)
    return h
views.append('<div class="view" id="v-index">' + fix_nav(idx_body) + '</div>')
import glob
ids = sorted([os.path.basename(p)[:-5] for p in glob.glob(os.path.join(D, 'ch*.html'))], key=lambda x: int(re.sub(r'\D', '', x) or 0)) + (['appendix'] if os.path.exists(os.path.join(D, 'appendix.html')) else [])
for vid in ids:
    b, _ = body(vid + '.html')
    b = re.sub(r'id="s(\d+)"', rf'id="{vid}-s\1"', b)
    b = re.sub(r'href="#s(\d+)"', rf'href="#{vid}-s\1"', b)
    b = re.sub(r'id="([arcd]\d+)"', rf'id="{vid}_\1"', b)
    b = re.sub(r'url\(#([arcd]\d+)\)', rf'url(#{vid}_\1)', b)
    views.append(f'<div class="view" id="v-{vid}" hidden>' + fix_nav(b) + '</div>')
ask_css = '''
.asktip{max-width:68ch;padding:10px 14px;border:1px solid var(--ctl);border-radius:10px;background:var(--ctl-bg);font-size:14.5px;margin:0 0 16px}
.ask-hov{outline:2px dashed var(--ctl);outline-offset:2px;cursor:help}
svg .ask-hov{outline:none;stroke:var(--ctl)!important;stroke-width:3}
svg text.ask-hov{fill:var(--ctl)!important;stroke:none!important}
#asktoggle{position:fixed;left:max(12px,env(safe-area-inset-left,0px));bottom:max(12px,env(safe-area-inset-bottom,0px));z-index:40;font:500 12px var(--mono);padding:8px 12px;border-radius:999px;border:1px solid var(--ctl);background:var(--surface);color:var(--fg);cursor:pointer}
#askpanel{position:fixed;right:max(12px,env(safe-area-inset-right,0px));bottom:max(12px,env(safe-area-inset-bottom,0px));width:min(430px,calc(100vw - 24px));max-height:min(62vh,520px);z-index:50;display:flex;flex-direction:column;background:var(--surface);color:var(--fg);border:1px solid var(--ctl);border-radius:12px;box-shadow:0 8px 30px rgba(0,0,0,.25)}
#askpanel[hidden]{display:none}
.ah{display:flex;gap:8px;align-items:flex-start;padding:10px 12px;border-bottom:1px solid var(--line)}
.aq{flex:1;font-size:12.5px;color:var(--muted);border-left:3px solid var(--ctl);padding-left:8px;min-width:0;overflow-wrap:anywhere}
.ax{border:0;background:none;color:var(--fg);font-size:20px;line-height:1;cursor:pointer;padding:0 4px}
.alog{padding:10px 12px;overflow:auto;display:flex;flex-direction:column;gap:8px;min-height:0}
.am{font-size:14px;line-height:1.5;white-space:pre-wrap;overflow-wrap:anywhere}
.am.q{align-self:flex-end;background:var(--net-bg);border:1px solid var(--net);border-radius:10px;padding:6px 10px;max-width:90%}
.am.a.err{color:var(--thr)}
.achips{display:flex;flex-wrap:wrap;gap:6px;padding:0 12px}
.achips button{font:12px var(--sans);padding:4px 9px;border-radius:999px;border:1px solid var(--line);background:var(--zone);color:var(--fg);cursor:pointer}
.achips button:hover,.achips button:focus-visible{border-color:var(--ctl);outline:none}
.af{display:flex;gap:6px;padding:10px 12px}
.af input{flex:1;min-width:0;font:14px var(--sans);padding:8px 10px;border:1px solid var(--line);border-radius:8px;background:var(--bg);color:var(--fg)}
.af input:focus{outline:2px solid var(--ctl);outline-offset:1px}
.af button{font:600 13px var(--sans);padding:8px 12px;border-radius:8px;border:1px solid var(--ctl);background:var(--ctl);color:var(--surface);cursor:pointer}
.af .astop{background:var(--surface);color:var(--fg)}
@media (max-width:760px){#askpanel{left:8px;right:8px;width:auto;bottom:8px}#asktoggle{bottom:auto;top:8px;left:8px}}
'''
js = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ask.js')).read()
for key, val in {'__SOURCE__': REQ.get('source', 'the source'), '__READER__': REQ.get('reader', 'The reader is a motivated learner.'), '__MATHNOTE__': REQ.get('mathnote', 'If equations matter, name each symbol and say what each term does.'),
                 '__LENSNOTE__': REQ.get('lensnote', 'If relevant, one line on what a practitioner or an exam would focus on.'), '__LENGTH__': REQ.get('length', 'usually 110 to 170 words; shorter if the question is simple'),
                 '__LENSES__': REQ.get('lenses', 'the lens panels')}.items():
    js = js.replace(key, val.replace('"', "'"))
qjs = ''.join(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f)).read() + '\n' for f in ('quiz.js', 'steps.js'))
doc = head_txt + '<style>' + css + ask_css + '</style>' + ''.join(views) + '<script>' + js + '</script><script>' + qjs + '</script>'
open(os.path.join(D, 'index_artifact.html'), 'w').write(doc)
open(os.path.join(D, 'atlas_single_local.html'), 'w').write('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"></head><body>' + doc + '</body></html>')
print(len(doc))
