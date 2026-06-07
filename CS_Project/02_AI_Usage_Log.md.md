# AI Usage Log

## Entry 1

### Date
2026-05-19

### AI Tool Used
Claude Code (Claude Sonnet)

### What I Asked AI
I used the /grill-me skill to stress-test and refine my PRD (Product Requirements Document) for a Python CLI study tool called TheoryLens. I asked AI to interview me with multiple-choice options for every major design decision, and then draft the full PRD v2 based on our decisions.

### Why I Asked
I had a rough project idea — a glossary/dictionary for gender and media theories — but needed to nail down the specifics: what features to include, how to store data, how the UI works, which APIs to use, and how to keep it achievable as a Python-only MVP. The PRD template requires detailed specs for every feature, function, data structure, and error case. I needed help turning my vague idea into a concrete, buildable blueprint.

### What AI Gave Me
AI guided me through ~28 design questions, each with 4-5 options and a recommendation. We decided on:
- **Project type:** CLI glossary (not web app)
- **Storage:** SQLite (not JSON or in-memory)
- **Search:** Fuzzy + partial matching using `difflib`
- **Connections:** Tag-based automatic + user-managed with explanations
- **Study list:** Grouped by learning status (want to learn / in progress / learned)
- **API:** Crossref for reading recommendations (standard library `urllib.request`)
- **Dependencies:** Zero external — standard library only
- **File structure:** `app.py` + `database.py` + `seed_data.json`
- **Seed data:** ~32 terms across Feminist Theory, Film/Media Theory, Queer Theory, Psychoanalysis

AI then drafted the complete PRD v2 with all 8 required sections: project identity, feature scope (5 features with full user flows and edge cases), data architecture (SQLite schema with 4 tables), function specifications (14 functions with docstrings), UI mockups for every screen, error handling (10 scenarios), testing plan (8 test cases), and stretch goals. AI also verified the project meets all 12 class constraints.

### What I Used
- The recommended options for most decisions (CLI terminal-only, SQLite, pre-loaded seed data, standard library only)
- Some non-recommended choices: fuzzy+partial search (not just exact), 4 theory areas (not 3), connections with explanations (not bare links)
- The full PRD draft as written — I accepted it without major changes

### What I Changed or Rejected
- I rejected the initial recommendation of 3 areas with ~10 terms each. I wanted 4 areas (Feminist, Film/Media, Queer, Psychoanalytic) with ~8 terms each for broader coverage.
- I rejected the recommendation of just tag-based automatic connections. I insisted on a dedicated "Manage connections" screen where users manually link terms with written explanations of how they relate.
- I added "Term of the Day" to the main screen (not in the original options) — a random term that excludes recently shown ones and prioritizes unstudied terms.
- I changed the browse feature to include both alphabetical ordering AND tag filtering (combining two separate options).

### What I Still Do Not Fully Understand
- How `difflib.SequenceMatcher` actually calculates fuzzy match scores — I know it works but don't fully understand the algorithm.
- How to structure the SQLite queries for getting connections "both directions" (term A→B and B→A) efficiently.
- How the Crossref API response is structured — I'll need to look at actual responses to parse them correctly.
- How to implement the "prioritize unstudied terms" logic for Term of the Day without it being too complex.

### My Next Step
Start building the project. Begin with `database.py` — set up the SQLite schema, write the seed data JSON file, and implement the CRUD functions. Then move to `app.py` for the UI and search logic.

---

## Entry 2

### Date
2026-05-26

### AI Tool Used
Claude Code (Claude Sonnet)

### What I Asked AI
I asked AI to help me run the TheoryLens project as a localhost web app and fix several issues with the website: (1) the reading recommendations were showing "Unknown" for authors, (2) the "Term of the Day" was changing every time I refreshed the home page instead of staying consistent per day, (3) the search button wasn't visually aligned with the search bar, (4) the browse page for tags containing slashes (like "Film/Media Theory") was returning a 404 error, and (5) the "why read" explanations for reading recommendations were too generic — every article about the same term got the same one-word label.

