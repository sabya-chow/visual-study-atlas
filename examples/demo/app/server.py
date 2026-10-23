#!/usr/bin/env python3
"""Local server for the LLM Security Atlas. Standard library only.
Serves the static pages (index.html, ch*.html, optional textbook PDF) and answers /ask with a streamed answer from a local Ollama model,
grounded by retrieval over the atlas text and the book text in ./book."""
import json, os, re, sys, math, hashlib, threading, time, argparse
import urllib.request, urllib.error
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.abspath(__file__))
CFG = json.load(open(os.path.join(ROOT, 'config.json')))
OLLAMA = CFG['ollama'].rstrip('/')
INDEX = {'ready': False, 'chunks': [], 'vecs': [], 'status': 'not started'}

def ollama(path, payload=None, stream=False, timeout=600):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(OLLAMA + path, data=data, headers={'Content-Type': 'application/json'})
    return urllib.request.urlopen(req, timeout=timeout)

# ---------- corpus ----------
class Txt(HTMLParser):
    def __init__(self):
        super().__init__(); self.out = []; self.skip = 0
    def handle_starttag(self, t, a):
        if t in ('script', 'style', 'svg'): self.skip += 1
        if t in ('p', 'li', 'tr', 'h1', 'h2', 'h3', 'div', 'figcaption'): self.out.append('\n')
    def handle_endtag(self, t):
        if t in ('script', 'style', 'svg'): self.skip = max(0, self.skip - 1)
    def handle_data(self, d):
        if not self.skip: self.out.append(d)

def split(text, n):
    text = re.sub(r'[ \t]+', ' ', text)
    paras, cur, out = [p.strip() for p in text.split('\n') if p.strip()], '', []
    for p in paras:
        if len(cur) + len(p) > n and cur: out.append(cur); cur = ''
        cur += (' ' if cur else '') + p
    if cur: out.append(cur)
    return out

def corpus():
    n = CFG['retrieval']['chunk_chars']; items = []
    t = Txt()
    for pf in sorted(f for f in os.listdir(ROOT) if f.endswith('.html')): t.feed(open(os.path.join(ROOT, pf), encoding='utf-8').read())
    for c in split(''.join(t.out), n): items.append(('atlas', c))
    if CFG['retrieval'].get('use_book', True):
        bd = os.path.join(ROOT, 'book')
        for f in sorted(os.listdir(bd)) if os.path.isdir(bd) else []:
            if f.endswith('.pages.json'):   # page-labelled text: lets answers cite 'Textbook p.N'
                for pg in json.load(open(os.path.join(bd, f), encoding='utf-8')):
                    for c in split(pg['t'], n): items.append(('p.%d' % pg['p'], c))
            elif f.endswith('.txt'):
                raw = open(os.path.join(bd, f), encoding='utf-8', errors='ignore').read()
                raw = re.sub(r'\n(?=[a-z,;(])', ' ', raw)
                for c in split(raw, n): items.append((f[:-4], c))
    return items

def embed(texts):
    r = json.load(ollama('/api/embed', {'model': CFG['embed_model'], 'input': texts}))
    return r['embeddings']

def build_index():
    try:
        INDEX['status'] = 'reading text'
        items = corpus(); cache_p = os.path.join(ROOT, 'index_cache.json')
        cache = json.load(open(cache_p)) if os.path.exists(cache_p) else {}
        vecs, todo = [None] * len(items), []
        for i, (src, c) in enumerate(items):
            k = hashlib.md5((CFG['embed_model'] + c).encode()).hexdigest()
            if k in cache: vecs[i] = cache[k]
            else: todo.append((i, k))
        B = 32
        for s in range(0, len(todo), B):
            INDEX['status'] = f'embedding {s}/{len(todo)}'
            part = todo[s:s + B]; es = embed([items[i][1] for i, _ in part])
            for (i, k), v in zip(part, es):
                nv = math.sqrt(sum(x * x for x in v)) or 1.0
                v = [x / nv for x in v]; vecs[i] = v; cache[k] = v
        if todo: json.dump(cache, open(cache_p, 'w'))
        INDEX.update(chunks=items, vecs=vecs, ready=True, status=f'ready ({len(items)} passages)')
    except Exception as e:
        INDEX['status'] = f'retrieval off: {e}'

def retrieve(q, k):
    if not INDEX['ready'] or not q.strip(): return []
    qv = embed([q[:2000]])[0]; nq = math.sqrt(sum(x * x for x in qv)) or 1.0; qv = [x / nq for x in qv]
    scores = sorted(((sum(a * b for a, b in zip(qv, v)), i) for i, v in enumerate(INDEX['vecs'])), reverse=True)[:k]
    return [INDEX['chunks'][i] for _, i in scores]

