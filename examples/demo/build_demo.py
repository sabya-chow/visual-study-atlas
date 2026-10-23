#!/usr/bin/env python3
"""Builds the demo atlas from source/home_budgeting_guide.pdf (original text). This file is also the reference for writing your own chapters:
sec() + one figure + defs_table() + check() per section, quiz() and a self-check per chapter, beyond() for anything not in the source,
step= on boxes/lines for step-through animation. Run: python3 make_source.py && python3 build_demo.py"""
import sys, os, json, subprocess, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
SK = os.path.abspath(os.path.join(HERE, '../../plugins/visual-study-atlas/skills/visual-study-atlas'))
sys.path.insert(0, os.path.join(SK, 'scripts'))
import atlas_kit as k
from atlas_kit import *
k.BOOK = 'A Short Guide to Home Budgeting'; k.CREDIT = 'Demo author'; k.ATLAS_NAME = 'Budgeting Atlas'; k.LAST_CHAPTER = 2; k.LENS_TITLES = ('', '')

# ---------- chapter 1 ----------
def f_flow():
    s = S('0 0 960 330', 'Money flow: income arrives, fixed, variable and irregular costs are paid or set aside, and what is left is the surplus.')
    s.box(20, 120, 170, 80, ['Income', 'after tax, per month'], 'dat', step=1)
    s.line([(190, 160), (250, 160)], step=2)
    for i, (t, d, kd, st) in enumerate([('Fixed costs', 'rent, loans, premiums', 'net', 2), ('Variable costs', 'food, fuel, fun', 'net', 3), ('Irregular costs', 'yearly bills / 12, set aside', 'net', 4)]):
        y = 20 + i * 100
        s.box(250, y, 290, 80, [t, d], kd, step=st)
        s.line([(250, 160), (230, 160), (230, y + 40), (250, y + 40)], step=st) if i else None
    s.line([(540, 60), (600, 160)], step=2); s.line([(540, 160), (600, 160)], step=3); s.line([(540, 260), (600, 160)], step=4)
    s.box(600, 120, 170, 80, ['Surplus', 'income minus costs'], 'ctl', step=5)
    s.box(790, 120, 150, 80, ['If negative', 'plan spends more', 'than it earns'], 'thr', step=5)
    s.line([(770, 160), (790, 160)], 'thr', step=5)
    s.captions(['Income arrives each month.', 'Fixed costs are paid first: they do not change.', 'Variable costs follow your choices.', 'Irregular costs: set aside yearly total divided by twelve.', 'What remains is the surplus; negative means overspending.'])
    return s.render('Read left to right. Irregular costs are the easy ones to forget, so they get their own monthly set-aside.')

def f_bucket():
    s = S('0 0 960 250', 'A stacked bar of the three-bucket rule of thumb: 50 percent needs, 30 percent wants, 20 percent savings, drawn to scale.')
    x = 40; W = 880
    for pct, name, kd in [(50, 'Needs', 'net'), (30, 'Wants', 'dat'), (20, 'Savings', 'ctl')]:
        w = W * pct / 100
        s.box(x, 50, w - 4, 110, [f'{name}  {pct}%'], kd); x += w
    s.text(480, 200, 'A starting draft, not a law: in an expensive city needs may exceed half.', 'sm')
    return s.render('Drawn to scale. Savings covers the emergency fund, retirement, goals and extra debt payments.')

def f_loop():
    s = S('0 0 960 250', 'The budgeting loop: plan at month start, record purchases, compare at month end, adjust categories, then repeat.')
    xs = [30, 270, 510, 750]; T = [('1 Plan', 'give every unit a job'), ('2 Record', 'soon after each purchase'), ('3 Compare', 'actual versus plan'), ('4 Adjust', 'fix categories wrong twice')]
    for i, x in enumerate(xs):
        s.box(x, 40, 180, 80, list(T[i]), ['net', 'net', 'dat', 'ctl'][i], step=i + 1)
        if i < 3: s.line([(x + 180, 80), (xs[i + 1], 80)], step=i + 2)
    s.line([(840, 120), (840, 190), (120, 190), (120, 120)], 'ctl', dash=True, step=4)
    s.text(480, 182, 'repeat every month', 'sm')
    s.captions(['Plan at the start of the month.', 'Record each purchase soon after.', 'At month end compare with the plan.', 'Adjust, then start the next loop.'])
    return s.render('Reviewing matters more than perfect recording: a category that is wrong two months running needs a new number.')

