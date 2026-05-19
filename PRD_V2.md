# PRD v2 — TheoryLens

## Part 1: Project Identity

**Project name:** TheoryLens

**One-sentence pitch:** "TheoryLens is a CLI study glossary that helps students of gender and media theory to explore, connect, and deepen their understanding of critical theories by providing curated definitions, a visual concept map of term relationships, and reading recommendations fetched from academic databases."

**Target user:** Undergraduate students studying gender studies, media studies, cultural studies, or related humanities courses. They are familiar with academic terminology but struggle to see how theories connect to each other. They want a quick reference tool that goes beyond definitions — one that shows relationships and guides further reading.

**Why this project:** Gender and media theory is dense and interconnected. Traditional glossaries give definitions in isolation, but theories like "male gaze" don't exist in a vacuum — they connect to psychoanalysis, feminism, and film theory simultaneously. TheoryLens maps these connections and helps students build a mental web of concepts, not just memorize definitions.

---

## Part 2: Feature Scope — The "Must-Have" List

### Feature 1: Term Search (Fuzzy + Partial Match)
**What it does:** Lets the user search for any term by typing a full name, partial keyword, or even a typo. Returns matching terms with definition previews.
**Why it matters:** This is the primary way users interact with the app — fast lookup is essential for a study tool.
**User flow:**
  1. App shows search prompt on main screen
  2. User types: "gaze"
  3. App returns:
     ```
     Results for "gaze":
     1. Male Gaze — A concept from feminist film theory describing how visual media is structured for a masculine viewer...
     2. The Gaze — A psychoanalytic concept derived from Lacan's theory of the mirror stage...

     Pick a term (or 0 to go back): _
     ```
  4. User types "1"
  5. App shows full term entry (definition, tags, connections, readings, study status)
**Edge cases:**
  - User types a query with no matches → "No terms found for 'xyz'. Try a different search or browse by category."
  - User types an empty string → "Search cannot be empty. Please enter a term."
  - User types a number that's out of range → "Please enter a number between 0 and 2."

### Feature 2: Browse by Category
**What it does:** Lets the user explore all terms organized by tag (e.g., Feminism, Film Theory, Queer Theory, Psychoanalysis). Terms are listed alphabetically, and the user can filter by multiple tags.
**Why it matters:** Not everyone knows what to search for. Browsing lets users discover terms they didn't know existed.
**User flow:**
  1. User selects "Browse by category" from main menu
  2. App displays:
     ```
     Categories:
     1. Feminism (10 terms)
     2. Film/Media Theory (8 terms)
     3. Queer Theory (7 terms)
     4. Psychoanalysis (7 terms)
     5. Filter by multiple tags

     Pick a category (or 0 to go back): _
     ```
  3. User types "1"
  4. App shows all Feminism terms alphabetically:
     ```
     --- Feminism (10 terms) ---
     1. Beauvoir, Simone de — "One is not born, but rather becomes, a woman."
     2. Butler, Judith — Philosopher known for gender performativity...
     ...
     ```
  5. User picks a term to view full details
**Edge cases:**
  - Category has no terms → "No terms found in this category."
  - User picks "Filter by multiple tags" → App prompts for tag selections, shows intersection.

### Feature 3: Personal Study List with Learning Status
**What it does:** Lets users save terms to a personal study list and track their learning progress with three statuses: "Want to Learn", "In Progress", "Learned".
**Why it matters:** A glossary without personalization is just a reference book. The study list makes TheoryLens an active study tool.
**User flow:**
  1. User views a term (via search or browse)
  2. User selects "Add to study list" from the term view
  3. App prompts: "Set status: 1. Want to Learn  2. In Progress  3. Learned"
  4. User types "1"
  5. App confirms: "'Male Gaze' added to study list as 'Want to Learn'."
  6. From main menu, user selects "My study list"
  7. App displays:
     ```
     === My Study List ===

     Want to Learn (3 terms):
       - Male Gaze (Film/Media Theory, Feminism)
       - Heteronormativity (Queer Theory)
       - The Mirror Stage (Psychoanalysis)

     In Progress (1 term):
       - Performativity (Feminism, Queer Theory)

     Learned (0 terms):
       (none)
     ```