### Why I Asked
The Flask web app was already built but had usability bugs. The author parsing issue made reading recommendations less useful. The term of the day refreshing on every visit defeated its purpose — it should feel like a daily feature, not random. The search bar misalignment was a visual polish issue. The slash-in-tag URL was a routing bug. And the one-word "why read" labels (like just "Context") weren't helpful — I wanted explanations that reflected each individual article's specific angle, not just the general topic.

### What AI Gave Me
AI made changes across four files:

**`app.py` — Reading recommendations overhaul:**
- Fixed author parsing from the Crossref API by filtering out entries without a `family` name field, so authors display properly instead of "Unknown"
- Built a `_TITLE_ANGLES` dictionary (~100 angle keywords mapped to explanation templates) that analyzes article titles to generate specific "why read" explanations
- The matching logic strips the term's own words from the title first, then matches against angle keywords like "contesting", "merchant", "state", "slippages", etc., so each article gets a unique explanation based on its actual content (e.g., "Thinking with Patriarchy" → "Read to explore how to apply patriarchy as a thinking tool", while "Merchant Patriarchy and the State" → "Read to explore how patriarchy intersects with state power and governance")

**`database.py` — Term of the Day persistence:**
- Changed `get_term_of_day()` to use a `term_of_day_meta` SQLite table that stores the picked term ID and the date it was selected
- On each call, it checks if today's date matches the stored date — if so, returns the same term; if not, picks a new one
- Added a `force_new` parameter for manual refresh via the "New Term" button

**`web_app.py` — New route and browse fix:**
- Added `/new-term-of-day` POST route to handle the manual refresh button
- Changed `/browse/<tag>` to `/browse/<path:tag>` so tags with slashes (like "Film/Media Theory") work correctly

**`templates/home.html` — UI updates:**
- Added a "New Term" button under the term of the day card
- Changed the search form to use a CSS class (`search-form`) instead of inline styles

**`templates/term.html` — Reading display:**
- Added a `reading-relevance` div under each reading that shows the article-specific "why read" explanation

**`static/style.css` — Styling fixes:**
- Fixed search bar alignment by using flexbox on the form with `align-items: stretch` and `flex: 1` on the input
- Added `.reading-relevance` style for the new explanation text
- Added `.btn.small` style for the "New Term" button

### What I Used
- All of the author parsing fix — the `if a.get("family")` filter solved the "Unknown" author problem
- The full `_TITLE_ANGLES` dictionary approach for generating article-specific explanations
- The date-based term of the day logic with the `term_of_day_meta` table
- The `<path:tag>` Flask route converter for slash-containing tags
- The flexbox-based search bar alignment fix

### What I Changed or Rejected
- I initially had one-word relevance labels (like "Context", "Power", "Media") — I asked AI to change these to full sentences starting with "Read to..." so they're actually understandable to users
- The first version of the relevance system matched keywords against the full title, which gave the same explanation for every article about the same term. I asked AI to strip the term's own words from the title first, so the matching focuses on what makes each article different
- I didn't reject any of the technical approaches — the title-angle keyword matching, date-based persistence, and path converter were all the right solutions

### What I Still Do Not Fully Understand
- How Flask's `<path:tag>` converter differs from the default `<tag>` converter internally — I know it allows slashes but don't understand the routing mechanism
- How the `_TITLE_ANGLES` keyword matching priority works when multiple angles could match (it sorts by length, so longer/more specific keywords match first)
- How the `term_of_day_meta` table interacts with the existing `recently_shown` table — both track what was shown, but for different purposes

### My Next Step
Continue improving the web app. Potential next features: better search results display, user authentication, or improving the concept map visualization.

---

## Entry 3

### Date
2026-06-07

### AI Tool Used
Claude Code (Claude Sonnet)

### What I Asked AI
I asked AI to help me implement the full V2 plan based on my teacher's feedback. The feedback was: make web_app.py the clear entry point, split the large app and database files into smaller modules, add automated tests for search and study list behavior, and deploy the Flask app. We used the /grill-me skill again to pressure-test the plan, then AI built everything.

