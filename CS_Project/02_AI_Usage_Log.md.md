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
