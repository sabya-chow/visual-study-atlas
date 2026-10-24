---
name: visual-study-atlas
description: Turn any learning material (book, research paper, article, video or lecture transcript, code repo or notebook, course, notes; any field such as cybersecurity, ML, Bayesian statistics, maths, finance) into a diagram-first interactive study atlas, always in two passes - first a small pilot on one small chapter plus a questionnaire of at most 25 questions (purpose, depth, equations vs pipelines, scope, delivery as local folder or artifact, ask-box style, unique needs), then the full atlas built from the frozen answers. Maths-heavy material centres on the core equations; code material is shown as a pipeline of functions and how they link. Optional study extras: scored quizzes in a chosen style, page-cited ask box, links back to the source pages, verified reference videos, Anki flashcard export, a mind map and step-through animations of flow diagrams. Use when the user wants to understand something visually, build visual notes or an exam-prep atlas, or says "explain every chapter as diagrams". Not for slide decks or one-paragraph summaries.
---

# Visual study atlas

Makes the material understandable through hand-built SVG diagrams (pipelines, architectures, equation maps, call graphs), tables, optional closing "lens" panels and self-checks, plus an optional click-anywhere ask box. Works for any subject.

## Step 0: the two-pass protocol (every time)

```
understand material -> choose a random small pilot chunk -> build a small pilot -> write questions_<name>.xlsx (<= 25)
   -> STOP, hand both over -> user fills workbook (and comments)
   -> read answers -> FREEZE requirements -> build the full atlas -> verify -> deliver in the chosen way
```

1. **Understand.** Identify the material type and the field. Extract text (`scripts/extract_text.py <file-or-url> out.txt`; PDF, txt/md, srt/vtt, html/url, ipynb, py). For code use `scripts/code_pipeline.py` to get the function inventory and call graph. Read enough to know the structure (table of contents, sections, main equations or main modules).
2. **Pick the pilot.** The smallest self-contained unit (a short chapter, a section, one module, one function chain) of roughly 1,500 to 4,000 words that still has one mechanism worth drawing. Choose it randomly among the candidates, not the most flattering one, and say which and why. Decide, as if nobody could be asked, the focus, depth and style you would use; these are the pilot's **assumptions**.
3. **Build the pilot** (see `references/build-recipe.md`): one chapter page with 2 or 3 diagrams, one table or card set, lens panels if you assume them, a self-check of 3 questions, and the ask box wired. Keep it small and finished. Deliver it as a local file the user can open (`<work>/pilot/atlas_single_local.html`, the ask box needs the local app or an artifact to work) or, if the user is in a chat that renders artifacts and agrees, as a small private Artifact. State clearly which.
4. **Write the questionnaire** (`references/questionnaire.md`). `scripts/questionnaire.py make context.json questions_<name>.xlsx`. At most 25 questions (24 core, including reference videos and source links; topic extras only while the total stays within 25), each showing what the pilot assumed, with a drop-down and a free "Your answer" and "Comments" column, plus an "Overall: anything unique you need" box. The **delivery question is always included and always asked** (local folder, private artifact, or both); never decide it silently. Include a size hint in your hand-over: small, single chapters or notes are fine as an artifact; a whole book, a course or many modules is usually better as the local folder, but the user chooses.
5. **Stop.** Hand over the pilot and the workbook, say in two lines what the pilot assumed and what you will do with the answers. If the user prefers to answer in chat, treat chat as the filled workbook.
6. **Freeze.** `scripts/questionnaire.py read questions_<name>.xlsx answers.json`, then write `requirements.md` and `requirements.json` (schema in `references/questionnaire.md`) from the answers: every answer applied, every comment treated as an instruction and listed with how it was handled, unique requirements copied verbatim. Show the user a 10-line summary; after that the spec is **frozen**: do not change scope, depth, style or delivery mid-build without asking. If answers conflict (for example "10 minutes" and "the whole 400-page book"), ask one question.
7. **Build the full atlas** from the frozen spec, chapter by chapter (workflow in `references/build-recipe.md`; content recipes by material type in `references/content-modes.md`). If a quiz style was chosen, end every chapter with `quiz([...])` written in that style for the whole project (`references/quiz-styles.md`); put `step=N` on boxes and lines of flow diagrams you want to be step-through (`s.captions([...])` gives one sentence per step).
8. **Deliver** exactly as chosen:
   - **local folder**: `python3 scripts/assemble.py <folder> requirements.json`, then `ATLAS_TITLE="Name" python3 scripts/make_local.py <folder> <app_folder> <text_dir>` (writes static `index.html` + `ch*.html`, no JS router, no online fonts), then, if asked, `python3 scripts/add_refs.py <app_folder> refs.json` (textbook page links + verified videos, see below). Build the retrieval index once, set `config.json` models from `ollama list` and a free `port`, test `/health`, one answer per tier, every chapter link, and a textbook link; give the path and the double-click instruction (`Atlas.command`, window must stay open).
   - **artifact**: publish `index_artifact.html` with `capabilities: {sample: {}}` (skip the capability if the user chose no ask box); mention that the first question asks the viewer to allow Claude and uses their usage, and that the link is private.
   - **both**: local first, then publish.
