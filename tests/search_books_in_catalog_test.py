import pytest
from services.library_service import (
    search_books_in_catalog
)
from database import (
    insert_book
)

def test_search_books_by_title():
    """Test searching for a book by title."""
    insert_book("Test Book", "Test Author", "1234567890123", 5, 5)
    results = search_books_in_catalog("Test Book", "title")
    assert len(results) > 0

def test_search_books_by_partial_title():
    """Test searching for a book by a partial title."""
    insert_book("Test Book", "Test Author", "1234567890124", 5, 5)
    results = search_books_in_catalog("Test Bo", "title")
    assert len(results) > 0

def test_search_books_by_title_not_found():
    """Test searching for a book by title that doesn't exist."""
    insert_book("Test Book", "Test Author", "1234567890125", 5, 5)
    results = search_books_in_catalog("Not Real Book", "title")
    assert len(results) == 0

def test_search_books_by_author():
    """Test searching for a book by author."""
    insert_book("Another Book", "Unique Author", "1234567890126", 5, 5)
    results = search_books_in_catalog("Unique Author", "author")
    assert len(results) > 0

def test_search_books_by_partial_author():
    """Test searching for a book by a partial author."""
    insert_book("Another Book", "Unique Author", "1234567890127", 5, 5)
    results = search_books_in_catalog("Uniq", "author")
    assert len(results) > 0

def test_search_books_by_author_not_found():
    """Test searching for a book by author that doesn't exist."""
    insert_book("Another Book", "Unique Author", "1234567890128", 5, 5)
    results = search_books_in_catalog("Not Real Author", "author")
    assert len(results) == 0

def test_search_books_by_isbn():
    """Test searching for a book by ISBN."""
    insert_book("ISBN Book", "ISBN Author", "1234567890129", 5, 5)
    results = search_books_in_catalog("1234567890129", "isbn")
    assert len(results) == 1

def test_search_books_by_partial_isbn():
    """Test searching for a book by a partial ISBN. Should not work."""
    insert_book("ISBN Book", "ISBN Author", "1234567890130", 5, 5)
    results = search_books_in_catalog("123456789013", "isbn")
    assert len(results) == 0

def test_search_books_by_isbn_not_found():
    """Test searching for a book by ISBN that doesn't exist."""
    insert_book("ISBN Book", "ISBN Author", "1234567890131", 5, 5)
    results = search_books_in_catalog("9999999999999", "isbn")
    assert len(results) == 0