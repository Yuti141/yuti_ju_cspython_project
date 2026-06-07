import pytest
import json
import os
import uuid
import db.core
from db.core import get_connection, init_database
from db.study_list import add_to_study_list, update_study_status, get_study_list


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


class TestStudyListAdd:
    def test_add_to_study_list_saves_correctly(self, db_conn):
        add_to_study_list(1, "want_to_learn")
        sl = get_study_list()
        assert any(t["term_id"] == 1 for t in sl["want_to_learn"])

    def test_add_multiple_statuses(self, db_conn):
        add_to_study_list(1, "want_to_learn")
        add_to_study_list(2, "in_progress")
        add_to_study_list(3, "learned")

        sl = get_study_list()
        assert any(t["term_id"] == 1 for t in sl["want_to_learn"])
        assert any(t["term_id"] == 2 for t in sl["in_progress"])
        assert any(t["term_id"] == 3 for t in sl["learned"])

    def test_duplicate_add_raises_error(self, db_conn):
        add_to_study_list(1, "want_to_learn")
        with pytest.raises(ValueError, match="already in study list"):
            add_to_study_list(1, "in_progress")

    def test_invalid_status_raises_error(self, db_conn):
        with pytest.raises(ValueError, match="Status must be one of"):
            add_to_study_list(1, "invalid_status")

    def test_add_nonexistent_term_raises_error(self, db_conn):
        with pytest.raises(ValueError, match="Term not found"):
            add_to_study_list(9999, "want_to_learn")


class TestStudyListUpdate:
    def test_update_status_works(self, db_conn):
        add_to_study_list(1, "want_to_learn")
        update_study_status(1, "learned")

        sl = get_study_list()
        assert not any(t["term_id"] == 1 for t in sl["want_to_learn"])
        assert any(t["term_id"] == 1 for t in sl["learned"])

    def test_update_nonexistent_term_raises_error(self, db_conn):
        with pytest.raises(ValueError, match="Term not in study list"):
            update_study_status(9999, "learned")

    def test_update_to_invalid_status_raises_error(self, db_conn):
        add_to_study_list(1, "want_to_learn")
        with pytest.raises(ValueError, match="Status must be one of"):
            update_study_status(1, "bad_status")


class TestStudyListRemove:
    def test_study_list_empty_by_default(self, db_conn):
        sl = get_study_list()
        assert sl["want_to_learn"] == []
        assert sl["in_progress"] == []
        assert sl["learned"] == []

    def test_add_then_remove_by_update(self, db_conn):
        add_to_study_list(1, "want_to_learn")
        update_study_status(1, "learned")
        sl = get_study_list()
        assert any(t["term_id"] == 1 for t in sl["learned"])
