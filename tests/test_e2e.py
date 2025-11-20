from playwright.sync_api import Playwright, sync_playwright, expect

def test_add_book_and_borrow(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("http://127.0.0.1:5000/catalog")
    # Adds book and fills information
    page.get_by_role("link", name="➕ Add Book").click()
    page.get_by_label("Title *").click()
    page.get_by_label("Title *").fill("Test Book")
    page.get_by_label("Author *").click()
    page.get_by_label("Author *").fill("Test Author")
    page.get_by_label("ISBN *").click()
    page.get_by_label("ISBN *").fill("1111111555555")
    page.get_by_label("Total Copies *").click()
    page.get_by_label("Total Copies *").fill("3")
    page.get_by_role("button", name="Add Book to Catalog").click()
    # Verifies book exists in catalog
    expect(page.get_by_role("cell", name="1111111555555")).to_be_visible()
    # Already on borrow book page, borrows book using patron ID
    page.get_by_placeholder("Patron ID (6 digits)").click()
    page.get_by_placeholder("Patron ID (6 digits)").fill("123456")
    page.get_by_role("button", name="Borrow").click()
    # Verifies the borrow confirmation message appears
    expect(page.get_by_text("Successfully borrowed \"Test")).to_be_visible()

    # ---------------------
    context.close()
    browser.close()

def test_add_book_and_search_by_author(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("http://127.0.0.1:5000/catalog")
    # Adds book and fills information
    page.get_by_role("link", name="➕ Add Book").click()
    page.get_by_label("Title *").click()
    page.get_by_label("Title *").fill("Best Book")
    page.get_by_label("Author *").click()
    page.get_by_label("Author *").fill("New Author")
    page.get_by_label("ISBN *").click()
    page.get_by_label("ISBN *").fill("2222222555555")
    page.get_by_label("Total Copies *").click()
    page.get_by_label("Total Copies *").fill("2")
    page.get_by_role("button", name="Add Book to Catalog").click()
    # Go to search page
    page.get_by_role("link", name="🔍 Search").click()
    # Change search type to author
    page.get_by_label("Search Type").select_option("author")
    # Enter search term and click search
    page.get_by_label("Search Term").click()
    page.get_by_label("Search Term").fill("New")
    page.get_by_role("button", name="🔍 Search").click()
    # Verify that the book shows up in the search
    expect(page.get_by_role("cell", name="2222222555555")).to_be_visible()

    # ---------------------
    context.close()
    browser.close()

def test_add_book_borrow_and_return(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("http://127.0.0.1:5000/catalog")
    # Adds book and fills information
    page.get_by_role("link", name="➕ Add Book").click()
    page.get_by_label("Title *").click()
    page.get_by_label("Title *").fill("Return Book")
    page.get_by_label("Author *").click()
    page.get_by_label("Author *").fill("Return Author")
    page.get_by_label("ISBN *").click()
    page.get_by_label("ISBN *").fill("4444444555555")
    page.get_by_label("Total Copies *").click()
    page.get_by_label("Total Copies *").fill("3")
    page.get_by_role("button", name="Add Book to Catalog").click()
    # Extract the book ID from the catalog table
    book_id = page.get_by_role("row", name="Return Book").locator("td").first.text_content()
    # Borrows book using patron ID
    page.get_by_placeholder("Patron ID (6 digits)").click()
    page.get_by_placeholder("Patron ID (6 digits)").fill("123456")
    page.get_by_role("button", name="Borrow").click()
    page.get_by_role("link", name="↩️ Return Book").click()
    # Use the extracted book ID to return the book
    page.get_by_label("Book ID *").click()
    page.get_by_label("Book ID *").fill(book_id)
    page.get_by_label("Patron ID *").click()
    page.get_by_label("Patron ID *").fill("123456")
    page.get_by_role("button", name="Process Return").click()
    # Verify the return was successful
    expect(page.get_by_text("Book \"Return Book\"")).to_be_visible()    

    # ---------------------
    context.close()
    browser.close()