# ---------- ask ----------
def build_messages(msgs, k):
    msgs = [dict(m) for m in msgs]
    first = msgs[0]['content']; last = next((m['content'] for m in reversed(msgs) if m['role'] == 'user'), '')
    clicked = ''
    m = re.search(r'Clicked part \([^)]*\): (.*)', first)
    if m: clicked = m.group(1)
    hits = retrieve((last + ' ' + clicked)[:1500], k)
    if hits:
        msgs[0]['content'] = first + '\n\nRELEVANT PASSAGES (from the atlas and the book; use them for facts, ignore if irrelevant). Passages labelled [p.N] are textbook pages: when you rely on one, finish your answer with a line such as "Textbook p.N" (at most two pages, only pages you used).\n' + '\n---\n'.join(f'[{s}] {c}' for s, c in hits)
    cites = []
    for s, _ in hits:
        if s.startswith('p.') and s not in cites: cites.append(s)
    return msgs, cites[:2]

def stream_answer(handler, tier, msgs, cites=()):
    model = CFG['models'].get(tier) or CFG['models']['default']
    payload = {'model': model['name'], 'messages': msgs, 'stream': True, 'options': CFG['options']}
    if model.get('think') is not None: payload['think'] = model['think']
    try:
        try: resp = ollama('/api/chat', payload)
        except urllib.error.HTTPError as e:
            body = e.read().decode('utf-8', 'ignore')
            if 'think' in body.lower() and 'think' in payload:
                payload.pop('think'); resp = ollama('/api/chat', payload)
            else: raise RuntimeError(body[:300] or str(e))
        full = ''
        for line in resp:
            if not line.strip(): continue
            j = json.loads(line)
            if 'error' in j: raise RuntimeError(j['error'])
            t = (j.get('message') or {}).get('content') or ''
            if t: full += t; handler.wfile.write(t.encode()); handler.wfile.flush()
            if j.get('done'): break
        if cites and 'Textbook p.' not in full:   # deterministic page citation from the retrieved passages
            handler.wfile.write(('\n\n' + ' \u00b7 '.join('Textbook ' + c for c in cites)).encode()); handler.wfile.flush()
    except (BrokenPipeError, ConnectionResetError): return
    except Exception as e:
        try: handler.wfile.write(('\x00ERROR: ' + str(e)).encode()); handler.wfile.flush()
        except Exception: pass

class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        if self.path.startswith('/health'):
            try: models = [m['name'] for m in json.load(ollama('/api/tags', timeout=5))['models']]
            except Exception as e: models = ['OLLAMA NOT REACHABLE: %s' % e]
            body = json.dumps({'index': INDEX['status'], 'models': models, 'config': CFG['models']}, indent=1).encode()
            self.send_response(200); self.send_header('Content-Type', 'application/json'); self.end_headers(); self.wfile.write(body); return
        p = 'index.html' if self.path == '/' or self.path.startswith('/?') or self.path.startswith('/#') else self.path.lstrip('/').split('?')[0]
        fp = os.path.normpath(os.path.join(ROOT, p))
        if not fp.startswith(ROOT) or not os.path.isfile(fp) or p in ('config.json', 'index_cache.json', 'server.py') or p.startswith('book'):
            self.send_response(404); self.end_headers(); return
        data = open(fp, 'rb').read(); self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8' if fp.endswith('.html') else 'application/pdf' if fp.endswith('.pdf') else 'application/octet-stream')
        if fp.endswith('.pdf'): self.send_header('Content-Disposition', 'inline')
        self.send_header('Content-Length', str(len(data))); self.end_headers(); self.wfile.write(data)
    def do_POST(self):
        if self.path != '/ask': self.send_response(404); self.end_headers(); return
        try:
            body = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))))
            msgs, cites = build_messages(body['messages'], CFG['retrieval']['top_k'])
        except Exception as e:
            self.send_response(400); self.end_headers(); self.wfile.write(str(e).encode()); return
        self.send_response(200); self.send_header('Content-Type', 'text/plain; charset=utf-8'); self.send_header('Cache-Control', 'no-store'); self.end_headers()
        stream_answer(self, body.get('tier', 'default'), msgs, cites)

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--port', type=int, default=CFG['port']); ap.add_argument('--reindex', action='store_true'); a = ap.parse_args()
    if a.reindex and os.path.exists(os.path.join(ROOT, 'index_cache.json')): os.remove(os.path.join(ROOT, 'index_cache.json'))
    threading.Thread(target=build_index, daemon=True).start()
    srv = ThreadingHTTPServer(('127.0.0.1', a.port), H)
    print(f'Atlas running at http://127.0.0.1:{a.port}  (Ctrl+C to stop)')
    try: srv.serve_forever()
    except KeyboardInterrupt: pass
