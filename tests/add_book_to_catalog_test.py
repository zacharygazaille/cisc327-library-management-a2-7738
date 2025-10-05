import pytest
from library_service import (
    add_book_to_catalog
)
from database import (
    insert_book
)

def test_add_book_valid_input():
    """Test adding a book with valid input."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", 5)
    
    assert success == True
    assert "successfully added" in message

def test_add_book_invalid_isbn_too_short():
    """Test adding a book with ISBN too short."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "123456789", 5)
    
    assert success == False
    assert "ISBN must be exactly 13 digits." in message

def test_add_book_invalid_isbn_too_long():
    """Test adding a book with ISBN too long."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "12345678901234", 5)
    
    assert success == False
    assert "ISBN must be exactly 13 digits." in message
    
def test_add_book_no_title():
    """Test adding a book with no Title."""
    success, message = add_book_to_catalog("", "Test Author", "1234567890124", 5)
    
    assert success == False
    assert "Title is required." in message

def test_add_book_title_too_long():
    """Test adding a book a Title that is too long"""
    success, message = add_book_to_catalog("12345678901234567890\
                                           12345678901234567890\
                                           12345678901234567890\
                                           12345678901234567890\
                                           12345678901234567890\
                                           12345678901234567890\
                                           12345678901234567890\
                                           12345678901234567890\
                                           12345678901234567890\
                                           123456789012345678901", "Test Author", "1234567890124", 5)
    
    assert success == False
    assert "Title must be less than 200 characters." in message

def test_add_book_no_author():
    """Test adding a book with no Author."""
    success, message = add_book_to_catalog("Test Book", "", "1234567890124", 5)
    
    assert success == False
    assert "Author is required." in message

def test_add_book_author_too_long():
    """Test adding a book an Author that is too long"""
    success, message = add_book_to_catalog("Test Book",
                                           "12345678901234567890\
                                           12345678901234567890\
                                           12345678901234567890\
                                           12345678901234567890\
                                           123456789012345678901", "1234567890124", 5)
    
    assert success == False
    assert "Author must be less than 100 characters." in message

def test_add_book_negative_copies():
    """Test adding a book with a negative amount of copies"""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890124", -5)
    
    assert success == False
    assert "Total copies must be a positive integer." in message

def test_add_book_isbn_exists():
    """Test adding a book with an ISBN that already exists"""
    insert_book("Test Book", "Test Author", "1234567890124", 5, 5)
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890124", 5)
    
    assert success == False
    assert "A book with this ISBN already exists." in message