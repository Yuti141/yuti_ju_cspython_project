import sqlite3
import random
from datetime import datetime, timedelta
from db.core import get_connection


def get_term_of_day(force_new=False):
    conn = get_connection()
    cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")

    if not force_new:
        cursor.execute("SELECT term_id, picked_date FROM term_of_day_meta WHERE id = 1")
        row = cursor.fetchone()
        if row and row["picked_date"] == today:
            cursor.execute("SELECT id, name, definition FROM terms WHERE id = ?", (row["term_id"],))
            term = cursor.fetchone()
            if term:
                conn.close()
                return {"id": term["id"], "name": term["name"], "definition": term["definition"]}

    five_days_ago = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")
    cursor.execute("SELECT DISTINCT term_id FROM recently_shown WHERE shown_date >= ?", (five_days_ago,))
    recent_ids = [row["term_id"] for row in cursor.fetchall()]

    cursor.execute("SELECT term_id FROM study_list")
    study_ids = [row["term_id"] for row in cursor.fetchall()]

    cursor.execute("SELECT id, name, definition FROM terms")
    all_terms = cursor.fetchall()

    if not all_terms:
        conn.close()
        return None

    candidates = []
    fallback = []

    for term in all_terms:
        is_recent = term["id"] in recent_ids
        is_studied = term["id"] in study_ids

        if not is_studied and not is_recent:
            candidates.append(term)
        else:
            fallback.append(term)

    chosen = random.choice(candidates) if candidates else random.choice(fallback)

    cursor.execute("DELETE FROM term_of_day_meta WHERE id = 1")
    cursor.execute(
        "INSERT INTO term_of_day_meta (id, term_id, picked_date) VALUES (1, ?, ?)",
        (chosen["id"], today)
    )

    cursor.execute("INSERT INTO recently_shown (term_id, shown_date) VALUES (?, ?)", (chosen["id"], today))
    conn.commit()
    conn.close()

    return {
        "id": chosen["id"],
        "name": chosen["name"],
        "definition": chosen["definition"]
    }
