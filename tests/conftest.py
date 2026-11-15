# tests/conftest.py
import os
import sys
import tempfile
import pytest

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

import database

@pytest.fixture(autouse=True)
def test_db():
    """
    Creates an isolated temporary SQLite database for each test run,
    ensuring tests never pollute production data.
    """
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".db")
    os.close(tmp_fd)

    orig_path = database.DB_PATH
    database.DB_PATH = tmp_path

    # Initialize schema in clean temporary database
    database.init_db()

    yield tmp_path

    # Teardown
    database.DB_PATH = orig_path
    if os.path.exists(tmp_path):
        try:
            os.remove(tmp_path)
        except OSError:
            pass
