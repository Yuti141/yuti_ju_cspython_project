import sqlite3
import json
import os
from difflib import SequenceMatcher
from datetime import datetime, timedelta

DB_PATH = "theorylens.db"
SEED_PATH = "seed_data.json"


def get_connection():
    """Returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_database():
    """
    Creates the SQLite database and tables if they don't exist.
    Loads seed data on first run.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS terms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            definition TEXT NOT NULL,
            tags TEXT,
            is_user_added INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS connections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            term_a_id INTEGER NOT NULL,
            term_b_id INTEGER NOT NULL,
            explanation TEXT NOT NULL,
            is_user_added INTEGER DEFAULT 0,
            FOREIGN KEY (term_a_id) REFERENCES terms(id),
            FOREIGN KEY (term_b_id) REFERENCES terms(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS study_list (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            term_id INTEGER NOT NULL UNIQUE,
            status TEXT NOT NULL,
            date_added TEXT,
            FOREIGN KEY (term_id) REFERENCES terms(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recently_shown (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            term_id INTEGER NOT NULL,
            shown_date TEXT,
            FOREIGN KEY (term_id) REFERENCES terms(id)
        )
    """)

    conn.commit()

    # Load seed data if terms table is empty
    cursor.execute("SELECT COUNT(*) FROM terms")
    count = cursor.fetchone()[0]
    if count == 0:
        _load_seed_data(conn)

    conn.close()


def _load_seed_data(conn):
    """Loads terms and connections from seed_data.json."""
    if not os.path.exists(SEED_PATH):
        return

    with open(SEED_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    cursor = conn.cursor()

    for term in data["terms"]:
        cursor.execute(
            "INSERT INTO terms (name, definition, tags, is_user_added) VALUES (?, ?, ?, 0)",
            (term["name"], term["definition"], term["tags"])
        )

    for conn_entry in data["connections"]:
        # Look up term IDs by name
        cursor.execute("SELECT id FROM terms WHERE name = ?", (conn_entry["term_a"],))
        row_a = cursor.fetchone()
        cursor.execute("SELECT id FROM terms WHERE name = ?", (conn_entry["term_b"],))
        row_b = cursor.fetchone()

        if row_a and row_b:
            cursor.execute(
                "INSERT INTO connections (term_a_id, term_b_id, explanation, is_user_added) VALUES (?, ?, ?, 0)",
                (row_a[0], row_b[0], conn_entry["explanation"])
            )

    conn.commit()


def search_terms(query):
    """
    Searches terms by name and definition using fuzzy and partial matching.

    Args:
        query: Search string (e.g., "gaze", "male gze", "film")

    Returns:
        List of matching term dicts sorted by relevance.

    Raises:
        ValueError: If query is empty.
    """
    if not query or not query.strip():
        raise ValueError("Search cannot be empty")

    query = query.strip().lower()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, definition, tags FROM terms")
    all_terms = cursor.fetchall()
    conn.close()

    results = []
    for term in all_terms:
        name_lower = term["name"].lower()
        def_lower = term["definition"].lower()

        # Exact name match = highest score
        if name_lower == query:
            score = 1.0
        # Name starts with query
        elif name_lower.startswith(query):
            score = 0.9
        # Query is substring of name
        elif query in name_lower:
            score = 0.8
        # Query is substring of definition
        elif query in def_lower:
            score = 0.5
        else:
            # Fuzzy match on name
            name_ratio = SequenceMatcher(None, query, name_lower).ratio()
            # Fuzzy match on definition (first 100 chars for performance)
            def_ratio = SequenceMatcher(None, query, def_lower[:100]).ratio()
            score = max(name_ratio, def_ratio)
            if score < 0.4:
                continue

        results.append({
            "id": term["id"],
            "name": term["name"],
            "definition": term["definition"],
            "tags": term["tags"],
            "score": score
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def view_term(term_id):
    """
    Retrieves full details for a single term including connections and study status.

    Args:
        term_id: The term's database ID.

    Returns:
        Dict with term details, connections, and study list status.

    Raises:
        ValueError: If term_id is invalid.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, definition, tags, is_user_added FROM terms WHERE id = ?", (term_id,))
    term = cursor.fetchone()
    if not term:
        conn.close()
        raise ValueError("Term not found")

    connections = get_connections(term_id)

    cursor.execute("SELECT status FROM study_list WHERE term_id = ?", (term_id,))
    study_row = cursor.fetchone()
    study_status = study_row["status"] if study_row else None

    conn.close()

    return {
        "id": term["id"],
        "name": term["name"],
        "definition": term["definition"],
        "tags": term["tags"],
        "is_user_added": term["is_user_added"],
        "connections": connections,
        "study_status": study_status
    }


def add_term(name, definition, tags):
    """
    Adds a new user-created term to the database.

    Args:
        name: Term name. Must be non-empty.
        definition: Short definition. Must be non-empty.
        tags: List of tag strings (e.g., ["Queer Theory", "Feminism"]).

    Returns:
        The new term's database ID.

    Raises:
        ValueError: If name or definition is empty, or term already exists.
    """
    if not name or not name.strip():
        raise ValueError("Term name cannot be empty")
    if not definition or not definition.strip():
        raise ValueError("Definition cannot be empty")

    name = name.strip()
    definition = definition.strip()
    tags_str = ",".join(t.strip() for t in tags if t.strip())

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM terms WHERE name = ?", (name,))
    if cursor.fetchone():
        conn.close()
        raise ValueError(f"Term '{name}' already exists")

    cursor.execute(
        "INSERT INTO terms (name, definition, tags, is_user_added) VALUES (?, ?, ?, 1)",
        (name, definition, tags_str)
    )
    term_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return term_id


def edit_term(term_id, name=None, definition=None, tags=None):
    """
    Edits a user-added term. Seed terms cannot be edited.

    Args:
        term_id: The term's database ID.
        name: New name (optional).
        definition: New definition (optional).
        tags: New tags list (optional).

    Returns:
        True if successful.

    Raises:
        ValueError: If term is seed data, not found, or duplicate name.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, is_user_added FROM terms WHERE id = ?", (term_id,))
    term = cursor.fetchone()
    if not term:
        conn.close()
        raise ValueError("Term not found")
    if not term["is_user_added"]:
        conn.close()
        raise ValueError("Cannot edit pre-loaded terms")

    if name and name.strip():
        name = name.strip()
        cursor.execute("SELECT id FROM terms WHERE name = ? AND id != ?", (name, term_id))
        if cursor.fetchone():
            conn.close()
            raise ValueError(f"Term '{name}' already exists")

    updates = []
    params = []
    if name and name.strip():
        updates.append("name = ?")
        params.append(name.strip())
    if definition and definition.strip():
        updates.append("definition = ?")
        params.append(definition.strip())
    if tags is not None:
        tags_str = ",".join(t.strip() for t in tags if t.strip())
        updates.append("tags = ?")
        params.append(tags_str)

    if updates:
        params.append(term_id)
        cursor.execute(f"UPDATE terms SET {', '.join(updates)} WHERE id = ?", params)
        conn.commit()

    conn.close()
    return True


def delete_term(term_id):
    """
    Deletes a user-added term and its connections. Seed terms cannot be deleted.

    Args:
        term_id: The term's database ID.

    Returns:
        True if successful.

    Raises:
        ValueError: If term is seed data or not found.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, is_user_added FROM terms WHERE id = ?", (term_id,))
    term = cursor.fetchone()
    if not term:
        conn.close()
        raise ValueError("Term not found")
    if not term["is_user_added"]:
        conn.close()
        raise ValueError("Cannot delete pre-loaded terms")

    cursor.execute("DELETE FROM connections WHERE term_a_id = ? OR term_b_id = ?", (term_id, term_id))
    cursor.execute("DELETE FROM study_list WHERE term_id = ?", (term_id,))
    cursor.execute("DELETE FROM recently_shown WHERE term_id = ?", (term_id,))
    cursor.execute("DELETE FROM terms WHERE id = ?", (term_id,))
    conn.commit()
    conn.close()
    return True


def add_to_study_list(term_id, status):
    """
    Adds a term to the user's study list with a learning status.

    Args:
        term_id: The term's database ID.
        status: One of "want_to_learn", "in_progress", "learned".

    Returns:
        True if successful.

    Raises:
        ValueError: If term already in study list or invalid status.
    """
    valid_statuses = ("want_to_learn", "in_progress", "learned")
    if status not in valid_statuses:
        raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM terms WHERE id = ?", (term_id,))
    if not cursor.fetchone():
        conn.close()
        raise ValueError("Term not found")

    cursor.execute("SELECT id FROM study_list WHERE term_id = ?", (term_id,))
    if cursor.fetchone():
        conn.close()
        raise ValueError("Term already in study list. Update status instead?")

    date_added = datetime.now().strftime("%Y-%m-%d")
    cursor.execute(
        "INSERT INTO study_list (term_id, status, date_added) VALUES (?, ?, ?)",
        (term_id, status, date_added)
    )
    conn.commit()
    conn.close()
    return True


def update_study_status(term_id, new_status):
    """
    Updates the learning status of a term in the study list.

    Args:
        term_id: The term's database ID.
        new_status: One of "want_to_learn", "in_progress", "learned".

    Returns:
        True if successful.

    Raises:
        ValueError: If term not in study list or invalid status.
    """
    valid_statuses = ("want_to_learn", "in_progress", "learned")
    if new_status not in valid_statuses:
        raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM study_list WHERE term_id = ?", (term_id,))
    if not cursor.fetchone():
        conn.close()
        raise ValueError("Term not in study list")

    cursor.execute("UPDATE study_list SET status = ? WHERE term_id = ?", (new_status, term_id))
    conn.commit()
    conn.close()
    return True


def get_study_list():
    """
    Returns the full study list grouped by status.

    Returns:
        Dict with keys "want_to_learn", "in_progress", "learned", each a list of term dicts.
    """
    conn = get_connection()
    cursor = conn.cursor()

    result = {"want_to_learn": [], "in_progress": [], "learned": []}

    cursor.execute("""
        SELECT sl.term_id, sl.status, sl.date_added, t.name, t.tags
        FROM study_list sl
        JOIN terms t ON sl.term_id = t.id
        ORDER BY sl.date_added DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        entry = {
            "term_id": row["term_id"],
            "name": row["name"],
            "tags": row["tags"],
            "date_added": row["date_added"]
        }
        result[row["status"]].append(entry)

    return result


def add_connection(term_a_id, term_b_id, explanation):
    """
    Creates a manual connection between two terms with an explanation.

    Args:
        term_a_id: First term's database ID.
        term_b_id: Second term's database ID.
        explanation: Brief explanation of the connection.

    Returns:
        True if successful.

    Raises:
        ValueError: If same term, connection exists, or term not found.
    """
    if term_a_id == term_b_id:
        raise ValueError("Cannot connect a term to itself")

    if not explanation or not explanation.strip():
        raise ValueError("Explanation cannot be empty")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM terms WHERE id = ?", (term_a_id,))
    if not cursor.fetchone():
        conn.close()
        raise ValueError("Term not found")
    cursor.execute("SELECT id FROM terms WHERE id = ?", (term_b_id,))
    if not cursor.fetchone():
        conn.close()
        raise ValueError("Term not found")

    # Check for existing connection in either direction
    cursor.execute("""
        SELECT id FROM connections
        WHERE (term_a_id = ? AND term_b_id = ?) OR (term_a_id = ? AND term_b_id = ?)
    """, (term_a_id, term_b_id, term_b_id, term_a_id))
    if cursor.fetchone():
        conn.close()
        raise ValueError("Connection already exists. Edit explanation instead?")

    cursor.execute(
        "INSERT INTO connections (term_a_id, term_b_id, explanation, is_user_added) VALUES (?, ?, ?, 1)",
        (term_a_id, term_b_id, explanation.strip())
    )
    conn.commit()
    conn.close()
    return True


def get_connections(term_id):
    """
    Retrieves all connections for a given term (both directions).

    Args:
        term_id: The term's database ID.

    Returns:
        List of dicts with connected term id, name, and explanation.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT t.id, t.name, c.explanation, c.is_user_added
        FROM connections c
        JOIN terms t ON (t.id = CASE WHEN c.term_a_id = ? THEN c.term_b_id ELSE c.term_a_id END)
        WHERE c.term_a_id = ? OR c.term_b_id = ?
    """, (term_id, term_id, term_id))

    results = []
    for row in cursor.fetchall():
        results.append({
            "term_id": row["id"],
            "term_name": row["name"],
            "explanation": row["explanation"],
            "is_user_added": row["is_user_added"]
        })

    conn.close()
    return results


def get_all_terms():
    """
    Returns all terms in the database, ordered alphabetically.

    Returns:
        List of term dicts with id, name, and tags.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, tags FROM terms ORDER BY name ASC")
    results = [{"id": row["id"], "name": row["name"], "tags": row["tags"]} for row in cursor.fetchall()]
    conn.close()
    return results


def get_terms_by_tag(tag):
    """
    Returns all terms that have the given tag, ordered alphabetically.

    Args:
        tag: The tag to filter by (e.g., "Feminism").

    Returns:
        List of term dicts.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, definition, tags FROM terms ORDER BY name ASC")
    all_terms = cursor.fetchall()
    conn.close()

    results = []
    for term in all_terms:
        term_tags = [t.strip() for t in (term["tags"] or "").split(",")]
        if tag in term_tags:
            results.append({
                "id": term["id"],
                "name": term["name"],
                "definition": term["definition"],
                "tags": term["tags"]
            })
    return results


def get_all_tags():
    """
    Returns all unique tags with term counts.

    Returns:
        List of dicts with tag name and count, sorted by count descending.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT tags FROM terms WHERE tags IS NOT NULL AND tags != ''")
    rows = cursor.fetchall()
    conn.close()

    tag_counts = {}
    for row in rows:
        for tag in row["tags"].split(","):
            tag = tag.strip()
            if tag:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

    result = [{"tag": tag, "count": count} for tag, count in tag_counts.items()]
    result.sort(key=lambda x: (-x["count"], x["tag"]))
    return result


def get_term_of_day():
    """
    Selects a random term for "Term of the Day", excluding recently shown terms
    and prioritizing terms not in the user's study list.

    Returns:
        Term dict with name and definition, or None if no terms exist.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Get recently shown term IDs (last 5)
    five_days_ago = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")
    cursor.execute("SELECT DISTINCT term_id FROM recently_shown WHERE shown_date >= ?", (five_days_ago,))
    recent_ids = [row["term_id"] for row in cursor.fetchall()]

    # Get terms in study list
    cursor.execute("SELECT term_id FROM study_list")
    study_ids = [row["term_id"] for row in cursor.fetchall()]

    # Get all terms
    cursor.execute("SELECT id, name, definition FROM terms")
    all_terms = cursor.fetchall()

    if not all_terms:
        conn.close()
        return None

    # Prioritize: unstudied + not recently shown > unstudied + recently shown > studied + not recently shown > rest
    import random
    candidates = []
    fallback = []

    for term in all_terms:
        is_recent = term["id"] in recent_ids
        is_studied = term["id"] in study_ids

        if not is_studied and not is_recent:
            candidates.append(term)
        elif not is_recent:
            fallback.append(term)
        else:
            fallback.append(term)

    chosen = random.choice(candidates) if candidates else random.choice(fallback)

    # Record that this term was shown today
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("INSERT INTO recently_shown (term_id, shown_date) VALUES (?, ?)", (chosen["id"], today))
    conn.commit()
    conn.close()

    return {
        "id": chosen["id"],
        "name": chosen["name"],
        "definition": chosen["definition"]
    }