**Edge cases:**
  - Term already in study list → "'Male Gaze' is already in your study list. Update status? (y/n)"
  - Study list is empty → "Your study list is empty. Search for terms and add them to start studying!"

### Feature 4: Concept Map (Connection Viewer)
**What it does:** Displays the connections between terms as a text-based adjacency list. Each connection includes an explanation of how the terms relate.
**Why it matters:** Theories don't exist in isolation. Seeing that "male gaze" connects to "scopophilia" with the explanation "Both deal with the act of looking and visual pleasure" helps students understand the intellectual landscape.
**User flow:**
  1. User selects "Concept map" from main menu
  2. App shows a numbered list of all terms
  3. User picks "Male Gaze"
  4. App displays:
     ```
     Male Gaze
     ├── Scopophilia — "Both deal with visual pleasure and the act of looking"
     ├── Laura Mulvey — "Mulvey coined the term in her 1975 essay"
     └── Feminist Film Theory — "Male gaze is a core concept in feminist film criticism"

     Pick another term to explore (or 0 to go back): _
     ```
  5. User can pick another term to explore its connections
**Edge cases:**
  - Term has no connections → "'Male Gaze' has no connections yet. Go to Manage Connections to link it to other terms."
  - Only user-added connections exist → Show those. Tag-based connections are generated automatically.

### Feature 5: Reading Recommendations (Crossref API)
**What it does:** When viewing a term, fetches related academic papers and readings from the Crossref API.
**Why it matters:** Definitions are starting points. Reading recommendations guide students to primary sources and deeper study.
**User flow:**
  1. User views a term (e.g., "Male Gaze")
  2. Term entry includes a "Reading Recommendations" section
  3. App fetches from Crossref API and displays:
     ```
     Reading Recommendations:
     1. "Visual Pleasure and Narrative Cinema" — Laura Mulvey (1975)
        DOI: 10.1097/00006842-197510000-00014
     2. "The Male Gaze in Contemporary Hollywood" — Sarah Projansky (2014)
        DOI: 10.1080/xxxxxxx
     ```
**Edge cases:**
  - API is down or unreachable → "Could not fetch reading recommendations. Try again later."
  - No results found → "No reading recommendations found for this term."
  - Network timeout → "Request timed out. Check your internet connection."

---

## Part 3: Data Architecture

### 3a: Data Structure (SQLite Tables)

**Table: terms**
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PRIMARY KEY | Auto-incrementing ID |
| name | TEXT NOT NULL | Term name (e.g., "Male Gaze") |
| definition | TEXT NOT NULL | Short definition |
| tags | TEXT | Comma-separated tags (e.g., "Feminism,Film/Media Theory") |
| is_user_added | INTEGER DEFAULT 0 | 1 if user-created, 0 if seed data |

**Table: connections**
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PRIMARY KEY | Auto-incrementing ID |
| term_a_id | INTEGER NOT NULL | FK to terms.id |
| term_b_id | INTEGER NOT NULL | FK to terms.id |
| explanation | TEXT NOT NULL | Brief explanation of the connection |
| is_user_added | INTEGER DEFAULT 0 | 1 if user-created |

**Table: study_list**
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PRIMARY KEY | Auto-incrementing ID |
| term_id | INTEGER NOT NULL | FK to terms.id |
| status | TEXT NOT NULL | "want_to_learn", "in_progress", or "learned" |
| date_added | TEXT | Date added (YYYY-MM-DD) |

**Table: recently_shown**
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PRIMARY KEY | Auto-incrementing ID |
| term_id | INTEGER NOT NULL | FK to terms.id |
| shown_date | TEXT | Date shown (YYYY-MM-DD) |

**Example data:**
```sql
INSERT INTO terms (name, definition, tags, is_user_added) VALUES
('Male Gaze', 'A concept from feminist film theory, coined by Laura Mulvey in 1975, describing how visual media is often structured from a masculine, heterosexual perspective, positioning the viewer as male and women as objects of visual pleasure.', 'Feminism,Film/Media Theory', 0);

INSERT INTO connections (term_a_id, term_b_id, explanation, is_user_added) VALUES
(1, 5, 'Both deal with visual pleasure and the act of looking as a source of power', 0);
```

