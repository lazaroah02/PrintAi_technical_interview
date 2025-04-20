import pytest
from unittest.mock import MagicMock, patch
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from app.scraping.scrape_books import get_catalog_page, BASE_URL


# Fixture para desactivar time.sleep en todos los tests
@pytest.fixture(autouse=True)
def no_sleep():
    with patch("time.sleep", return_value=None):
        yield


def test_get_catalog_page_success():
    mock_driver = MagicMock()
    mock_driver.get = MagicMock()
    mock_driver.page_source = "<html><body>Catalog Page</body></html>"
    mock_driver.find_elements = MagicMock(return_value=[])

    result = get_catalog_page(mock_driver, 1)

    mock_driver.get.assert_called_with(BASE_URL.format(1))
    assert isinstance(result, BeautifulSoup)
    assert "Catalog Page" in result.prettify()


def test_get_catalog_page_not_found():
    mock_driver = MagicMock()
    mock_driver.get = MagicMock()
    mock_driver.page_source = "<html><body>Catalog Page</body></html>"
    mock_driver.find_elements = MagicMock(return_value=[MagicMock()])

    with pytest.raises(ValueError, match="Page 1 not found."):
        get_catalog_page(mock_driver, 1)


def test_get_catalog_page_timeout():
    mock_driver = MagicMock()
    mock_driver.get = MagicMock(side_effect=TimeoutException)

    with pytest.raises(TimeoutException):
        get_catalog_page(mock_driver, 1)


def test_get_catalog_page_empty_content():
    mock_driver = MagicMock()
    mock_driver.get = MagicMock()
    mock_driver.page_source = "<html><body></body></html>"
    mock_driver.find_elements = MagicMock(return_value=[])

    result = get_catalog_page(mock_driver, 1)

    assert isinstance(result, BeautifulSoup)
    assert "body" in result.prettify()


def test_get_catalog_page_with_sleep_called():
    mock_driver = MagicMock()
    mock_driver.get = MagicMock()
    mock_driver.page_source = "<html><body>Catalog Page</body></html>"
    mock_driver.find_elements = MagicMock(return_value=[])

    with patch("time.sleep") as mock_sleep:
        get_catalog_page(mock_driver, 1)
        mock_sleep.assert_called_once_with(2)


def test_get_catalog_page_logging_timeout():
    mock_driver = MagicMock()
    mock_driver.get = MagicMock(side_effect=TimeoutException)

    with patch("logging.warning") as mock_warning:
        with pytest.raises(TimeoutException):
            get_catalog_page(mock_driver, 1)

        mock_warning.assert_called_once_with("Timeout on page 1")
