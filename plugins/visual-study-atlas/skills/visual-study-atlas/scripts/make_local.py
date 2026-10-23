#!/usr/bin/env python3
"""Build the local, offline app folder from an assembled atlas.
Usage: make_local.py <atlas_folder_with_atlas_single_local.html> <output_folder> [book_text_dir]
Creates index.html + ch*.html (static pages with the Ollama shim; no JS router), server.py, config.json, Atlas.command, README.md, book/ (optional text for retrieval)."""
import sys, os, shutil, re
src, out = sys.argv[1], sys.argv[2]
book = sys.argv[3] if len(sys.argv) > 3 else None
K = os.path.dirname(os.path.abspath(__file__)); A = os.path.join(K, '..', 'local_app')
os.makedirs(out, exist_ok=True)
h = open(os.path.join(src, 'atlas_single_local.html')).read()
h = h.replace("(ERR[e && e.code] || ERR.upstream_error)", "(ERR[e && e.code] || ERR.upstream_error) + (e && e.message && e.code === 'upstream_error' ? ' (' + e.message + ')' : '')")
shim = open(os.path.join(A, 'local_shim.html')).read()
h = h.replace('<body>', '<body>' + shim, 1)
sys.path.insert(0, K)
from split_pages import split
split(h, out, os.environ.get('ATLAS_TITLE', 'Atlas'))
for f in ('server.py', 'config.json', 'Atlas.command', 'README.md'):
    shutil.copy(os.path.join(A, f), os.path.join(out, f))
os.chmod(os.path.join(out, 'Atlas.command'), 0o755); os.chmod(os.path.join(out, 'server.py'), 0o755)
if book and os.path.isdir(book):
    os.makedirs(os.path.join(out, 'book'), exist_ok=True)
    for f in os.listdir(book):
        if f.endswith('.txt'): shutil.copy(os.path.join(book, f), os.path.join(out, 'book', f))
print('local app written to', out)
