"""
Library Service Module - Business Logic Functions
Contains all the core business logic for the Library Management System
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from database import (
    get_book_by_id, get_book_by_isbn, get_patron_borrow_count,
    insert_book, insert_borrow_record, update_book_availability,
    update_borrow_record_return_date, get_all_books, get_patron_borrowed_books
)

def add_book_to_catalog(title: str, author: str, isbn: str, total_copies: int) -> Tuple[bool, str]:
    """
    Add a new book to the catalog.
    Implements R1: Book Catalog Management
    
    Args:
        title: Book title (max 200 chars)
        author: Book author (max 100 chars)
        isbn: 13-digit ISBN
        total_copies: Number of copies (positive integer)
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Input validation
    if not title or not title.strip():
        return False, "Title is required."
    
    if len(title.strip()) > 200:
        return False, "Title must be less than 200 characters."
    
    if not author or not author.strip():
        return False, "Author is required."
    
    if len(author.strip()) > 100:
        return False, "Author must be less than 100 characters."
    
    if len(isbn) != 13:
        return False, "ISBN must be exactly 13 digits."
    
    if not isinstance(total_copies, int) or total_copies <= 0:
        return False, "Total copies must be a positive integer."
    
    # Check for duplicate ISBN
    existing = get_book_by_isbn(isbn)
    if existing:
        return False, "A book with this ISBN already exists."
    
    # Insert new book
    success = insert_book(title.strip(), author.strip(), isbn, total_copies, total_copies)
    if success:
        return True, f'Book "{title.strip()}" has been successfully added to the catalog.'
    else:
        return False, "Database error occurred while adding the book."

def borrow_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Allow a patron to borrow a book.
    Implements R3 as per requirements  
    
    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book to borrow
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."
    
    # Check if book exists and is available
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."
    
    if book['available_copies'] <= 0:
        return False, "This book is currently not available."
    
    # Check patron's current borrowed books count
    current_borrowed = get_patron_borrow_count(patron_id)
    
    if current_borrowed >= 5:
        return False, "You have reached the maximum borrowing limit of 5 books."
    
    # Create borrow record
    borrow_date = datetime.now()
    due_date = borrow_date + timedelta(days=14)
    
    # Insert borrow record and update availability
    borrow_success = insert_borrow_record(patron_id, book_id, borrow_date, due_date)
    if not borrow_success:
        return False, "Database error occurred while creating borrow record."
    
    availability_success = update_book_availability(book_id, -1)
    if not availability_success:
        return False, "Database error occurred while updating book availability."
    
    return True, f'Successfully borrowed "{book["title"]}". Due date: {due_date.strftime("%Y-%m-%d")}.'

def return_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Process book return by a patron.
    
    TODO: Implement R4 as per requirements
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "This is an invalid patron ID. Must be exactly 6 digits."
    
    # Check if book exists
    book = get_book_by_id(book_id)
    if not book:
        return False, "This is an invalid book."
    
    # Check if the patron has borrowed this book and not yet returned it
    borrowed_books = get_patron_borrowed_books(patron_id)
    has_borrowed = any(b['book_id'] == book_id for b in borrowed_books)
    if not has_borrowed:
        return False, "Not currently borrowed by this patron."
    
    # Use the late fee calculation function
    late_fee_info = calculate_late_fee_for_book(patron_id, book_id)
    late_fee_msg = ""
    if late_fee_info['days_overdue'] > 0 and late_fee_info['fee_amount'] > 0:
        late_fee_msg = f" late fee: ${late_fee_info['fee_amount']:.2f} for {late_fee_info['days_overdue']} days overdue."
    
    # Update the borrow record with the return date
    return_date = datetime.now()
    update_success = update_borrow_record_return_date(patron_id, book_id, return_date)
    if not update_success:
        return False, "Database error occured while updating return date."
    
    # Increase the available copies of the book
    availability_success = update_book_availability(book_id, 1)
    if not availability_success:
        return False, "Database error occured while updating book availability."

    return True, f'Book "{book["title"]}" successfully returned.{late_fee_msg}'