### 3b: Data Flow

- **Data comes FROM:** Pre-loaded seed file (JSON) on first launch, user input for new terms/connections, Crossref API for readings.
- **Data gets STORED:** SQLite database file (`theorylens.db`).
- **Data gets READ:** On every search, browse, view, study list display, and concept map query.
- **Data gets WRITTEN:** After every user action that modifies data (add term, add to study list, add connection, update status). Immediate write — no in-memory buffer.

---

## Part 4: Function Specifications

### database.py

```python
def init_database() -> None:
    """
    Creates the SQLite database and tables if they don't exist.
    Loads seed data on first run.

    Returns:
        None

    Edge cases handled:
        - Database file already exists → skips creation, tables preserved
        - Seed data already loaded → checks if terms table is empty before inserting
    """
```

```python
def search_terms(query: str) -> list[dict]:
    """
    Searches terms by name and definition using fuzzy and partial matching.

    Args:
        query: Search string (e.g., "gaze", "male gze", "film")

    Returns:
        List of matching term dicts sorted by relevance.

    Example:
        >>> search_terms("gaze")
        [{"id": 1, "name": "Male Gaze", "definition": "A concept from...", "tags": "Feminism,Film/Media Theory"}, ...]

    Edge cases handled:
        - Empty query → raises ValueError: "Search cannot be empty"
        - No matches → returns empty list
    """
```

```python
def view_term(term_id: int) -> dict:
    """
    Retrieves full details for a single term including tags, connections, and study status.

    Args:
        term_id: The term's database ID.

    Returns:
        Dict with term details, list of connections, and study list status (if any).

    Edge cases handled:
        - Invalid term_id → raises ValueError: "Term not found"
    """
```

```python
def add_term(name: str, definition: str, tags: list[str]) -> int:
    """
    Adds a new user-created term to the database.

    Args:
        name: Term name (e.g., "Heteronormativity"). Must be non-empty.
        definition: Short definition. Must be non-empty.
        tags: List of tag strings (e.g., ["Queer Theory", "Feminism"]).

    Returns:
        The new term's database ID.

    Example:
        >>> add_term("Heteronormativity", "The assumption that heterosexuality is the default...", ["Queer Theory"])
        33

    Edge cases handled:
        - Empty name → raises ValueError: "Term name cannot be empty"
        - Empty definition → raises ValueError: "Definition cannot be empty"
        - Duplicate name → raises ValueError: "Term 'Male Gaze' already exists"
    """
```

```python
def edit_term(term_id: int, name: str = None, definition: str = None, tags: list[str] = None) -> bool:
    """
    Edits a user-added term. Seed terms cannot be edited.

    Args:
        term_id: The term's database ID.
        name: New name (optional).
        definition: New definition (optional).
        tags: New tags list (optional).

    Returns:
        True if successful.

    Edge cases handled:
        - Term is seed data → raises ValueError: "Cannot edit pre-loaded terms"
        - Term not found → raises ValueError: "Term not found"
        - Duplicate name → raises ValueError: "Term 'X' already exists"
    """
```

```python
def delete_term(term_id: int) -> bool:
    """
    Deletes a user-added term and its connections. Seed terms cannot be deleted.

    Args:
        term_id: The term's database ID.

    Returns:
        True if successful.

    Edge cases handled:
        - Term is seed data → raises ValueError: "Cannot delete pre-loaded terms"
        - Term not found → raises ValueError: "Term not found"
        - Term is in study list → also removes from study list
    """
```

```python
def add_to_study_list(term_id: int, status: str) -> bool:
    """
    Adds a term to the user's study list with a learning status.

    Args:
        term_id: The term's database ID.
        status: One of "want_to_learn", "in_progress", "learned".

    Returns:
        True if successful.

    Edge cases handled:
        - Term already in study list → raises ValueError: "Term already in study list. Update status instead?"
        - Invalid status → raises ValueError: "Status must be 'want_to_learn', 'in_progress', or 'learned'"
    """
```

