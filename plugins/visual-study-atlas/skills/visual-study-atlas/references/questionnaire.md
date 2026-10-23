# Questionnaire (max 25) and the frozen spec

`scripts/questionnaire.py make context.json questions_<name>.xlsx`. context.json:
```json
{"topic": "...", "material": "...", "pilot": "what the pilot covered",
 "assumed": {"depth": "working understanding", "focus": "core equations first", "delivery": "local folder (offline, runs from Finder)"},
 "drop": ["language"], "extra": [{"id": "dataset", "question": "Which dataset should recur?", "choices": ["coin", "medical test"], "assumed": "medical test"}]}
```
24 core questions: material, purpose, target (exam/role/audience), prior knowledge, depth, focus (equations vs pipelines), maths level, code level, scope, must include, leave out, visuals, examples, lenses, self-check, ask box yes/no, ask style, **delivery (always)**, reference videos, source links, ask engine (local Ollama / Claude / none), look, language and tone, pilot feedback. Drop what does not apply; add extras only while the total stays at 25 or fewer (the maker truncates at 25).
Add an "Overall" free-text for unique requirements.

## Answer to decision table
| Answer | Decision |
|---|---|
| purpose = pass an exam | lens panel A named after the exam (e.g. "<Exam> lens"), self-check with worked answers, coverage map |
| purpose = job role | lens panel B named "<Role> asks" with evidence/practice questions |
| focus = core equations first | every section starts from the equation map; symbols table; worked numeric example; boxes secondary |
| focus = pipeline first | pipeline/architecture diagrams per section; function cards for code |
| maths = none | no formulas; plain-word mechanisms and tables |
| maths = full derivations | add derivation steps one line each, assumptions list |
| code = function-by-function | one card per function, call graph, data shapes |
| scope = chosen chapters | only those; index lists the rest as "not built" |
| delivery = local | `make_local.py`; ask engine default Ollama; offline |
| delivery = artifact | publish; ask engine Claude via `sample`; keep page under 16 MB |
| askstyle = very compact | RULES length "under 60 words"; `modelTier` quick |
| askstyle = explainer | RULES length 110 to 170 words; default tier; Go deeper on complex |
| videolinks = yes | search, verify (oembed: title + channel), add 'Video' links to dense sections only; say they are unwatched picks; skip topics with no good video |
| sourcelinks = pages of my copy | `add_refs.py`: map every section heading to PDF pages, chips for sub-topics, copy the PDF into the local app as textbook.pdf (served inline); needs a PDF with a text layer |
| completeness / 'nothing left' | coverage checklist closing every section (`check()`), definitions in tables, self-check per chapter |
| maths = none | relations stated as one-line word statements with small numbers, never formula notation; say so when a concept needs it |
| quizstyle = exam style / recall / true-false / mixed | `quiz()` per chapter in that style (references/quiz-styles.md); none = keep only the open self-check |
| features = all | `add_refs.py` (page-cited answers), `export_anki.py`, `make_mindmap.py`, `step=` on flow diagrams; ask-only = skip the rest |
| engine = none | omit shim/ask.js and the sample capability |
| language = Hindi glosses | add short glosses after key terms |

## requirements.json (frozen spec)
```json
{"source": "title", "reader": "who they are", "purpose": "...", "scope": "...", "focus": "...", "maths": "...", "code": "...",
 "visuals": "...", "examples": "...", "lenses": "Exam lens / Practitioner asks", "lens_a": "Exam lens", "lens_b": "Practitioner asks",
 "selfcheck": "...", "askbox": true, "askstyle": "...", "length": "usually 110 to 170 words", "mathnote": "...", "lensnote": "...",
 "delivery": "local|artifact|both", "engine": "ollama|claude|none", "look": "...", "language": "...",
 "unique": ["verbatim user requirements"], "comments_handled": [{"comment": "...", "handled": "..."}]}
```
`assemble.py` reads source/reader/mathnote/lensnote/length/lenses; set `atlas_kit.LENS_TITLES = (lens_a, lens_b)` in your chapter scripts.