def calculate_late_fee_for_book(patron_id: str, book_id: int) -> Dict:
    """
    Calculate late fees for a specific book.
    
    TODO: Implement R5 as per requirements 
    
    
    return { // return the calculated values
        'fee_amount': 0.00,
        'days_overdue': 0,
        'status': 'Late fee calculation not implemented'
    }
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return {'fee_amount': 0.0, 'days_overdue': 0}
    
    # Check if book exists
    book = get_book_by_id(book_id)
    if not book:
        return {'fee_amount': 0.0, 'days_overdue': 0}
    
    # Find the active borrow record for this patron and book
    borrowed_books = get_patron_borrowed_books(patron_id)
    borrow_record = None
    for b in borrowed_books:
        if b['book_id'] == book_id:
            borrow_record = b
            break

    if not borrow_record or 'due_date' not in borrow_record:
        return {'fee_amount': 0.0, 'days_overdue': 0}
    
    # Parse due_date if it's a string
    due_date = borrow_record['due_date']
    if isinstance(due_date, str):
        try:
            due_date = datetime.fromisoformat(due_date)
        except Exception:
            due_date = datetime.strptime(due_date, "%Y-%m-%d %H:%M:%S")

    today = datetime.now()
    days_overdue = (today.date() - due_date.date()).days

    if days_overdue <= 0:
        return {'fee_amount': 0.0, 'days_overdue': 0}

    if days_overdue <= 7:
        fee = days_overdue * 0.5
    else:
        fee = 7 * 0.5 + (days_overdue - 7) * 1.0
    fee = min(fee, 15.0)

    return {'fee_amount': round(fee, 2), 'days_overdue': days_overdue}

def search_books_in_catalog(search_term: str, search_type: str) -> List[Dict]:
    """
    Search for books in the catalog.
    
    TODO: Implement R6 as per requirements
    """
    search_term = search_term.strip()
    if not search_term:
        return []

    books = get_all_books()
    results = []

    if search_type == "title":
        # Case-insensitive, partial match
        results = [b for b in books if search_term.lower() in b['title'].lower()]
    elif search_type == "author":
        # Case-insensitive, partial match
        results = [b for b in books if search_term.lower() in b['author'].lower()]
    elif search_type == "isbn":
        # Exact match only
        results = [b for b in books if b['isbn'] == search_term]
    else:
        results = []

    return results

def get_patron_status_report(patron_id: str) -> Dict:
    """
    Get status report for a patron.
    
    TODO: Implement R7 as per requirements
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return {
            'currently_borrowed': [],
            'total_late_fees': 0.0,
            'num_currently_borrowed': 0,
            'history': []
        }
    
    # Get all borrow records for this patron
    all_borrows = []
    conn = None
    try:
        from database import get_db_connection
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT br.*, b.title, b.author, b.isbn
            FROM borrow_records br
            JOIN books b ON br.book_id = b.id
            WHERE br.patron_id = ?
            ORDER BY br.borrow_date DESC
        """, (patron_id,))
        all_borrows = [dict(row) for row in cur.fetchall()]
    finally:
        if conn:
            conn.close()

    currently_borrowed = []
    total_late_fees = 0.0
    history = []

    now = datetime.now()

    for record in all_borrows:
        # Parse due_date and return_date
        due_date = record['due_date']
        if isinstance(due_date, str):
            try:
                due_date_dt = datetime.fromisoformat(due_date)
            except Exception:
                due_date_dt = datetime.strptime(due_date, "%Y-%m-%d %H:%M:%S")
        else:
            due_date_dt = due_date

        return_date = record['return_date']
        if return_date:
            if isinstance(return_date, str):
                try:
                    return_date_dt = datetime.fromisoformat(return_date)
                except Exception:
                    return_date_dt = datetime.strptime(return_date, "%Y-%m-%d %H:%M:%S")
            else:
                return_date_dt = return_date
        else:
            return_date_dt = None

        book_info = {
            'title': record['title'],
            'author': record['author'],
            'isbn': record['isbn'],
            'borrow_date': record['borrow_date'],
            'due_date': record['due_date'],
            'return_date': record['return_date']
        }

        # If not yet returned
        if not return_date_dt:
            is_overdue = now > due_date_dt
            book_info['is_overdue'] = is_overdue
            currently_borrowed.append(book_info)
            # Calculate late fee for overdue books
            if is_overdue:
                days_overdue = (now.date() - due_date_dt.date()).days
                total_late_fees += round(days_overdue * 0.5, 2)
        # Add to history regardless
        history.append(book_info)

    return {
        'currently_borrowed': currently_borrowed,
        'total_late_fees': round(total_late_fees, 2),
        'num_currently_borrowed': len(currently_borrowed),
        'history': history
    }