```python
def update_study_status(term_id: int, new_status: str) -> bool:
    """
    Updates the learning status of a term in the study list.

    Args:
        term_id: The term's database ID.
        new_status: One of "want_to_learn", "in_progress", "learned".

    Returns:
        True if successful.

    Edge cases handled:
        - Term not in study list → raises ValueError: "Term not in study list"
    """
```

```python
def add_connection(term_a_id: int, term_b_id: int, explanation: str) -> bool:
    """
    Creates a manual connection between two terms with an explanation.

    Args:
        term_a_id: First term's database ID.
        term_b_id: Second term's database ID.
        explanation: Brief explanation of the connection.

    Returns:
        True if successful.

    Edge cases handled:
        - Same term → raises ValueError: "Cannot connect a term to itself"
        - Connection already exists → raises ValueError: "Connection already exists. Edit explanation instead?"
        - Either term not found → raises ValueError: "Term not found"
    """
```

```python
def get_connections(term_id: int) -> list[dict]:
    """
    Retrieves all connections for a given term (both directions).

    Args:
        term_id: The term's database ID.

    Returns:
        List of dicts with connected term name and explanation.

    Example:
        >>> get_connections(1)
        [{"term": "Scopophilia", "explanation": "Both deal with visual pleasure..."}, ...]

    Edge cases handled:
        - Term has no connections → returns empty list
    """
```

```python
def get_term_of_day() -> dict:
    """
    Selects a random term for "Term of the Day", excluding recently shown terms
    and prioritizing terms not in the user's study list.

    Returns:
        Term dict with name and definition.

    Edge cases handled:
        - All terms recently shown → resets recently shown list, picks randomly
        - No terms in database → returns None
    """
```

### app.py

```python
def fetch_readings(term_name: str) -> list[dict]:
    """
    Fetches reading recommendations from the Crossref API for a given term.

    Args:
        term_name: The term to search for (e.g., "Male Gaze").

    Returns:
        List of dicts with title, authors, year, and DOI.

    Example:
        >>> fetch_readings("Male Gaze")
        [{"title": "Visual Pleasure and Narrative Cinema", "authors": "Laura Mulvey", "year": "1975", "doi": "10.xxx"}, ...]

    Edge cases handled:
        - API unreachable → returns empty list with message "Could not fetch readings"
        - No results → returns empty list with message "No readings found"
        - Timeout → returns empty list with message "Request timed out"
    """
```

```python
def display_main_menu(term_of_day: dict) -> None:
    """
    Renders the main screen with search prompt, term of the day, and menu options.

    Args:
        term_of_day: The term dict to display as "Term of the Day".

    Returns:
        None (prints to terminal).
    """
```

```python
def run() -> None:
    """
    Main application loop. Handles menu navigation, user input, and screen transitions.

    Returns:
        None

    Edge cases handled:
        - Invalid menu input → "Please enter a valid option."
        - KeyboardInterrupt (Ctrl+C) → Graceful exit: "Goodbye!"
    """
```

---

## Part 5: User Interface & Interaction Design

### 5a: Main Menu

```
====================================
           THEORYLENS
    Your Gender & Media Theory Guide
====================================

Term of the Day:
  Performativity — The idea that gender is not an identity but a
  repeated performance, as theorized by Judith Butler.

Search for a term: _

── or choose an option ──
1. Browse by category
2. My study list
3. Concept map
4. Manage connections
5. Add a new term
6. Exit

What would you like to do? (1-6):
```

### 5b: Screen-by-Screen Flow

**Search Results:**
```
Results for "gaze":
1. Male Gaze — A concept from feminist film theory describing how visual media
   is structured for a masculine viewer, positioning women as objects of visual
   pleasure.
   Tags: Feminism, Film/Media Theory

2. The Gaze — A psychoanalytic concept from Lacan describing the awareness of
   being looked at, which shapes subjectivity.
   Tags: Psychoanalysis

Pick a term (or 0 to go back):
```

