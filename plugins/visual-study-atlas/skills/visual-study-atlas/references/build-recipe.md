# Build recipe (page engineering)

## Pipeline
1. Extract text per chapter or unit (`extract_text.py`; for PDFs also split by the running chapter marker). Read it fully, in chunks.
2. Write claims first: one sentence per section, then pick the one picture that proves it. Figure types: pipeline with controls per phase, request path with trust boundary, layered stack, kill chain / lifecycle, cycle or feedback loop, 2x2 (`quad`), staircase, hub-and-spoke, timeline, bar chart from real numbers, comparison lanes, equation map, call graph.
3. Write `chN.py` (copy `templates/example_chapter.py`): `sec(id, 'SECTION n', title, claim, figure + tables/cards + lens(...))`, then a self-check section of `<details>` Q/A pairs, then `write(path, page(n, title, intro, sections, 'pages'))`.
4. Verify: parse every `<svg>` (xml.dom.minidom); serve the folder with `python3 -m http.server`; screenshot 3 or 4 figures per chapter in the browser pane; fix overlaps and clipped text before moving on.
5. Index: edit `templates/index_template.py`. Assemble: `scripts/assemble.py <folder> requirements.json`. Test locally with a mock `window.claude` for the ask box (click a diagram box, check the panel and the routing).
6. Deliver as frozen.

## Design rules
- Text in boxes 11px, about 6.3 px per character; keep lines at or below box width / 6.3 characters, 3 to 5 lines per box, 15px line height.
- Label arrows or say in the text what flows. One figure, one claim; caption states it.
- Colors only through CSS tokens (control teal, threat red, asset amber, flow blue); the page has light and dark.
- `S.text` unescapes then escapes HTML, so entities such as `&ldquo;` are safe in svg strings.
- Marker ids repeat across chapters; `assemble.py` prefixes them. Keep the `a/r/c/d + number` pattern.
- Number only real sequences (steps, phases).
- Typical overlaps: labels beside arrows, callout boxes on staircases, text past box edges. Check by screenshot.
- macOS `sed -i` needs `-i ''`; prefer small Python replacements.
- The main published page has no doctype/html/head/body (assemble.py produces that); extra files in an artifact would need their own.

## Honesty
Mark your own additions; flag garbled tables; attribute cases "as cited"; flag anything beyond the source "verify current guidance"; never invent numbers.

## Ask box
Hover outlines an askable unit (paragraph, list item, table cell, heading, svg box or label); click or selection opens a docked panel with chips and a text box. The tutor prompt comes from the frozen spec (`assemble.py` fills `__SOURCE__`, `__READER__`, `__MATHNOTE__`, `__LENSNOTE__`, `__LENGTH__`, `__LENSES__`). Local: `server.py` answers with retrieval over the source text via Ollama; set tiers in `config.json`. Artifact: Claude via the `sample` capability. Normal asks use the default tier; "Go deeper" uses the strongest; first-turn answers are cached for an hour.

## Local app
`make_local.py <atlas_folder> <out_folder> <text_dir>` copies atlas.html (with the shim), server.py, config.json, Atlas.command, README.md and the book text for retrieval. First run builds the embedding index (cached). Test `/health`, one `/ask` per tier, and report honestly: local models can invent examples.

## Dense, exam-style books: lessons from building a dense exam-style book (read before building)
- **Read the whole chapter text first, then write**: one `chN_part.py` per group of sections, each returning a list of `sec(...)`; a `chN.py` joins them and appends the self-check. Parse every svg after each part.
- **Per section**: claim, one diagram, tables holding every definition (`defs_table`), `check([...])` coverage checklist as the last item, `beyond(...)` for anything not in the source. Completeness = the checklist items match the source's bullets, lists and defined terms; no separate glossary needed.
- **Maths = none** still means keep the concept: state formulas as words ("single loss = asset value times exposure share") with the source's small examples.
- **Overflow check**: serve the folder, open each chapter at a 1100 px window, run `scripts/overflow_check.js` in `javascript_tool` (prints `clean` or the spilling labels). Then eyeball only the busiest figures. Normal screenshots at phone width hide the right part of wide svgs.
- **Static pages, no router, no online fonts**: `make_local.py` now calls `split_pages.py`, giving index.html + ch*.html. A single page with a hash router plus a render-blocking Google Fonts stylesheet can show a blank screen; static pages cannot.
- **Source links**: `add_refs.py <app> refs.json` after `make_local.py` (spec in the script docstring). Find headings with PyMuPDF exact-line matches, never case-insensitive search (it hits earlier mentions). Page numbers are PDF page numbers. The link opens `textbook.pdf#page=N` served by the local server with `Content-Disposition: inline`; `file://` links do not work from an http page. Some embedded browsers download PDFs instead of showing them; test in the user's real browser.
- **Videos**: use WebSearch with `allowed_domains: ["youtube.com"]`, then verify each ID with `https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=ID&format=json` (title + channel; 401/403 means embedding off, 404 gone). Prefer the source author's channel, the framework owner (NIST), or the method's inventor. Add only for dense topics; say the picks are unwatched; skip topics with no good result rather than guess.
- **Ports and launcher**: pick a port nobody uses (check `lsof -i :PORT`; the earlier atlas may hold 8765). `Atlas.command` clears a stale copy on that port. The page only loads while the launcher window is open.
- **Clean up**: delete the workbook, pilot folder and scratch copies when the user asks; keep only the app folder.
- **Never** move or delete the user's files other than ones you created; if the user relocates the app, work in the new location.
