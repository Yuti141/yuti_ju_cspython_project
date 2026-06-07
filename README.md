# TheoryLens

A study glossary for gender and media theory. Browse terms, track your learning progress, explore connections between concepts, and get reading recommendations from academic databases.

## Run locally

```bash
python web_app.py
```

Then open http://localhost:5000 in your browser.

## Run tests

Tests use an in-memory SQLite database and load the real `seed_data.json` so search and study-list behavior matches the live app.

```bash
python -m pytest
```

For verbose output:

```bash
python -m pytest -v
```

## Deploy

This app is configured for Render using `wsgi.py` and Gunicorn.