Q1 = [dict(q='Maya earns 3,000 after tax. Rent and loan payments are 1,400 and groceries are about 500. A 600 car service arrives once a year. What should she do first about the car bill?', opts=['Ignore it until it arrives', 'Set aside 50 a month (600 divided by 12)', 'Cut groceries to zero', 'Raise the savings bucket to 30 percent'], ans=1, why='Irregular costs are divided by twelve and set aside monthly so they never become a surprise.'),
      dict(q='A household in a high-rent city spends 62 percent of income on needs. Which statement about the 50/30/20 split is the BEST?', opts=['The household is breaking a rule and must move', 'The split is a rule of thumb; adjust the other buckets to fit', 'Savings should be set to zero permanently', 'Wants must still be 30 percent'], ans=1, why='It is a starting draft, not a law; needs can exceed half and the other buckets shrink.'),
      dict(q='Two months in a row, the dining-out category ended 80 over plan. What does the loop suggest?', opts=['Try harder next month', 'Stop recording purchases', 'Adjust the category to a realistic number', 'Delete the category'], ans=2, why='A category wrong twice needs a new number, not more willpower.')]
SC1 = [('What is the surplus?', 'Income left after fixed, variable and irregular costs; negative means the plan overspends.'), ('What is zero-based budgeting?', 'Every unit of income gets a job so income minus planned spending equals zero; savings count as a job.')]

def ch1():
    S_ = []
    S_.append(sec('s1', 'SECTION 1', 'Income and spending', 'Money arrives as income and leaves as three kinds of cost; what remains is the surplus.', f_flow() + defs_table([('Fixed costs', 'Same every month: rent, loan payments, insurance premiums.'), ('Variable costs', 'Change with your choices: groceries, fuel, entertainment.'), ('Irregular costs', 'Arrive a few times a year: repairs, annual subscriptions, gifts. Divide the yearly total by twelve and set it aside monthly.'), ('Surplus', 'What is left after all three; negative means the plan spends more than it earns.')]) + check(['Budget = plan for where income goes', 'Fixed, variable, irregular costs', 'Irregular costs cause surprises: yearly total / 12', 'Surplus and negative surplus'])))
    S_.append(sec('s2', 'SECTION 2', 'The three-bucket rule of thumb', 'Split after-tax income into needs, wants and savings; 50/30/20 is a first draft, not a law.', f_bucket() + defs_table([('Needs', 'What you must pay to live and work.'), ('Wants', 'What you choose.'), ('Savings', 'Emergency fund, retirement, goals, extra debt payments.')]) + beyond('Other splits exist (for example 60/20/20); pick the one that fits your costs.') + check(['Three buckets', '50/30/20 as a common start', 'Rule of thumb, not a law', 'Expensive cities push needs above half'])))
    S_.append(sec('s3', 'SECTION 3', 'Tracking and reviewing', 'A budget is a four-step loop; zero-based budgeting gives every unit of income a job.', f_loop() + check(['Plan, record, compare, adjust', 'Zero-based budgeting', 'Savings are a planned job', 'Review matters more than perfect recording', 'Wrong two months in a row: change the number'])))
    S_.append(sec('s4', 'SECTION 4', 'Quiz and self-check', 'Scenario questions, scored. Pick the BEST answer.', quiz(Q1, 'ch1-quiz', 'Chapter 1 quiz') + qa(SC1)))
    return S_

# ---------- chapter 2 ----------
def f_fund():
    s = S('0 0 960 280', 'Emergency fund target drawn to scale for essential costs of 2,000 a month: one month 2,000, three months 6,000, six months 12,000.')
    for i, (m, lab) in enumerate([(1, 'Start: 1 month'), (3, 'Typical low: 3 months'), (6, 'Typical high: 6 months')]):
        w = 620 * m / 6; y = 30 + i * 70
        s.text(30, y + 26, lab, 'sm', 'start'); s.raw(f'<rect x="260" y="{y}" width="{w}" height="40" rx="6" class="bar {"datb" if i == 0 else "thrb" if i == 2 else "datb"}"/>'); s.text(260 + w + 10, y + 26, f'{2000 * m:,}', 'tt', 'start')
    s.text(480, 250, 'Keep it in a separate, reachable account; refill after use.', 'sm')
    return s.render('Bars are to scale. Starting with one month beats waiting until you can save the full amount.')

def f_debt():
    s = S('0 0 960 300', 'Compound interest on an unpaid balance of 1,000 at 2 percent a month, drawn to scale for six months.')
    b = 1000.0; x0 = 60
    for i in range(7):
        w = 800 * (b / 1130); y = 20 + i * 38
        s.text(40, y + 20, f'M{i}', 'sm', 'end'); s.raw(f'<rect x="{x0}" y="{y}" width="{w:.1f}" height="26" rx="4" class="bar datb"/>'); s.text(x0 + w + 8, y + 19, f'{b:,.2f}', 'sm', 'start'); b *= 1.02
    return s.render('Each month interest is charged on the larger balance, so the bars grow faster over time. Values computed, not decorative.')

