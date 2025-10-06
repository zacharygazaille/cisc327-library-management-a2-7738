import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import clear_database

@pytest.fixture(autouse=True)
def run_before_each_test():
    clear_database() # Clears DB before running tests so that tests work without having to switch all the book IDs every time