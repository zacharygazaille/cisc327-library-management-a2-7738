import pytest
from datetime import datetime, timedelta
from library_service import (
    borrow_book_by_patron
)
from database import (
    insert_book,
    get_book_by_isbn
)

def test_borrow_book_valid_input():
    """Test borrowing a book with valid input."""
    insert_book("Test Book", "Test Author", "1234567890123", 5, 5)
    book = get_book_by_isbn("1234567890123")
    success, message = borrow_book_by_patron("123456", book['id'])

    assert success == True
    expected_due_date = (datetime.today() + timedelta(days=14)).strftime("%Y-%m-%d")
    assert f'Successfully borrowed' in message

def test_borrow_book_patron_id_too_short():
    """Test borrowing a book with a patron id that is too short."""
    insert_book("Test Book", "Test Author", "1234567890124", 5, 5)
    book = get_book_by_isbn("1234567890124")
    success, message = borrow_book_by_patron("12345", book['id'])
    
    assert success == False
    assert "Invalid patron ID. Must be exactly 6 digits." in message

def test_borrow_book_patron_id_too_long():
    """Test borrowing a book with a patron id that is too long."""
    insert_book("Test Book", "Test Author", "1234567890125", 5, 5)
    book = get_book_by_isbn("1234567890125")
    success, message = borrow_book_by_patron("1234567", book['id'])
    
    assert success == False
    assert "Invalid patron ID. Must be exactly 6 digits." in message

def test_borrow_book_book_not_found():
    """Test borrowing a book with a book that doesn't exist."""
    success, message = borrow_book_by_patron("123456", "123456789")
    
    assert success == False
    assert "Book not found." in message

def test_borrow_book_no_available_copies():
    """Test borrowing a book with no available copies"""
    insert_book("Test Book", "Test Author", "1234567890126", 1, 1)
    book = get_book_by_isbn("1234567890126")
    borrow_book_by_patron("123456", book['id'])
    success, message = borrow_book_by_patron("123457", book['id'])
    
    assert success == False
    assert "This book is currently not available." in message

def test_borrow_book_max_borrowed_box():
    """Test borrowing a book with a patron that has borrowed the max limit of books"""
    insert_book("Test Book", "Test Author", "1111111111111", 5, 5)
    book1 = get_book_by_isbn("1111111111111")
    insert_book("Test Book", "Test Author", "2222222222222", 5, 5)
    book2 = get_book_by_isbn("2222222222222")
    insert_book("Test Book", "Test Author", "3333333333333", 5, 5)
    book3 = get_book_by_isbn("3333333333333")
    insert_book("Test Book", "Test Author", "4444444444444", 5, 5)
    book4 = get_book_by_isbn("4444444444444")
    insert_book("Test Book", "Test Author", "5555555555555", 5, 5)
    book5 = get_book_by_isbn("5555555555555")
    insert_book("Test Book", "Test Author", "6666666666666", 5, 5)
    book6 = get_book_by_isbn("6666666666666")
    borrow_book_by_patron("123458", book1['id'])
    borrow_book_by_patron("123458", book2['id'])
    borrow_book_by_patron("123458", book3['id'])
    borrow_book_by_patron("123458", book4['id'])
    borrow_book_by_patron("123458", book5['id'])
    success, message = borrow_book_by_patron("123458", book6['id'])
    
    assert success == False
    assert "You have reached the maximum borrowing limit of 5 books." in message


def test_borrow_book_db_error(monkeypatch):
    """Test borrowing a book with a database error"""
    insert_book("Test Book", "Test Author", "1234567890997", 1, 1)
    book = get_book_by_isbn("1234567890997")
    monkeypatch.setattr("library_service.update_book_availability", lambda book_id, change: False)
    success, message = borrow_book_by_patron("123456", book['id'])
    assert success is False
    assert "Database error occurred while updating book availability." in message

def test_borrow_book_db_error_on_borrow_record(monkeypatch):
    """Test borrowing a book with another database error"""
    insert_book("Test Book", "Test Author", "1234567890996", 1, 1)
    book = get_book_by_isbn("1234567890996")
    monkeypatch.setattr("library_service.insert_borrow_record", lambda patron_id, book_id, borrow_date, due_date: False)
    success, message = borrow_book_by_patron("123456", book['id'])
    assert success is False
    assert "Database error occurred while creating borrow record." in message