def f_risk():
    s = S('0 0 960 280', 'Insurance as risk transfer: you pay a small regular premium; for a large rare loss you pay the deductible and the insurer pays the rest.')
    s.box(30, 100, 200, 80, ['You', 'pay the premium monthly'], 'dat', step=1); s.line([(230, 140), (380, 140)], step=1)
    s.box(380, 100, 200, 80, ['Insurer', 'pools many small premiums'], 'net', step=1)
    s.box(380, 10, 200, 60, ['Rare large loss', 'fire, illness, liability'], 'thr', step=2); s.line([(480, 70), (480, 100)], 'thr', step=2)
    s.line([(580, 140), (730, 140)], 'ctl', step=3); s.box(730, 100, 200, 80, ['Pays above deductible', 'you pay the first part'], 'ctl', step=3)
    s.box(30, 210, 900, 50, ['Emergency fund + insurance', 'the fund covers deductibles and small events; insurance covers the large ones'], 'bx', step=4)
    s.captions(['You pay a regular, small premium.', 'A rare, large loss happens.', 'The insurer pays above your deductible.', 'The emergency fund covers the deductible and small events.'])
    return s.render('Insure what would be a disaster; skip cover for mere inconveniences.')

Q2 = [dict(q='Dev spends 1,800 a month on essentials and has 2,000 saved. He can afford a deposit for a new gadget (500). What is the BEST move?', opts=['Use the emergency fund for the gadget', 'Cancel insurance to free cash', 'Keep building the fund toward 3 months before the gadget', 'Borrow for the gadget and stop saving'], ans=2, why='The emergency fund is not for planned purchases; the target is three to six months of essentials.'),
      dict(q='Priya has two debts: 4,000 at 18 percent and 300 at 9 percent. She wants to minimise total interest. Which method fits?', opts=['Snowball', 'Avalanche', 'Pay both equally', 'Ignore interest'], ans=1, why='Avalanche pays the highest rate first and saves the most interest; snowball is about quick wins.'),
      dict(q='A 400 phone-case warranty is offered. Which statement is BEST?', opts=['Insure everything small', 'Always buy because insurers are cheap', 'Buy and cancel health cover', 'Skip it: an inconvenience, not a disaster'], ans=3, why='Insure the risks that would be a disaster; skip cover for inconveniences.')]
SC2 = [('What does a deductible do?', 'It is the amount you pay first before the insurer pays.'), ('Why does compound interest grow faster?', 'Unpaid interest is added to the balance, so the next charge is on a larger amount.')]

def ch2():
    S_ = []
    S_.append(sec('s1', 'SECTION 1', 'The emergency fund', 'A cash reserve of three to six months of essential costs, kept separate and reachable.', f_fund() + defs_table([('Emergency fund', 'Cash reserve for surprises such as job loss or a medical bill; not for planned purchases.'), ('Target', 'Three to six months of essential costs; start with one month.')]) + check(['Purpose', 'Target size and a worked example', 'Separate, reachable account', 'Refill after use'])))
    S_.append(sec('s2', 'SECTION 2', 'Debt basics', 'Interest is the price of borrowing; compounding makes unpaid balances grow faster.', f_debt() + defs_table([('Compound interest', 'Unpaid interest is added to the balance, so the next charge is on a larger amount.'), ('Avalanche', 'Pay the highest interest rate first; saves the most interest.'), ('Snowball', 'Pay the smallest balance first; quick wins.')]) + beyond('Real loans may compound daily or have fees; check your loan terms.') + check(['Interest = price of borrowing', 'Compounding with 1,000 at 2 percent example', 'Avalanche vs snowball', 'Choose one and keep to it'])))
    S_.append(sec('s3', 'SECTION 3', 'Insurance and risk transfer', 'Insurance moves a rare, large cost to a company for a small regular premium.', f_risk() + defs_table([('Premium', 'The regular payment to the insurer.'), ('Deductible', 'The amount you pay first before the insurer pays.')]) + check(['Premium and deductible', 'Insure disasters, skip inconveniences', 'Fund and insurance work together'])))
    S_.append(sec('s4', 'SECTION 4', 'Quiz and self-check', 'Scenario questions, scored. Pick the BEST answer.', quiz(Q2, 'ch2-quiz', 'Chapter 2 quiz') + qa(SC2)))
    return S_

def finish(n, title, intro, secs):
    h = page(n, title, intro, secs, '', label=f'Chapter {n}')
    return h

