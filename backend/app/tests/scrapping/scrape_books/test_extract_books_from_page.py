import pytest
from unittest.mock import MagicMock, patch
from bs4 import BeautifulSoup
from app.scraping.scrape_books import extract_books_from_page


# Fixture global para evitar que time.sleep ralentice los tests
@pytest.fixture(autouse=True)
def no_sleep():
    with patch("time.sleep", return_value=None):
        yield


# Mocking the helper variables and constants
BASE_URL = "https://books.toscrape.com/catalogue/page-{}.html"
DETAIL_URL_PREFIX = "https://books.toscrape.com/catalogue/"
IMAGE_BASE_URL = "https://books.toscrape.com/"


# Sample HTML to use in the tests
BOOK_PAGE_HTML = """
<html>
    <body>
        <ul class="breadcrumb">
            <li><a href="#">Books</a></li>
            <li><a href="#">Fiction</a></li>
            <li><a href="#">Sci-Fi</a></li>
        </ul>
        <div class="item active">
            <img src="../img/book.jpg" alt="Book Cover">
        </div>
    </body>
</html>
"""


CATALOG_PAGE_HTML = """
<html>
    <body>
        <article class="product_pod">
            <h3><a title="Book Title" href="book/1">Book Title</a></h3>
            <p class="price_color">£15.99</p>
        </article>
        <article class="product_pod">
            <h3><a title="Expensive Book" href="book/2">Expensive Book</a></h3>
            <p class="price_color">£25.99</p>
        </article>
    </body>
</html>
"""


# Test 1: Test successful book extraction
def test_extract_books_from_page_success():
    mock_driver = MagicMock()
    mock_driver.get = MagicMock()
    mock_driver.page_source = BOOK_PAGE_HTML

    soup = BeautifulSoup(CATALOG_PAGE_HTML, 'html.parser')
    books = extract_books_from_page(soup, mock_driver, 1)

    assert len(books) == 1
    assert books[0]["title"] == "Book Title"
    assert books[0]["price"] == "15.99"
    assert books[0]["category"] == "Sci-Fi"
    assert books[0]["image_url"] == "https://books.toscrape.com/img/book.jpg"


# Test 2: Ensure books with price > 20 are skipped
def test_extract_books_from_page_price_filter():
    mock_driver = MagicMock()
    mock_driver.get = MagicMock()
    mock_driver.page_source = BOOK_PAGE_HTML

    soup = BeautifulSoup(CATALOG_PAGE_HTML, 'html.parser')
    books = extract_books_from_page(soup, mock_driver, 2)

    assert len(books) == 1
    assert books[0]["title"] == "Book Title"


# Test 3: Handling missing elements or invalid structure
def test_extract_books_from_page_error_handling():
    mock_driver = MagicMock()
    mock_driver.get = MagicMock()

    broken_book_page_html = """
    <html>
        <body>
            <div class="item active">
                <img src="../img/book.jpg" alt="Book Cover">
            </div>
        </body>
    </html>
    """
    mock_driver.page_source = broken_book_page_html

    broken_catalog_html = """
    <html>
        <body>
            <article class="product_pod">
                <h3><a title="Book Title" href="/book/1">Book Title</a></h3>
                <p class="price_color">£15.99</p>
            </article>
        </body>
    </html>
    """
    soup = BeautifulSoup(broken_catalog_html, 'html.parser')
    books = extract_books_from_page(soup, mock_driver, 1)

    assert len(books) == 0


# Test 4: Ensure driver.get and time.sleep are called
def test_extract_books_from_page_driver_get_and_sleep():
    mock_driver = MagicMock()
    mock_driver.get = MagicMock()
    mock_driver.page_source = BOOK_PAGE_HTML

    soup = BeautifulSoup(CATALOG_PAGE_HTML, 'html.parser')

    with patch("time.sleep") as mock_sleep:
        extract_books_from_page(soup, mock_driver, 1)

        mock_driver.get.assert_called_with(
            "https://books.toscrape.com/catalogue/book/1"
            )
        mock_driver.get.assert_called_once()
        mock_sleep.assert_called_once_with(1)


# Test 5: Stop when 'remaining' limit is reached
def test_extract_books_from_page_remaining_limit():
    mock_driver = MagicMock()
    mock_driver.get = MagicMock()
    mock_driver.page_source = BOOK_PAGE_HTML

    soup = BeautifulSoup(CATALOG_PAGE_HTML, 'html.parser')
    books = extract_books_from_page(soup, mock_driver, 1)

    assert len(books) == 1
    assert books[0]["title"] == "Book Title"


# Test 6: Handle empty catalog page (no books)
def test_extract_books_from_page_empty_catalog():
    mock_driver = MagicMock()
    mock_driver.get = MagicMock()
    mock_driver.page_source = BOOK_PAGE_HTML

    empty_catalog_html = "<html><body></body></html>"
    soup = BeautifulSoup(empty_catalog_html, 'html.parser')
    books = extract_books_from_page(soup, mock_driver, 1)

    assert len(books) == 0