### Why I Asked
My teacher reviewed the project and said the codebase was too monolithic — `database.py` was ~694 lines and `app.py` had both CLI and web logic mixed together. He wanted a clear web entry point, modular code, tests that prove search and study list work correctly, and a live deployed URL. I needed help restructuring the entire project without breaking existing functionality.

### What AI Gave Me

**Planning phase (grill-me skill):**
- AI interviewed me through ~8 design decisions: kill the CLI entirely (option 1), extract readings into `services/readings.py` (dedicated module), split database.py into a `db/` package by entity (core, terms, study_list, connections, tags, term_of_day), use in-memory SQLite with real seed data for tests, deploy to Render, and use `wsgi.py` as the production entry point.

**Implementation phase:**

- **`services/readings.py`** — Extracted `fetch_readings()`, `_TITLE_ANGLES` dictionary, and `_get_relevance_keyword()` from the old `app.py`
- **`db/core.py`** — `get_connection()` (now accepts optional db path for tests), `init_database()`, `_load_seed_data()`
- **`db/terms.py`** — `search_terms`, `view_term`, `add_term`, `edit_term`, `delete_term`
- **`db/study_list.py`** — `add_to_study_list`, `update_study_status`, `get_study_list`
- **`db/connections.py`** — `add_connection`, `get_connections`
- **`db/tags.py`** — `get_all_terms`, `get_terms_by_tag`, `get_all_tags`
- **`db/term_of_day.py`** — `get_term_of_day`
- **`wsgi.py`** — Production entry point for Render (imports app, calls `init_database()`, exposes `app_flask` for gunicorn)
- **`requirements.txt`** — Flask, gunicorn, pytest
- **`tests/test_search.py`** — 9 tests: exact match, partial match, fuzzy match, definition search, missing term returns empty, empty query raises error, case insensitivity, single-term DB edge case, no-match edge case
- **`tests/test_study_list.py`** — 10 tests: add saves correctly, multiple statuses, duplicate raises error, invalid status raises error, nonexistent term raises error, update status works, update nonexistent raises error, update invalid status raises error, empty by default, add-then-update workflow
- **`web_app.py`** — Refactored imports to use `db/` submodules directly; added explicit `endpoint=` parameters on renamed route functions so templates' `url_for()` calls still work
- **`render.yaml`** — Render deployment config with gunicorn bind to `$PORT`
- **`README.md`** — Added run, test, and deploy instructions plus the live demo link
- **Deleted** `app.py` and `database.py`

**Deployment fixes:**
- First deploy failed because gunicorn wasn't binding to Render's `PORT` env var — fixed with `--bind 0.0.0.0:$PORT`
- Second deploy showed "Internal Server Error" because templates called `url_for('add_term')` but the route function was renamed to `add_term_route` — fixed by adding explicit `endpoint="add_term"` (and same for edit, delete, add_to_study_list, update_study_status)

### What I Used
- All decisions from the grill-me session: kill CLI, db/ package, services/ module, in-memory tests with real seed data, Render deployment
- The full test suite as written — 19 tests covering all the behaviors my teacher asked for
- The `endpoint=` fix for template compatibility
- The `--bind 0.0.0.0:$PORT` gunicorn fix for Render

### What I Changed or Rejected
- I kept the Flask web UI as the sole interface (no CLI preservation) — this was the recommended option and matched teacher feedback
- I chose the `db/` package split by entity rather than by operation type or minimal split — this made the code organization clearest
- I chose hybrid test data strategy: load real `seed_data.json` for integration tests, use minimal fake data for edge-case tests
- I didn't add a `.gitignore` for `__pycache__/` or `.db` files — should probably do that later

### What I Still Do Not Fully Understand
- How `file::memory:?cache=shared` works in SQLite — why it creates disk files sometimes but is still "in-memory"
- How gunicorn's worker model works — if multiple workers each call `init_database()`, do they conflict?
- How Render's ephemeral filesystem affects SQLite in the long run — the DB resets on every deploy, which is fine for a demo but not production
- How Flask's `endpoint=` parameter interacts with the auto-generated endpoint names — I know it overrides them but don't understand the routing table internals

### My Next Step
Submit the project. Everything is built, tested, deployed, and documented.