if __name__ == '__main__':
    work = os.path.join(HERE, '_build'); shutil.rmtree(work, ignore_errors=True); os.makedirs(work)
    open(os.path.join(work, 'ch1.html'), 'w').write(finish(1, 'Where the money goes', 'Income, the three-bucket rule of thumb, and the budgeting loop.', ch1()))
    open(os.path.join(work, 'ch2.html'), 'w').write(finish(2, 'Safety nets', 'Emergency fund, debt basics and insurance.', ch2()))
    sys.path.insert(0, HERE)
    cards_ = ''.join(f'<a class="chap" href="ch{n}.html"><span class="cn">{n}</span><span class="ct"><b>{t_}</b><span>{d_}</span></span></a>' for n, t_, d_ in [(1, 'Where the money goes', 'Income, the three-bucket rule of thumb, the budgeting loop.'), (2, 'Safety nets', 'Emergency fund, debt basics, insurance.')])
    xcss = ('.chaps{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.chap{display:flex;gap:14px;padding:14px 16px;border:1px solid var(--line);border-radius:10px;background:var(--surface);color:var(--fg);text-decoration:none}'
            '.cn{font:800 28px var(--disp);color:var(--ctl)}.ct{display:flex;flex-direction:column;gap:4px}.ct span{font-size:14px;color:var(--muted)}@media(max-width:760px){.chaps{grid-template-columns:1fr}}')
    body_ = ('<header><div class="wrap"><div class="eyebrow">Study atlas &middot; demo</div><h1>Budgeting Atlas</h1><p class="lead">A tiny demo built from an original three-page source. Diagrams, definition tables, coverage checklists, scored quizzes, flashcards and a mind map.</p></div></header>'
             f'<div class="wrap"><section id="chapters"><div class="sec-n">CHAPTERS</div><h2>Pick a chapter</h2><div class="chaps">{cards_}</div></section></div>')
    open(os.path.join(work, 'index.html'), 'w').write('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">' + k.HEAD.replace('Study Atlas', 'Budgeting Atlas') + '<style>' + k.CSS + k.EXTRA + xcss + '</style></head><body>' + body_ + '</body></html>')
    json.dump({'source': 'A Short Guide to Home Budgeting (demo)', 'reader': 'The reader is a beginner who wants to understand budgeting basics in plain English.', 'length': 'usually 110 to 170 words', 'mathnote': 'Use small numbers.', 'lensnote': 'If useful, add a one-line everyday example.', 'lenses': 'none'}, open(os.path.join(work, 'req.json'), 'w'))
    run = lambda *a, **kw: subprocess.run(list(a), check=True, **kw)
    run(sys.executable, os.path.join(SK, 'scripts/assemble.py'), work, os.path.join(work, 'req.json'))
    app = os.path.join(HERE, 'app'); shutil.rmtree(app, ignore_errors=True)
    txt = os.path.join(work, 'txt'); os.makedirs(txt)
    from pypdf import PdfReader
    open(os.path.join(txt, 'guide.txt'), 'w').write('\n'.join(p.extract_text() for p in PdfReader(os.path.join(HERE, 'source/home_budgeting_guide.pdf')).pages))
    env = dict(os.environ, ATLAS_TITLE='Budgeting Atlas')
    run(sys.executable, os.path.join(SK, 'scripts/make_local.py'), work, app, txt, env=env)
    refs = {'pdf': os.path.join(HERE, 'source/home_budgeting_guide.pdf'), 'ranges': {'ch1': [2, 3], 'ch2': [3, 4]},
            'sections': {'ch1-s1': {'heading': 'Income and Spending'}, 'ch1-s2': {'heading': 'The Three-Bucket Rule of Thumb'}, 'ch1-s3': {'heading': 'Tracking and Reviewing'},
                         'ch2-s1': {'heading': 'The Emergency Fund'}, 'ch2-s2': {'heading': 'Debt Basics'}, 'ch2-s3': {'heading': 'Insurance and Risk Transfer'}}}
    json.dump(refs, open(os.path.join(work, 'refs.json'), 'w'))
    cp = os.path.join(app, 'config.json'); cfg = json.load(open(cp)); cfg['port'] = 8801; json.dump(cfg, open(cp, 'w'), indent=2)
    run(sys.executable, os.path.join(SK, 'scripts/add_refs.py'), app, os.path.join(work, 'refs.json'), '--no-verify')
    run(sys.executable, os.path.join(SK, 'scripts/make_mindmap.py'), app, '--title', 'Budgeting Atlas')
    run(sys.executable, os.path.join(SK, 'scripts/export_anki.py'), app, os.path.join(HERE, 'budgeting_flashcards.txt'))
    shutil.rmtree(work)
    print('demo app ->', app)