**Term View:**
```
====================================
         MALE GAZE
====================================
Tags: Feminism, Film/Media Theory

Definition:
A concept from feminist film theory, coined by Laura Mulvey in 1975,
describing how visual media is often structured from a masculine,
heterosexual perspective, positioning the viewer as male and women
as objects of visual pleasure.

Connections:
├── Scopophilia — "Both deal with visual pleasure and the act of looking"
├── Laura Mulvey — "Mulvey coined the term in her 1975 essay"
└── Feminist Film Theory — "Male gaze is a core concept in feminist film criticism"

Reading Recommendations:
1. "Visual Pleasure and Narrative Cinema" — Laura Mulvey (1975)
   DOI: 10.1097/00006842-197510000-00014
2. "The Male Gaze in Contemporary Cinema" — Various (2019)
   DOI: 10.1080/xxxxxxx

Study Status: Want to Learn

Options:
1. Add to study list
2. Update study status
3. Back to search
```

**Browse by Category:**
```
Categories:
1. Feminism (10 terms)
2. Film/Media Theory (8 terms)
3. Queer Theory (7 terms)
4. Psychoanalysis (7 terms)
5. Filter by multiple tags

Pick a category (or 0 to go back): 1

--- Feminism (10 terms) ---
 1. Beauvoir, Simone de — "One is not born, but rather becomes, a woman."
 2. Butler, Judith — Philosopher known for gender performativity theory.
 3. Crenshaw, Kimberle — Coined the term "intersectionality."
 4. Feminist Film Theory — A framework analyzing gender representation in cinema.
 5. hooks, bell — Cultural critic and feminist scholar.
 6. Intersectionality — The interconnected nature of social categorizations.
 7. Male Gaze — A concept describing how visual media is structured for masculine viewers.
 8. Patriarchy — A social system where men hold primary power.
 9. Performativity — The idea that gender is a repeated performance, not an identity.
10. Standpoint Theory — Knowledge is situated within social position.

Pick a term (or 0 to go back):
```

**Study List:**
```
=== My Study List ===

Want to Learn (3 terms):
  - Heteronormativity (Queer Theory)
  - The Mirror Stage (Psychoanalysis)
  - Male Gaze (Feminism, Film/Media Theory)

In Progress (1 term):
  - Performativity (Feminism, Queer Theory)

Learned (0 terms):
  (none)

Options:
1. View a term
2. Update status
3. Back to menu
```

**Concept Map:**
```
All terms:
 1. Abjection
 2. Beauvoir, Simone de
 3. Butler, Judith
 ...
32. The Male Gaze

Pick a term to view connections (or 0 to go back): 32

Male Gaze
├── Scopophilia — "Both deal with visual pleasure and the act of looking"
├── Laura Mulvey — "Mulvey coined the term in her 1975 essay"
└── Feminist Film Theory — "Male gaze is a core concept in feminist film criticism"

Pick another term (or 0 to go back):
```

**Manage Connections:**
```
--- Manage Connections ---

Select first term:
 1. Abjection
 2. Beauvoir, Simone de
 ...
32. The Male Gaze

Pick term A (or 0 to go back): 1

Select second term:
 1. Beauvoir, Simone de
 2. Butler, Judith
 ...
31. The Gaze

Pick term B: 31

Explain the connection: Both deal with the subject's relationship to being observed and the resulting psychological effects.

Connect "Abjection" to "The Gaze"? (y/n): y

Connection created!
```

**Add New Term:**
```
--- Add a New Term ---

Term name: Queer Temporality
Definition: The concept that queer experiences disrupt linear notions of time,
challenging the idea of chronological progression tied to reproduction and
heteronormative life stages.
Tags (comma-separated): Queer Theory, Postmodernism

Summary:
  Name: Queer Temporality
  Definition: The concept that queer experiences disrupt linear notions of time...
  Tags: Queer Theory, Postmodernism

Save this term? (y/n): y

Term "Queer Temporality" added successfully!
```

---

## Part 6: Error Handling & Edge Cases

