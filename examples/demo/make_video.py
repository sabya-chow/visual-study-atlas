#!/usr/bin/env python3
"""Builds demo.mp4 from real screen captures of the demo app (video_frames/) plus title, flashcard and end cards.
Needs opencv-python and Pillow. All content shown is the original demo content."""
import os, cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); W, H, FPS = 1280, 720, 24
def font(sz, bold=False):
    for p in ('/System/Library/Fonts/Supplemental/Arial Bold.ttf' if bold else '/System/Library/Fonts/Supplemental/Arial.ttf', '/Library/Fonts/Arial.ttf', 'DejaVuSans.ttf'):
        try: return ImageFont.truetype(p, sz)
        except OSError: pass
    return ImageFont.load_default()
BG, FG, ACC = (242, 245, 248), (18, 32, 44), (11, 122, 117)

def card(lines, sub=None):
    im = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(im); y = H // 2 - 40 * len(lines)
    for ln in lines: d.text((W // 2, y), ln, font=font(54, True), fill=FG, anchor='mm'); y += 78
    if sub:
        for s in sub: d.text((W // 2, y + 30), s, font=font(28), fill=ACC, anchor='mm'); y += 44
    return im

def shot(path, caption, n):
    im = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(im)
    fr = Image.open(path).convert('RGB'); sc = 590 / fr.height; fr = fr.resize((int(fr.width * sc), 590), Image.LANCZOS)
    im.paste(fr, ((W - fr.width) // 2, 16)); d.rectangle([0, 620, W, H], fill=FG)
    d.text((40, 650), f'{n}', font=font(30, True), fill=ACC, anchor='lm'); d.text((90, 650), caption, font=font(27), fill=(255, 255, 255), anchor='lm')
    return im

def flash():
    rows = [l.rstrip('\n').split('\t') for l in open(os.path.join(HERE, 'budgeting_flashcards.txt'), encoding='utf-8') if not l.startswith('#')][:5]
    im = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(im); d.text((W // 2, 70), 'budgeting_flashcards.txt  (import into Anki)', font=font(30, True), fill=FG, anchor='mm'); y = 130
    import re
    for a, b, t in rows:
        b = re.sub('<[^>]+>', ' ', b)[:78]
        d.rounded_rectangle([90, y, W - 90, y + 88], 12, fill=(255, 255, 255), outline=(195, 207, 218)); d.text((120, y + 28), a[:60], font=font(26, True), fill=FG, anchor='lm'); d.text((120, y + 62), b, font=font(22), fill=(77, 97, 118), anchor='lm'); y += 104
    return im

S = [(card(['Visual Study Atlas'], ['Turn any learning material into an offline, diagram-first study atlas', 'Demo built from an original three-page text']), 3.5)]
caps = ['Pilot first, then a full atlas: one page per chapter, all offline', 'Every chapter opens with a section index and a colour key', 'One claim and one picture per section, with a link back to the source page',
        'Flow diagrams can be stepped through one box at a time', 'Tables hold every definition; a checklist shows nothing was skipped', 'Scored quizzes in the style chosen at the start, with an explanation for each',
        'Click anything to ask a local model: no cloud, no account', 'Answers come in plain English with an example', 'Answers cite the source page; the link opens your own PDF there']
for i, c in enumerate(caps, 1): S.append((shot(os.path.join(HERE, 'video_frames', f'{i:02d}.png'), c, i), 4.0 if i not in (8,) else 3.2))
S.append((shot(os.path.join(HERE, 'video_frames', 'textbook_page-3.png'), 'The textbook link opens the PDF at that page (demo source shown)', 10), 3.6))
S.append((shot(os.path.join(HERE, 'video_frames', '10.png'), 'A mind map built from the same structure: click a section for its checklist', 11), 3.6))
S.append((flash(), 3.8))
S.append((card(['Install', 'then run /visual-study-atlas'], ['/plugin marketplace add sabya-chow/visual-study-atlas', '/plugin install visual-study-atlas@visual-study-atlas-marketplace', 'All demo content is original (CC0). Bring your own sources.']), 5.0))

out = os.path.join(HERE, 'demo.mp4')
vw = None
for codec in ('avc1', 'mp4v'):
    vw = cv2.VideoWriter(out, cv2.VideoWriter_fourcc(*codec), FPS, (W, H))
    if vw.isOpened(): print('codec', codec); break
prev = None
for im, secs in S:
    fr = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)
    if prev is not None:
        for k in range(1, 9): vw.write(cv2.addWeighted(prev, 1 - k / 9, fr, k / 9, 0))
    for _ in range(int(secs * FPS)): vw.write(fr)
    prev = fr
vw.release(); print('wrote', out, round(os.path.getsize(out) / 1e6, 2), 'MB')
