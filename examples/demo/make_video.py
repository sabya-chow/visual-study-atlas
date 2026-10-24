#!/usr/bin/env python3
"""Builds demo.mp4 from real screen captures of the demo app (video_frames/) plus title, flashcard and end cards.
Needs opencv-python, Pillow, numpy and imageio-ffmpeg; narration uses the macOS `say` voice (set VOICE=...). All content shown is the original demo content."""
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

NARR = [
 "This is Visual Study Atlas, a Claude Code skill that turns any learning material into an offline, diagram-first study atlas. This short demo uses an original three-page sample text about home budgeting.",
 "The atlas has one page per chapter, and everything runs on your own computer.",
 "Each chapter opens with a section index and a colour key.",
 "Every section has one claim and one picture, plus a link back to the page of your own source document.",
 "Flow diagrams can be stepped through one box at a time, so you see the sequence build up.",
 "Tables hold every definition, and a coverage checklist shows that nothing was skipped.",
 "Scored quizzes follow the style you chose at the start, with an explanation for every question.",
 "Click anything on the page to ask a question. A local model on your machine answers, with no cloud and no account.",
 "Answers come in plain English, with an example.",
 "Answers cite the source page, and the link opens your own PDF at that page.",
 "Here the link opens the demo source at that page.",
 "A mind map is built from the same structure. Click a section to see its checklist.",
 "Flashcards are exported for Anki, which handles the spaced repetition for you.",
 "To install, add the marketplace from GitHub, install the plugin, and run the skill. All demo content is original. Bring your own sources."]
VOICE = os.environ.get('VOICE', 'Samantha')

S = [card(['Visual Study Atlas'], ['Turn any learning material into an offline, diagram-first study atlas', 'Demo built from an original three-page text'])]
caps = ['Pilot first, then a full atlas: one page per chapter, all offline', 'Every chapter opens with a section index and a colour key', 'One claim and one picture per section, with a link back to the source page',
        'Flow diagrams can be stepped through one box at a time', 'Tables hold every definition; a checklist shows nothing was skipped', 'Scored quizzes in the style chosen at the start, with an explanation for each',
        'Click anything to ask a local model: no cloud, no account', 'Answers come in plain English with an example', 'Answers cite the source page; the link opens your own PDF there']
for i, c in enumerate(caps, 1): S.append(shot(os.path.join(HERE, 'video_frames', f'{i:02d}.png'), c, i))
S.append(shot(os.path.join(HERE, 'video_frames', 'textbook_page-3.png'), 'The textbook link opens the PDF at that page (demo source shown)', 10))
S.append(shot(os.path.join(HERE, 'video_frames', '10.png'), 'A mind map built from the same structure: click a section for its checklist', 11))
S.append(flash())
S.append(card(['Install', 'then run /visual-study-atlas'], ['/plugin marketplace add sabya-chow/visual-study-atlas', '/plugin install visual-study-atlas@visual-study-atlas-marketplace', 'All demo content is original (CC0). Bring your own sources.']))
assert len(S) == len(NARR)

import subprocess, tempfile, wave, imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe(); tmp = tempfile.mkdtemp(); SR = 22050; PAD = 0.7
clips = []
for i, txt in enumerate(NARR):
    a = os.path.join(tmp, f'{i}.aiff'); w = os.path.join(tmp, f'{i}.wav')
    subprocess.run(['say', '-v', VOICE, '-r', '165', '-o', a, txt], check=True)
    subprocess.run([FF, '-y', '-loglevel', 'error', '-i', a, '-ar', str(SR), '-ac', '1', w], check=True)
    with wave.open(w) as wf: raw = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
    clips.append(raw)
holds = [max(3.0, len(c) / SR + PAD) for c in clips]
TR = 9  # crossfade frames
vid = os.path.join(tmp, 'silent.mp4'); vw = None
for codec in ('avc1', 'mp4v'):
    vw = cv2.VideoWriter(vid, cv2.VideoWriter_fourcc(*codec), FPS, (W, H))
    if vw.isOpened(): break
audio = np.zeros(0, dtype=np.int16); prev = None
for im, hold, clip in zip(S, holds, clips):
    fr = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)
    if prev is not None:
        for k in range(1, TR): vw.write(cv2.addWeighted(prev, 1 - k / TR, fr, k / TR, 0))
        audio = np.concatenate([audio, np.zeros(int((TR - 1) / FPS * SR), dtype=np.int16)])
    for _ in range(int(hold * FPS)): vw.write(fr)
    seg = np.zeros(int(int(hold * FPS) / FPS * SR), dtype=np.int16); seg[:len(clip)] = clip[:len(seg)]
    audio = np.concatenate([audio, seg]); prev = fr
vw.release()
wavp = os.path.join(tmp, 'all.wav')
with wave.open(wavp, 'wb') as wf: wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes(audio.tobytes())
out = os.path.join(HERE, 'demo.mp4')
subprocess.run([FF, '-y', '-loglevel', 'error', '-i', vid, '-i', wavp, '-c:v', 'copy', '-c:a', 'aac', '-b:a', '128k', '-shortest', out], check=True)
print('wrote', out, round(os.path.getsize(out) / 1e6, 2), 'MB', 'voice', VOICE)
