import sqlite3
import json
import os

DB_PATH = "theorylens.db"
SEED_PATH = "seed_data.json"


def get_connection(db_path=None):
    """Returns a connection to the SQLite database."""
    conn = sqlite3.connect(db_path or DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_database(db_path=None):
    """Creates the SQLite database and tables if they don't exist. Loads seed data on first run."""
    conn = get_connection(db_path)
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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS term_of_day_meta (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            term_id INTEGER NOT NULL,
            picked_date TEXT NOT NULL
        )
    """)

    conn.commit()

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

    for term in data.get("terms", []):
        cursor.execute(
            "INSERT INTO terms (name, definition, tags, is_user_added) VALUES (?, ?, ?, 0)",
            (term["name"], term["definition"], term.get("tags", ""))
        )

    for conn_entry in data.get("connections", []):
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