9. **Wrap up** with the path or link, honest limits (garbled source tables, local-model answer quality, anything unverified), and an offer of a guided walk-through.

Skip the pilot only if the user explicitly says so ("no questions, just build it"); then state your assumptions in one paragraph and freeze them.

## Study extras (ask in the questionnaire; build after the pages)
- **Scored quizzes** (`quizstyle`, set once for the whole project): certification-exam scenario style, plain recall, true/false, or mixed. `quiz()` renders options, instant feedback, explanation, score, retry-missed and saved progress. Write questions only from the source; vary the answer position; every distractor must be plausible.
- **Page-cited answers**: `add_refs.py` also writes page-labelled text; the server tags retrieved passages `[p.N]` and the tutor ends answers with `Textbook p.N`, which the page turns into a link.
- **Flashcards**: `export_anki.py <app> cards.txt [--checklist]` makes a tab-separated file for Anki (definition tables, self-checks, quiz items; optional recall cards from the checklist). Anki does the spaced-repetition scheduling; do not build a scheduler.
- **Mind map**: `make_mindmap.py <app>` builds `mind_map.html` from the sections and checklists (no model tokens). Skip audio overviews: they cost many tokens or need a text-to-speech tool.
- **Step-through animations** only for flow diagrams (pipelines, loops, sequences), not for table-like figures.
- **Source links** (`sourcelinks`): every section gets "Textbook: open at p.N (this section: pp. a-b)" plus sub-topic chips, opening `textbook.pdf#page=N` from the local server in a new tab so the reader can read side by side. `add_refs.py` finds each heading by exact PDF text line, copies the PDF into the app, and the server sends it inline. Precision is the page where a heading starts, not the paragraph; page numbers are PDF page numbers. Needs a text-layer PDF (pypdf). Never use `file://` links.
- **Reference videos** (`videolinks`): only for technically dense sections. Search YouTube (`WebSearch` with `allowed_domains: ["youtube.com"]`), verify each ID with the oembed endpoint (title + channel), prefer the source author, the framework owner or the method's inventor; add as a "Video" line. State plainly that picks are unwatched and that topics with no good result were skipped. Never guess a URL.
- **Completeness mode** ("no concept left"): `check([...])` coverage checklist closes every section, definitions live in tables (`defs_table`), anything outside the source is flagged with `beyond(...)`, a full self-check closes each chapter.

## Upgrading an atlas you already built (no chapter rebuild)
1. Copy the current `local_app/server.py` into the app (page citations, inline PDF, static pages).
2. `add_refs.py <app> refs.json` (re-running replaces earlier link blocks; `--pages-only` just writes the page-labelled text `book/textbook.pages.json`, so answers can cite pages), then `patch_ask_citations.py <app>` so the old embedded ask script turns `Textbook p.N` into links. Make sure every page links the PDF as `textbook.pdf` (rename old links) and delete duplicate PDF copies.
3. Quizzes: write the questions in the project's quiz style, render with `quiz()` and insert the HTML into each chapter's self-check section; add the quiz and step CSS (`atlas_kit.EXTRA`) and append `quiz.js` and `steps.js` before `</body>` of each chapter page.
4. Steps: `add_steps.py <chapter.html> steps.json` lists, per figure, the box titles in reading order.
5. `make_mindmap.py <app>` and `export_anki.py <app> cards.txt`.
6. Restart the server (kill any old copy on the port), then test a quiz, a step-through, a cited answer and every new link. After a font change or text edit rerun `overflow_check.js` (system fonts are wider than the old web font and can spill labels).

