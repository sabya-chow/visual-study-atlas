# Study atlas (local)

Everything runs on this Mac. No account, no internet needed (fonts fall back to system fonts).

## Start
Double-click `Atlas.command` (or run `./Atlas.command` in Terminal). It starts Ollama if needed, starts the local server and opens http://127.0.0.1:8765.
First run builds a search index over the atlas and the book text (about 5 minutes, saved in `index_cache.json`). Questions work while it builds, but are better grounded once `http://127.0.0.1:8765/health` shows `ready`.

## Use
Click any sentence, table cell or diagram box (or select words) and ask. The pill at the bottom left toggles click-to-ask.

## Files
- `index.html`, `ch1.html`, ... static pages (no JavaScript routing, no online fonts).
- `textbook.pdf` (optional) local copy of the source, opened by the "Textbook" links at the right page.
- `server.py` serves the page and `/ask`; retrieval + streaming from Ollama (standard library only).
- `config.json` models per tier, port, retrieval settings.
- `book/` text of the book used for grounding answers (local copy only).
- `Atlas.command` launcher. Drag it to the Dock or to Applications for one-click use.

## Change models
Edit `config.json`: `quick` (fast chips), `default` (normal asks), `complex` (Go deeper). Names must match `ollama list`. `think` is `false`, `"low"`, `"high"` or removed if a model does not support it.
Re-index after changing the embedding model: `python3 server.py --reindex`.

## Honest limits
Local 9B to 20B models explain well when the passages are retrieved, but can still invent details in examples. Treat examples as illustrations and check facts against the chapter page.

The page only loads while `Atlas.command` is running; if the browser shows nothing, start it again.
