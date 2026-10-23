#!/usr/bin/env python3
"""Split the single-page atlas (views switched by a JS hash router) into plain static pages:
index.html, ch1.html, ch2.html, ... (appendix.html). Why: static pages need no JS routing, so a link can never
leave a blank screen; each page carries its own <style>, <title>, the local shim and the ask script.
Also removes any Google Fonts link (an online stylesheet can stall rendering of an offline app).
Usage: split_pages.py <single_page.html> <out_folder> [--title "Atlas name"]
Library: split(html_text, out_folder, title='Atlas')"""
import re, os, sys

def split(t, out, title='Atlas'):
    b0 = t.index('<body>'); head = t[:b0]; body = t[b0 + 6:]
    first = body.index('<div class="view"'); pre = body[:first]
    st = re.search(r'<style>.*?</style>', pre, re.S).group(0)
    shim = re.search(r'<script>.*?</script>', pre, re.S)
    shim = shim.group(0) if shim else ''
    scripts = re.findall(r'<script>.*?</script>', body[first:], re.S)
    main = ''.join(scripts)   # ask box + quiz scripts (after the views)
    # no router: only scroll to #anchor
    main = re.sub(r"window\.addEventListener\('hashchange', route\); route\(\);",
                  "if (location.hash) { var e0 = document.getElementById(decodeURIComponent(location.hash.slice(1))); if (e0) e0.scrollIntoView(); }", main)
    head = re.sub(r'<link rel="(preconnect|stylesheet)"[^>]*>', '', head)
    head = re.sub(r'<meta name="claude:viewport-fit-sides"[^>]*>', '', head)
    views = re.findall(r'<div class="view" id="v-(\w+)"[^>]*>(.*?)</div>(?=<div class="view"|<script>)', body, re.S)
    ids = [v for v, _ in views]
    os.makedirs(out, exist_ok=True)
    for vid, c in views:
        c = re.sub(r'href="#index"', 'href="index.html"', c)
        c = re.sub(r'href="#(ch\d+|appendix)"', r'href="\1.html"', c)
        if vid == 'index':  # table-of-sections links: ch1.html#s3 -> ch1.html#ch1-s3
            c = re.sub(r'href="((?:ch\d+|appendix))\.html#(s\d+)"', r'href="\1.html#\1-\2"', c)
        name = title if vid == 'index' else f'{title}: ' + ('Appendix' if vid == 'appendix' else 'Chapter ' + vid[2:])
        page = head + f'<title>{name}</title>' + st + '</head><body>' + shim + f'<div class="view" id="v-{vid}">' + c + '</div>' + main + '</body></html>'
        open(os.path.join(out, vid + '.html'), 'w', encoding='utf-8').write(page)
    return ids

if __name__ == '__main__':
    a = sys.argv; ttl = a[a.index('--title') + 1] if '--title' in a else 'Atlas'
    print(split(open(a[1], encoding='utf-8').read(), a[2], ttl))
