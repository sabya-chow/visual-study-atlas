# Visual Study Atlas

A [Claude Code](https://claude.com/claude-code) skill that turns learning material (a book, paper, transcript, notes, a code repo) into a **diagram-first, offline study atlas**: one page per chapter, hand-built SVG diagrams, definition tables, a coverage checklist per section, scored quizzes, a click-anywhere ask box that runs on a local model, and links back to the page of your own copy of the source.

**Demo (about 90 seconds, narrated with a text-to-speech voice):** [watch demo.mp4](https://github.com/sabya-chow/visual-study-atlas/blob/main/examples/demo/demo.mp4). It is made from screen captures of the app built out of an original three-page sample text in [examples/demo](examples/demo).

## What you get

| Feature | What it does |
|---|---|
| Pilot first | Builds one small chapter and a questionnaire (max 25 questions) before the full build; your answers are frozen as the spec |
| Diagrams | Pipelines, loops, architectures, bar charts drawn to scale; every SVG has an accessible label; an overflow checker catches spilled text |
| Coverage checklist | Closes every section so you can check nothing was skipped; anything outside the source is flagged "Beyond the book: verify" |
| Scored quizzes | Style chosen once for the whole project (exam-style scenarios, plain recall, true/false, mixed); instant explanation, score, retry missed, saved progress |
| Ask box | Click any sentence, table cell or diagram box and ask. Runs on a local Ollama model, fully offline. Answers cite `Textbook p.N`, linked to your PDF |
| Source links | Every section links to the page where it starts in your own PDF, with sub-topic chips |
| Flashcards | `export_anki.py` writes a file Anki imports (definitions, self-checks, quiz items) |
| Mind map | `make_mindmap.py` builds a clickable mind map from the sections and checklists |
| Step-through diagrams | Flow diagrams can be stepped through one box at a time |
| Reference videos (optional) | Verified YouTube links on dense sections; unwatched picks, clearly labelled |

## Install

As a plugin from this repository:

```
/plugin marketplace add sabya-chow/visual-study-atlas
/plugin install visual-study-atlas@visual-study-atlas-marketplace
```

Or copy `plugins/visual-study-atlas/skills/visual-study-atlas` to `~/.claude/skills/visual-study-atlas`.

Python 3.9+ and `pip install -r requirements.txt` (`openpyxl`, `pypdf`). For the local ask box install [Ollama](https://ollama.com) with a chat model and `nomic-embed-text`; set the model names in the generated `config.json`.

## Use

In Claude Code, run `/visual-study-atlas` and point it at your material. The skill:

1. reads the material and builds a small **pilot** plus a questionnaire workbook, then stops;
2. after you fill the workbook, **freezes** the spec and builds the full atlas;
3. delivers a local folder: double-click `Atlas.command`, keep that window open, and read at `http://127.0.0.1:<port>`.

Try the finished sample first: `cd examples/demo/app && python3 server.py` (needs Ollama only for the ask box), or rebuild it with `python3 examples/demo/make_source.py && python3 examples/demo/build_demo.py`.

## Repository map

```
.claude-plugin/marketplace.json          plugin marketplace entry
plugins/visual-study-atlas/               the plugin
  skills/visual-study-atlas/SKILL.md      the skill (protocol, extras, rules)
  skills/visual-study-atlas/scripts/      kit, assemble, make_local, split_pages, add_refs, export_anki, make_mindmap, quiz.js, steps.js, overflow_check.js, ...
  skills/visual-study-atlas/local_app/    offline server (Ollama + retrieval), launcher, shim
  skills/visual-study-atlas/references/   questionnaire, build recipe, content modes, quiz styles
examples/demo/                            original sample source, builder, built app, flashcards, video
COPYRIGHT_AND_USE.md                      what is and is not included; responsible use
```

## Responsible use

This repository contains tooling and original demo content only. Bring sources you are allowed to use, and do not publish atlases built from copyrighted material. Read [COPYRIGHT_AND_USE.md](COPYRIGHT_AND_USE.md).

## Limits

- Local models can be wrong; check facts against your source. Page links land on the page where a heading starts, not the paragraph.
- Source links need a PDF with a text layer.
- Reference videos are picked from titles and channels, not watched.
- The step-through animation suits flow diagrams, not table-like figures.

## License

MIT. Demo content is original and also CC0.