| # | Error Scenario | App Response |
|---|---------------|-------------|
| 1 | User types a letter when a number is expected | "Please enter a valid number." |
| 2 | User searches with empty input | "Search cannot be empty. Please enter a term." |
| 3 | Database file is corrupted or missing on startup | "Database not found. Creating fresh database..." and rebuild from seed data |
| 4 | Crossref API is down or unreachable | "Could not fetch reading recommendations. Try again later." |
| 5 | User tries to add a duplicate term | "Term 'Male Gaze' already exists. Edit it instead? (y/n)" |
| 6 | User tries to create a duplicate connection | "'Male Gaze' is already connected to 'Scopophilia'. Edit the explanation instead? (y/n)" |
| 7 | User tries to edit/delete a seed term | "Cannot modify pre-loaded terms. You can only edit terms you added." |
| 8 | Term has no connections in concept map | "'Male Gaze' has no connections yet. Go to Manage Connections to add one." |
| 9 | User enters invalid study status | "Status must be 'want_to_learn', 'in_progress', or 'learned'." |
| 10 | API request times out | "Request timed out. Check your internet connection." |

---

## Part 7: Testing Plan

```
Test 1: Search for a term by partial name
  - Input: search "gaze"
  - Expected: Returns "Male Gaze" and "The Gaze" with preview snippets

Test 2: Search for a term with a typo
  - Input: search "performatvity" (typo)
  - Expected: Returns "Performativity" via fuzzy match

Test 3: Add term to study list, then view study list
  - Input: view "Male Gaze" → add to study list → status "Want to Learn"
  - Expected: "Male Gaze" appears under "Want to Learn" in study list

Test 4: Add a new user term, then search for it
  - Input: add term "Queer Temporality" with definition and tags
  - Expected: Searching "temporality" returns the new term

Test 5: Add a connection between two terms, then view concept map
  - Input: connect "Male Gaze" to "Scopophilia" with explanation
  - Expected: Concept map for "Male Gaze" shows "Scopophilia" with explanation

Test 6: API failure graceful handling
  - Input: disconnect internet, view a term
  - Expected: Term shows definition and connections, reading section says "Could not fetch readings"

Test 7: Try to edit a seed term
  - Input: attempt to edit "Male Gaze" (seed term)
  - Expected: Error message "Cannot modify pre-loaded terms"

Test 8: Term of the day excludes recently shown
  - Input: launch app multiple times
  - Expected: Different term shown each time, no repeats within 5 launches
```

---

## Part 8: Stretch Goals

- [ ] Data visualization with matplotlib: bar chart of terms per category, pie chart of study status distribution
- [ ] Export study list to CSV
- [ ] Rich terminal formatting (colors, tables) — requires `rich` library approval
- [ ] Weekly study summary: "You learned 3 new terms this week"
- [ ] Edit connection explanations
- [ ] Search within definitions (not just term names)
- [ ] Import/export full database as JSON for sharing

---

## Project Constraints Compliance

| Constraint | Status |
|-----------|--------|
| Python Only | Standard library only: `sqlite3`, `difflib`, `urllib.request`, `json`, `random`, `datetime` |
| Clear User/Purpose | Study tool for gender/media theory students |
| MVP | Glossary + search + study list + connections + Crossref readings |
| 4+ Python Skills | Functions, dictionaries, file I/O, API use, error handling, loops, conditionals, user I/O |
| 4+ Custom Functions | 14 functions defined |
| Real Data Structure | SQLite database with 4 tables |
| Save/Load/Fetch/Generate | SQLite save/load + Crossref API fetch |
| Handle User Mistakes | 10 error scenarios documented |
| Difficulty Feature | File Storage (SQLite) + API Connection (Crossref) |

---

## File Structure

```
theorylens/
├── app.py          # Main application: UI, menu, search, Crossref API
├── database.py     # Database: init, CRUD operations, seed data
├── seed_data.json  # Pre-loaded terms and connections
└── theorylens.db   # SQLite database (created on first run)
```

## Dependencies

None. All modules from Python standard library:
- `sqlite3` — Database
- `difflib` — Fuzzy string matching
- `urllib.request` — HTTP requests for Crossref API
- `json` — Parse API responses and seed data
- `random` — Term of the day selection
- `datetime` — Date tracking for study list and recently shown terms
