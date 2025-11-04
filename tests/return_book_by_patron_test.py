import pytest
from datetime import datetime, timedelta
from services.library_service import (
    borrow_book_by_patron,
    return_book_by_patron
)
from database import (
    get_book_by_isbn,
    insert_book,
    insert_borrow_record
)

def test_return_book_valid():
    """Test returning a book that was borrowed."""
    insert_book("Test Book", "Test Author", "1234567890123", 5, 5)
    book = get_book_by_isbn("1234567890123")
    borrow_book_by_patron("123456", book['id'])
    success, message = return_book_by_patron("123456", book['id'])
    
    assert success == True
    assert "successfully returned" in message

def test_return_book_valid_with_late_fee():
    """Test returning a book that was borrowed and is overdue"""
    insert_book("Test Book", "Test Author", "1234567890124", 5, 5)
    book = get_book_by_isbn("1234567890124")
    due_date = datetime.today() - timedelta(days=5)
    borrow_date = due_date - timedelta(days=14)
    insert_borrow_record("123456", book['id'], borrow_date, due_date)
    success, message = return_book_by_patron("123456", book['id'])
    
    assert success == True
    assert "successfully returned" in message
    assert "late fee" in message

def test_return_book_not_borrowed():
    """Test returning a book that was not borrowed by the patron."""
    insert_book("Test Book", "Test Author", "1234567890125", 5, 5)
    book = get_book_by_isbn("1234567890125")
    success, message = return_book_by_patron("123457", book['id'])
    assert success is False
    assert "Not currently borrowed" in message

def test_return_book_invalid_book_id():
    """Test returning a book with an invalid book ID."""
    success, message = return_book_by_patron("123458", 99999)
    assert success is False
    assert "invalid book" in message

def test_return_book_patron_id_too_short():
    """Test returning a book with a patron ID that is too short."""
    insert_book("Test Book", "Test Author", "1234567890126", 5, 5)
    book = get_book_by_isbn("1234567890126")
    success, message = return_book_by_patron("12345", book['id'])
    assert success is False
    assert "invalid patron" in message

def test_return_book_patron_id_too_long():
    """Test returning a book with a patron ID that is too long."""
    insert_book("Test Book", "Test Author", "1234567890127", 5, 5)
    book = get_book_by_isbn("1234567890127")
    success, message = return_book_by_patron("1234567", book['id'])
    assert success is False
    assert "invalid patron" in message

def test_return_book_db_error(monkeypatch):
    """Test returning a book with a database error."""
    insert_book("Test Book", "Test Author", "1234567890999", 1, 1)
    book = get_book_by_isbn("1234567890999")
    borrow_book_by_patron("123456", book['id'])
    monkeypatch.setattr("services.library_service.update_book_availability", lambda book_id, change: False)
    success, message = return_book_by_patron("123456", book['id'])
    assert success is False
    assert "Database error occured" in message

def test_return_book_db_error_on_return_date(monkeypatch):
    """Test returning a book with another database error."""
    insert_book("Test Book", "Test Author", "1234567890998", 1, 1)
    book = get_book_by_isbn("1234567890998")
    borrow_book_by_patron("123456", book['id'])
    monkeypatch.setattr("services.library_service.update_borrow_record_return_date", lambda patron_id, book_id, return_date: False)
    success, message = return_book_by_patron("123456", book['id'])
    assert success is False
    assert "Database error occured while updating return date." in message