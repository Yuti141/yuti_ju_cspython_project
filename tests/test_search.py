import pytest
import json
import os
import uuid
import db.core
from db.core import get_connection, init_database
from db.terms import search_terms


SEED_PATH = "seed_data.json"
ORIGINAL_DB_PATH = db.core.DB_PATH


@pytest.fixture
def db_conn():
    test_db = f"file:memdb_{uuid.uuid4().hex}?mode=memory&cache=shared"
    db.core.DB_PATH = test_db
    init_database(test_db)

    conn = get_connection(test_db)
    yield conn
    conn.close()
    db.core.DB_PATH = ORIGINAL_DB_PATH


class TestSearchWithSeedData:
    def test_search_returns_expected_concepts(self, db_conn):
        results = search_terms("Male Gaze")
        assert len(results) >= 1
        assert any(r["name"] == "Male Gaze" for r in results)

    def test_partial_search_works(self, db_conn):
        results = search_terms("gaze")
        names = [r["name"] for r in results]
        assert "Male Gaze" in names

    def test_fuzzy_search_works(self, db_conn):
        results = search_terms("performatvity")
        names = [r["name"] for r in results]
        assert "Performativity" in names

    def test_search_in_definition(self, db_conn):
        results = search_terms("feminist film theory")
        assert len(results) > 0

    def test_search_missing_term_returns_empty(self, db_conn):
        results = search_terms("xyznonexistent")
        assert results == []

    def test_empty_search_raises_error(self, db_conn):
        with pytest.raises(ValueError, match="Search cannot be empty"):
            search_terms("")

    def test_search_case_insensitive(self, db_conn):
        results_lower = search_terms("male gaze")
        results_upper = search_terms("MALE GAZE")
        assert [r["name"] for r in results_lower] == [r["name"] for r in results_upper]


class TestSearchEdgeCases:
    def test_single_term_database(self, db_conn):
        cursor = db_conn.cursor()
        cursor.execute("PRAGMA foreign_keys = OFF")
        cursor.execute("DELETE FROM terms")
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.execute(
            "INSERT INTO terms (name, definition, tags) VALUES (?, ?, ?)",
            ("Test Term", "A test definition.", "Test")
        )
        db_conn.commit()

        results = search_terms("Test")
        assert len(results) == 1
        assert results[0]["name"] == "Test Term"

    def test_no_match_in_sparse_database(self, db_conn):
        cursor = db_conn.cursor()
        cursor.execute("PRAGMA foreign_keys = OFF")
        cursor.execute("DELETE FROM terms")
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.execute(
            "INSERT INTO terms (name, definition, tags) VALUES (?, ?, ?)",
            ("Only Term", "Only definition.", "Tag")
        )
        db_conn.commit()

        results = search_terms("zzzzzzzzzzzzzzz")
        assert results == []
