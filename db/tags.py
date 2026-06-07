import sqlite3
from db.core import get_connection


def get_all_terms():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, tags FROM terms ORDER BY name ASC")
    results = [{"id": row["id"], "name": row["name"], "tags": row["tags"]} for row in cursor.fetchall()]
    conn.close()
    return results


def get_terms_by_tag(tag):
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
