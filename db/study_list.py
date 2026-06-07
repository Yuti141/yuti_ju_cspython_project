import sqlite3
from datetime import datetime
from db.core import get_connection


def add_to_study_list(term_id, status):
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
