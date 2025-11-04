from services.library_service import (
    get_all_books,
    insert_book,
    borrow_book_by_patron,
    get_book_by_isbn,
)

def test_catalog_empty_initially():
    """Test catalog is empty when no books are added."""
    books = get_all_books()
    assert books == []

def test_catalog_shows_added_book():
    """Test catalog returns all added books with correct fields."""
    insert_book("Test Book", "Test Author", "1234567890999", 3, 3)
    books = get_all_books()
    assert len(books) == 1
    book = books[0]
    assert book['title'] == "Test Book"
    assert book['author'] == "Test Author"
    assert book['isbn'] == "1234567890999"
    assert book['total_copies'] == 3
    assert book['available_copies'] == 3

def test_catalog_after_borrowing():
    """Test available copies updates after borrowing."""
    insert_book("Another Book", "Another Author", "1234567890888", 2, 2)
    book = get_book_by_isbn("1234567890888")
    borrow_book_by_patron("123456", book['id'])
    books = get_all_books()
    for b in books:
        if b['isbn'] == "1234567890888":
            assert b['available_copies'] == 1

def test_catalog_no_negative_available_copies():
    """Test catalog does not show negative available copies."""
    insert_book("Unique Book", "Unique Author", "1234567890777", 1, 1)
    book = get_book_by_isbn("1234567890777")
    borrow_book_by_patron("123456", book['id'])
    borrow_book_by_patron("123457", book['id'])
    books = get_all_books()
    for b in books:
        if b['isbn'] == "1234567890777":
            assert b['available_copies'] >= 0

def test_catalog_fields_present():
    """Test that all required fields are present for each book in the catalog."""
    insert_book("Field Test Book", "Field Author", "1234567890666", 4, 4)
    books = get_all_books()
    required_fields = {'id', 'title', 'author', 'isbn', 'available_copies', 'total_copies'}
    for book in books:
        assert required_fields.issubset(book.keys())