from datetime import datetime, timedelta
from library_service import (
    borrow_book_by_patron,
    calculate_late_fee_for_book,
)
from database import (
    insert_book,
    get_book_by_isbn,
    insert_borrow_record
)

def test_calculate_fee_no_overdue():
    """Test calculating fees for a book that is not overdue."""
    insert_book("Test Book", "Test Author", "1234567890123", 5, 5)
    book = get_book_by_isbn("1234567890123")
    borrow_book_by_patron("123456", book['id'])
    result = calculate_late_fee_for_book("123456", book['id'])
    
    assert result['fee_amount'] == 0.00
    assert result['days_overdue'] == 0

def test_calculate_5_days_overdue():
    """Test calculating fees for a book that is 5 days overdue."""
    insert_book("Test Book", "Test Author", "1234567890124", 5, 5)
    book = get_book_by_isbn("1234567890124")
    due_date = datetime.today() - timedelta(days=5)
    borrow_date = due_date - timedelta(days=14)
    insert_borrow_record("123456", book['id'], borrow_date, due_date)
    result = calculate_late_fee_for_book("123456", book['id'])
    
    assert result['fee_amount'] == 2.5
    assert result['days_overdue'] == 5

def test_calculate_10_days_overdue():
    """Test calculating fees for a book that is 10 days overdue."""
    insert_book("Test Book", "Test Author", "1234567890125", 5, 5)
    book = get_book_by_isbn("1234567890125")
    due_date = datetime.today() - timedelta(days=10)
    borrow_date = due_date - timedelta(days=14)
    insert_borrow_record("123456", book['id'], borrow_date, due_date)
    result = calculate_late_fee_for_book("123456", book['id'])
    
    assert result['fee_amount'] == 6.5
    assert result['days_overdue'] == 10

def test_calculate_30_days_overdue():
    """Test calculating fees for a book that is 30 days overdue."""
    insert_book("Test Book", "Test Author", "1234567890126", 5, 5)
    book = get_book_by_isbn("1234567890126")
    due_date = datetime.today() - timedelta(days=30)
    borrow_date = due_date - timedelta(days=14)
    insert_borrow_record("123456", book['id'], borrow_date, due_date)
    result = calculate_late_fee_for_book("123456", book['id'])
    
    assert result['fee_amount'] == 15.0
    assert result['days_overdue'] == 30

def test_calculate_patron_too_short():
    """Test calculating fees for a book with a patron id that is too short"""
    insert_book("Test Book", "Test Author", "1234567890127", 5, 5)
    book = get_book_by_isbn("1234567890127")
    result = calculate_late_fee_for_book("12345", book["id"])

    assert result['fee_amount'] == 0.0
    assert result['days_overdue'] == 0

def test_calculate_patron_too_long():
    """Test calculating fees for a book with a patron id that is too long"""
    insert_book("Test Book", "Test Author", "1234567890128", 5, 5)
    book = get_book_by_isbn("1234567890128")
    result = calculate_late_fee_for_book("1234567", book["id"])

    assert result['fee_amount'] == 0.0
    assert result['days_overdue'] == 0

def test_calculate_patron_invalid_book():
    """Test calculating fees for a book with an invalid book ID"""
    result = calculate_late_fee_for_book("123456", "1234567890129")

    assert result['fee_amount'] == 0.0
    assert result['days_overdue'] == 0

def test_calculate_late_fee_no_borrow_record():
    """Test calculating fees for a book that hasn't been borrowed"""
    insert_book("Test Book", "Test Author", "1234567890999", 1, 1)
    book = get_book_by_isbn("1234567890999")
    result = calculate_late_fee_for_book("123456", book['id'])
    assert result['fee_amount'] == 0.0
    assert result['days_overdue'] == 0