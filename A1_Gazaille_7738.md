Name: Zachary Gazaille
ID: 20387738
Group Number: 2

| Function Name                | Implementation  | What is Missing              |
|------------------------------|-----------------|------------------------------|
| add_book_to_catalog          | Complete        | Nothing                      |
|-------------------------------------------------------------------------------|
| borrow_book_by_patron        | Complete        | Nothing                      |
|-------------------------------------------------------------------------------|
| return_book_by_patron        | Not Implemented | Needs to accept patron ID    |
|                              |                 | and book ID as parameters,   |
|                              |                 | verify that book was         |
|                              |                 | borrowed by patron, update   |
|                              |                 | available copies, record     |
|                              |                 | return date and call         |
|                              |                 | calculate_late_fees_for_book |
|------------------------------|-----------------|------------------------------|
| calculate_late_fees_for_book | Not Implemented | Needs to retrieve the borrow |
|                              |                 | record for the given patron  |
|                              |                 | and book using the function  |
|                              |                 | get_patron_status_report,    |
|                              |                 | check the book's due date,   |
|                              |                 | subtract it from the current |
|                              |                 | date, then multiply the      |
|                              |                 | first 7 days by $0.50        |
|                              |                 | following days by $1.00. If  |
|                              |                 | the total exceeds $15.00,    |
|                              |                 | change it to just $15.00.    |
|                              |                 | Then return a JSON           |
|                              |                 | dictionary with the fee      |
|                              |                 | amount and days overdue      |
|------------------------------|-----------------|------------------------------|
| search_books_in_catalog      | Not Implemented | Needs to accept the          |
|                              |                 | search_type. If the type is  |
|                              |                 | ISBN, query the database for |
|                              |                 | the exact search_term.       |
|                              |                 | Otherwise, perform a         |
|                              |                 | partial, case-insensitive    |
|                              |                 | search for the title or      |
|                              |                 | author. Then, return the     |
|                              |                 | results in the same format   |
|                              |                 | as catalog display           |
|------------------------------|-----------------|------------------------------|
| get_patron_status_report     | Not Implemented | Needs to retrieve patron     |
|                              |                 | borrowed books by calling    |
|                              |                 | get_patron_borrowed_books.   |
|                              |                 | For each book, it needs to   |
|                              |                 | include the due dates. Then, |
|                              |                 | it needs to pass the patron  |
|                              |                 | id and book id to            |
|                              |                 | calculate_late_fees_for_book |
|                              |                 | and sum up the total late    |
|                              |                 | fees for the patron. Then,   |
|                              |                 | It sums up the number of     |
|                              |                 | currently borrowed books.    |
|                              |                 | Finally, we need a new       |
|                              |                 | helper function to query     |
|                              |                 | borrowing histroy. it will   |
|                              |                 | pretty much match            |
|                              |                 | get_patron_borrowed_books    |
|                              |                 | except not only books with a |
|                              |                 | null return date. Then, it   |
|                              |                 | needs to display all this    |
|                              |                 | information                  |
|-------------------------------------------------------------------------------|

TESTS:

add_book_to_catalog_test
- Test adds a book successfully with valid input and expects a success message
- Test adds a book with an ISBN that is too short and expects an error message
- Test adds a book with an ISBN that is too long and expects an error message
- Test adds adds a book missing a Title and expects an error message
- Test adds a book with a Title that is too long and expects an error message
- Test adds a book with no author and expects an error message
- Test adds a book with an author that is too long and expects an error message
- Test adds a book with negative copies and expects an error message
- Test adds a book and then adds another book with the same ISBN and expects an error message

borrow_book_by_patron_test
- Test adds a book to the catalog and then successfully borrows the book with valid input and expects a success message
- Test adds a book to the catalog and then borrows it with a patron ID that is too short. Test expects an error message.
- Test adds a book to the catalog and then borrows it with a patron ID that is too long. Test expects an error message.
- Test attempts to borrow a book that isn't in the catalog. Test expects an error message.
- Test adds a book with 1 copy, borrows the book using a patron ID, then attempts to borrow the same book with a different patron ID. Test expects an error message.
- Test adds 6 books to the catalog and then attempts to borrow the 6 books with the same patron ID but the max available borrowed books is 5. Test expects an error message.

