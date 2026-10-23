# Content recipes by material type

Suggestive, not rigid; choose what makes the idea click.

## Maths and statistics (Bayesian, probability, optimisation, ML theory)
Per section: (1) the core equation in a large equation card, symbols table (symbol, meaning, units/range), (2) what each term does in words, (3) a derivation ladder only if asked, (4) a small worked numeric example with the arithmetic shown, (5) an intuition picture (areas, curves, update arrows, before/after distributions), (6) assumptions and when it breaks, (7) "where it is used". Use SVG for plots drawn from real computed values (compute in Python, draw to scale), never decorative curves. Write equations as clear text or inline HTML (`<sub>`, `<sup>`), or load KaTeX from cdnjs when many formulas (pin an exact version). Diagram ideas: equation map (terms as boxes with arrows to meaning), update loop (prior -> likelihood -> posterior), shape comparison charts.

## Code, repos, notebooks
Run `scripts/code_pipeline.py` for the function inventory. Page contents: overview pipeline (input -> stages -> output) with the file and function behind each stage; a **function card** per important function (signature, inputs, what it does in one sentence, outputs, calls, called by); a call graph; data shapes at each hop (small example values); one traced run if safe (own code only; outside code read-only, reconstruct the mechanism in code you write and vouch for). Show only the lines that matter, with a moving highlight idea (numbered lines).

## Conceptual and professional fields (cybersecurity, finance practice, management, law)
Architecture and flow diagrams, decision flows, comparison tables, case timelines, 2x2 matrices, lens panels (exam / practitioner), self-checks with scenario questions. Attribute cases to the source; mark hypothetical ones.

## Research papers
Problem and gap; key idea in one picture; method pipeline; the core equation or loss with symbol table; experiment setup and results (real numbers as bar charts); limits and assumptions; related work map (only what the paper states).

## Articles and blog posts
Argument map (claim, evidence, counterpoint); key terms; timeline if historical; "what to remember" list.

## Video and lecture transcripts
Timeline with chapter markers from the transcript; concept graph; each key claim with the nearby quote paraphrased; worked examples recreated; glossary. Do not invent content that the speaker did not say.

## Courses (many modules)
One page per module; index with prerequisites map and a progress-style checklist; consistent figure style across modules; local delivery usually best. Keep module pages short enough to read in one sitting.

## Mixed or messy notes
Cluster by topic first, show the structure (map), then fill pages. Say what was inferred.
