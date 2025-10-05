import pytest
from datetime import datetime, timedelta
from library_service import (
    get_patron_status_report,
    borrow_book_by_patron,
    insert_borrow_record
)
from database import (
    insert_book, get_book_by_isbn,
    update_borrow_record_return_date
)

def test_patron_status_no_borrowed_book():
    """Test retrieving patron status with no borrowed books"""
    result = get_patron_status_report("123456")
    
    assert result['currently_borrowed'] == 0
    assert result['total_late_fees'] == 0.0
    assert result['num_currently_borrowed'] == 0
    assert result['history'] == []

def test_patron_status_currently_borrowed_not_overdue():
    """Test retrieving patron status with borrowed books that aren't overdue"""
    insert_book("Test Book", "Test Author", "1234567890123", 1, 1)
    book = get_book_by_isbn("1234567890123")
    borrow_book_by_patron("123456", book['id'])
    result = get_patron_status_report("123456")
    
    assert result['currently_borrowed'][0]['title'] == "Test Book"
    assert result['total_late_fees'] == 0.0
    assert result['num_currently_borrowed'] == 1
    assert len(result['history']) == 1

def test_patron_status_overdue_book():
    """Test retrieving patron status with borrowed books that are overdue"""
    insert_book("Test Book", "Test Author", "1234567890124", 1, 1)
    book = get_book_by_isbn("1234567890124")
    due_date = datetime.today() - timedelta(days=5)
    borrow_date = due_date - timedelta(days=14)
    insert_borrow_record("123457", book['id'], borrow_date, due_date)
    result = get_patron_status_report("123457")
    
    assert result['currently_borrowed'][0]['title'] == "Test Book"
    assert result['currently_borrowed'][0]['is_overdue'] == True
    assert result['total_late_fees'] > 0.0
    assert result['num_currently_borrowed'] == 1
    assert len(result['history']) == 1

def test_patron_status_with_returned_books():
    """Test patron status with returned books in history."""
    insert_book("Test Book", "Test Author", "1234567890125", 1, 1)
    book = get_book_by_isbn("1234567890125")
    borrow_book_by_patron("123458", book['id'])
    update_borrow_record_return_date("123458", book['id'], datetime.today())
    result = get_patron_status_report("123458")
    assert result['num_currently_borrowed'] == 0
    assert result['currently_borrowed'] == []
    assert len(result['history']) == 1
    assert result['history'][0]['title'] == "Test Book"

def test_patron_status_max_borrowed_books():
    """Test patron status with 5 currently borrowed books."""
    insert_book("Test Book", "Test Author", "1234567890126", 1, 1)
    book1 = get_book_by_isbn("1234567890126")
    insert_book("Test Book", "Test Author", "1234567890127", 1, 1)
    book2 = get_book_by_isbn("1234567890127")
    insert_book("Test Book", "Test Author", "1234567890128", 1, 1)
    book3 = get_book_by_isbn("1234567890128")
    insert_book("Test Book", "Test Author", "1234567890129", 1, 1)
    book4 = get_book_by_isbn("1234567890129")
    insert_book("Test Book", "Test Author", "1234567890130", 1, 1)
    book5 = get_book_by_isbn("1234567890130")
    borrow_book_by_patron("123459", book1['id'])
    borrow_book_by_patron("123459", book2['id'])
    borrow_book_by_patron("123459", book3['id'])
    borrow_book_by_patron("123459", book4['id'])
    borrow_book_by_patron("123459", book5['id'])

    result = get_patron_status_report("123459")
    assert result['num_currently_borrowed'] == 5
    assert len(result['currently_borrowed']) == 5
    assert len(result['history']) == 5

def test_patron_status_patron_too_short():
    """Test patron status report for a patron ID that is too short."""
    result = get_patron_status_report("12345")
    assert result['currently_borrowed'] == []
    assert result['total_late_fees'] == 0.0
    assert result['num_currently_borrowed'] == 0
    assert result['history'] == []

def test_patron_status_patron_too_long():
    """Test patron status report for a patron ID that is too long."""
    result = get_patron_status_report("1234567")
    assert result['currently_borrowed'] == []
    assert result['total_late_fees'] == 0.0
    assert result['num_currently_borrowed'] == 0
    assert result['history'] == []