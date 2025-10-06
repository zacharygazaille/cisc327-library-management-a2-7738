import pytest
from datetime import datetime, timedelta
from database import (
    add_sample_data, get_all_books, insert_book, insert_borrow_record, update_book_availability, update_borrow_record_return_date
)

def test_add_sample_data():
    add_sample_data()
    books = get_all_books()
    titles = [book['title'] for book in books]
    assert "The Great Gatsby" in titles
    assert "To Kill a Mockingbird" in titles
    assert "1984" in titles

def test_insert_book_duplicate_isbn():
    assert insert_book("Book1", "Author1", "1234567890123", 1, 1) is True
    assert insert_book("Book2", "Author2", "1234567890123", 1, 1) is False

def test_insert_borrow_record_invalid_patron_id():
    assert insert_book("Book3", "Author3", "1234567890999", 1, 1) is True
    books = get_all_books()
    book_id = books[0]['id']
    result = insert_borrow_record(None, book_id, datetime.now(), datetime.now() + timedelta(days=14))
    assert result is False

def test_update_book_availability_none_change():
    assert insert_book("Book6", "Author6", "1234567890666", 1, 1) is True
    books = get_all_books()
    book_id = books[0]['id']
    result = update_book_availability(book_id, None)
    assert result is False

def test_update_borrow_record_return_date_invalid_type():
    result = update_borrow_record_return_date("123456", 1, None)
    assert result is False