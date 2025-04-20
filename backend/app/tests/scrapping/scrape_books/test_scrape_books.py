from unittest.mock import patch, MagicMock
from app.scraping.scrape_books import scrape_books


# Test 1: Successful scraping flow
@patch("app.scraping.scrape_books.save_books_into_redis_database")
@patch("app.scraping.scrape_books.extract_books_from_page")
@patch("app.scraping.scrape_books.get_catalog_page")
@patch("app.scraping.scrape_books.webdriver.Chrome")
def test_scrape_books_success(
        mock_chrome,
        mock_get_catalog,
        mock_extract, mock_save
        ):
    mock_driver = MagicMock()
    mock_chrome.return_value = mock_driver
    mock_get_catalog.return_value = "soup"
    mock_extract.side_effect = [
        [{"title": "Book 1"}, {"title": "Book 2"}],
        [{"title": "Book 3"}],
        []
    ]

    scrape_books(limit=3)

    assert mock_extract.call_count == 2  # Two calls until limit is reached
    mock_save.assert_called_once_with(
        [{"title": "Book 1"}, {"title": "Book 2"}, {"title": "Book 3"}]
    )
    mock_driver.quit.assert_called_once()


# Test 2: Skip a page when an error occurs
@patch("app.scraping.scrape_books.save_books_into_redis_database")
@patch(
    "app.scraping.scrape_books.extract_books_from_page",
    side_effect=Exception("boom")
    )
@patch("app.scraping.scrape_books.get_catalog_page")
@patch("app.scraping.scrape_books.webdriver.Chrome")
def test_scrape_books_page_error(
        mock_chrome,
        mock_get_catalog,
        mock_extract,
        mock_save
        ):
    mock_driver = MagicMock()
    mock_chrome.return_value = mock_driver
    mock_get_catalog.return_value = "soup"

    scrape_books(limit=3)

    mock_extract.assert_called_once()
    mock_save.assert_called_once_with([])  # No books extracted
    mock_driver.quit.assert_called_once()


# Test 4: Break loop when no books are returned
@patch("app.scraping.scrape_books.save_books_into_redis_database")
@patch("app.scraping.scrape_books.extract_books_from_page", return_value=[])
@patch("app.scraping.scrape_books.get_catalog_page")
@patch("app.scraping.scrape_books.webdriver.Chrome")
def test_scrape_books_break_on_empty(
        mock_chrome,
        mock_get_catalog,
        mock_extract,
        mock_save
        ):
    mock_driver = MagicMock()
    mock_chrome.return_value = mock_driver
    mock_get_catalog.return_value = "soup"

    scrape_books(limit=5)

    mock_extract.assert_called_once()  # Loop breaks when books == []
    mock_save.assert_called_once_with([])
    mock_driver.quit.assert_called_once()


# Test 5: Always close the browser (finally block)
@patch("app.scraping.scrape_books.webdriver.Chrome")
def test_scrape_books_driver_quit_called(mock_chrome):
    mock_driver = MagicMock()
    mock_chrome.return_value = mock_driver

    with patch(
            "app.scraping.scrape_books.get_catalog_page",
            side_effect=Exception("error")
            ), \
            patch("app.scraping.scrape_books.logging.warning"), \
            patch("app.scraping.scrape_books.extract_books_from_page"), \
            patch("app.scraping.scrape_books.save_books_into_redis_database"):

        scrape_books(limit=5)
        mock_driver.quit.assert_called_once()
