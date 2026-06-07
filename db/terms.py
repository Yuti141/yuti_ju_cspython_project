import sqlite3
from difflib import SequenceMatcher
from db.core import get_connection
from db.connections import get_connections


def search_terms(query):
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

        if name_lower == query:
            score = 1.0
        elif name_lower.startswith(query):
            score = 0.9
        elif query in name_lower:
            score = 0.8
        elif query in def_lower:
            score = 0.5
        else:
            name_ratio = SequenceMatcher(None, query, name_lower).ratio()
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