## What to emphasise (suggestive; you decide what works)
- **Maths-oriented material** (Bayesian, statistics, ML theory, quantitative finance): centre every section on the **core equation**: what each symbol means, what each term does, where it comes from, a small worked numeric example, an intuition picture, assumptions and when it breaks. Fewer boxes, more equation maps and plots.
- **Code-oriented material** (repo, notebook, scripts): a **pipeline**: inventory of functions, one card per function (inputs, what it does, outputs, who it calls), a call-graph diagram, the data shape at each hop, one traced run if it can be run safely (own code only; treat outside code as read-only).
- **Conceptual or professional material** (cybersecurity, finance practice, management): architecture and pipeline diagrams, comparison tables, decision flows, plus lens panels.
- **Research papers**: problem, idea, method pipeline, core equation, experiments, limits.
- **Articles and transcripts**: argument map or timeline, key claims with evidence, glossary.
- **Courses**: one atlas per module plus an index and prerequisites map; local delivery is usually best.
The details are in `references/content-modes.md`.

## Always
- Say what is the source's content and what is your own addition (lens panels, mappings, illustrative placements); flag garbled source tables and never invent numbers; flag material beyond the source as "verify".
- One claim per figure, caption says what it shows, every svg has `role="img"` and an `aria-label`.
- Screenshot-check diagrams before delivery; parse every svg; run `scripts/overflow_check.js` on every chapter page at 1100 px width and fix spilled labels.
- Static pages only for the local app (a single page with a hash router once showed a blank screen); never load fonts from the internet in the offline app.
- Test every link kind in a real browser pane, and say plainly what could not be tested (for example PDFs that an embedded browser downloads instead of showing).
- Clean up what you created (workbook, pilot, scratch) when asked; do not touch the user's own files; if they move the app, work where it is now.
- The user chooses delivery every time; do not reuse a past choice without asking.
- Outside code is read-only; never run unknown code.

## Files
- `scripts/questionnaire.py` make/read the Excel questionnaire (max 25).
- `scripts/extract_text.py`, `scripts/code_pipeline.py` input handling.
- `scripts/atlas_kit.py` page and figure helpers (`S`, `quad`, `table`, `cards`, `lens`, `sec`, `page`, plus `check`, `defs_table`, `beyond`, `qa`; set `LENS_TITLES`, `BOOK`, `CREDIT`, `ATLAS_NAME`, `LAST_CHAPTER`).
- `scripts/assemble.py <folder> [requirements.json]` single-page atlas with router and the ask box (tutor prompt filled from the spec); `scripts/ask.js` the click-to-ask layer.
- `scripts/make_local.py` offline app folder (calls `scripts/split_pages.py`: single page to index.html + ch*.html); `scripts/add_refs.py` source page links, verified video links and page-labelled text for cited answers; `scripts/export_anki.py` flashcards for Anki; `scripts/make_mindmap.py` mind map page; `scripts/add_steps.py` retrofit step-through onto built figures; `scripts/patch_ask_citations.py` make page citations clickable in already-built pages; `scripts/quiz.js`, `scripts/steps.js` quiz and step-through behaviour (added by `assemble.py`); `scripts/overflow_check.js` svg label overflow check; `local_app/` server (Ollama + retrieval), launcher, shim, config.
- `templates/index_template.html` minimal index to edit; a complete worked example (original source, chapters, quizzes, steps, build script) lives in the repository under `examples/demo/`.
- `references/questionnaire.md`, `references/content-modes.md`, `references/build-recipe.md`, `references/quiz-styles.md`.