calculate_late_fees_for_book_test
- Test adds a book, borrows it and immediately calculates fees. Expects 0.0 fees and 0 days overdue.
- Test adds a book, makes a due date that is 5 days ago, makes a borrow date 14 days before the borrow date, inserts a borrow record with those due and borrow dates then calculates fees. Expects 2.5 fees and 5 days overdue.
- Test adds a book, makes a due date that is 10 days ago, makes a borrow date 14 days before the borrow date, inserts a borrow record with those due and borrow dates then calculates fees. Expects 6.5 fees and 10 days overdue.
- Test adds a book, makes a due date that is 30 days ago, makes a borrow date 14 days before the borrow date, inserts a borrow record with those due and borrow dates then calculates fees. Expects 15.0 fees and 30 days overdue.
- Test adds a book and attempts to calculate late fees with a patron ID that is too short. Expects 0.0 fees and 0 days.
- Test adds a book and attempts to calculate late fees with a patron ID that is too long. Expects 0.0 fees and 0 days.
- Test attempts to calculate fees for a book that doesn't exist. Expects 0.0 fees and 0 days.

get_patron_status_report_test
- Test retrieves the patron report for a patron that has no books. Expects 0 currently_borrowed, 0.0 total_late_fees, 0 num_currently_borrowed and an empty history
- Test adds a book, borrows it using a patron and then retrieves the patron report for that patron. Expects the name of the first book in currently_borrowed to be "Test Book", 0.0 total_late_fees, 1 num_currently_borrowed and a history of length 1.
- Test adds a book, adds a borrow record that is 5 days overdue to a patron and then retrieves the patron report for that patron. Expects the name of the first book in currently_borrowed to be "Test Book", the is_overdue parameter for that book to be True, total_late_fees greater than 0.0, 1 num_currently_borrowed and a history of length 1.
- Test adds a book, borrows it using a patron, updates the return date to be today and then retrieves the patron report for that patron. Expects currently_borrowed to be empty, 0.0 total_late_fees, 0 num_currently_borrowed, a history of length 1 and the title of the first book in history to be "Test Book".
- Test adds 5 books, borrows those 5 books using a patron, then retrieves the patron report for that patron. Expects the length of currently_borrowed to be 5, 5 num_currently_borrowed and a history of length 5.
- Test attempts to get the patron report for a patron with a patron ID that is too short. Expects currently_borrowed to be empty, 0.0 total_late_fees, 0 num_currently_borrowed, and an empty history.
- Test attempts to get the patron report for a patron with a patron ID that is too long. Expects currently_borrowed to be empty, 0.0 total_late_fees, 0 num_currently_borrowed, and an empty history.

return_book_by_patron_test
- Test adds a book, borrows it using a patron ID and then successfully returns the book. Expects a success message.
- Test adds a book, then makes a borrow record that is overdue. Then, it returns the book. Excpects a success message and a mention of a late fee in the return message.
- Test adds a book, doesn't borrow it and then attempts to return it. Expects an error message.
- Test attempts to return a book without adding it. Expects an error message.
- Test adds a book and attempts to return it with a patron ID that is too short. Expects an error mesage.
- Test adds a book and attempts to return it with a patron ID that is too long. Expects an error mesage.

search_books_in_catalog_test
- Test adds a book and then performs a search by its title. Expects more than 0 search results.
- Test adds a book and then performs a search by a part of its title. Expects more than 0 search results.
- Test adds a book and then performs a search by a title that doesn't match any book. Expects 0 search results.
- Test adds a book and then performs a search by its author. Expects more than 0 search results.
- Test adds a book and then performs a search by a part of its author. Expects more than 0 search results.
- Test adds a book and then performs a search by an author that doesn't exist. Expects 0 search results.
- Test adds a book and then performs a search by its ISBN. Expects 1 search result.
- Test adds a book and then performs a search by a part of its ISBN. Expects 0 search result because you can't search by a partial ISBN.
- Test adds a book and then performs a search by an ISBN that doesn't exist. Expects 0 search result.
