import sqlite3
from db.core import get_connection


def add_connection(term_a_id, term_b_id, explanation):
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
