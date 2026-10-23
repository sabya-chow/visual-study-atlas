#!/usr/bin/env python3
"""Function inventory for code-focused material (Python).
  code_pipeline.py <file-or-dir> <out.json>
For each function: file, signature, docstring first line, calls to other functions defined in the same project,
so you can draw the call graph and a 'function card' (input, does, output, calls) per function."""
import ast, sys, os, json
src, out = sys.argv[1], sys.argv[2]
files = [src] if os.path.isfile(src) else [os.path.join(r, f) for r, _, fs in os.walk(src) for f in fs if f.endswith('.py')]
funcs = {}
trees = {}
for f in files:
    try: trees[f] = ast.parse(open(f).read())
    except Exception: continue
    for n in ast.walk(trees[f]):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            funcs[n.name] = {'file': os.path.relpath(f, os.path.dirname(src) if os.path.isfile(src) else src), 'line': n.lineno, 'args': [a.arg for a in n.args.args], 'doc': (ast.get_docstring(n) or '').split('\n')[0], 'returns': ast.unparse(n.returns) if n.returns else '', 'calls': []}
for f, t in trees.items():
    for n in ast.walk(t):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for c in ast.walk(n):
                if isinstance(c, ast.Call):
                    nm = c.func.id if isinstance(c.func, ast.Name) else (c.func.attr if isinstance(c.func, ast.Attribute) else None)
                    if nm in funcs and nm != n.name and nm not in funcs[n.name]['calls']: funcs[n.name]['calls'].append(nm)
json.dump(funcs, open(out, 'w'), indent=1); print(len(funcs), 'functions ->', out)
