import pytest
from unittest.mock import patch, MagicMock
from app.scraping.scrape_hn import load_hn_page, BASE_URL


# 1. Test Successful Page Load
@patch("time.sleep")  # Mocking time.sleep to avoid actual delay during tests
@patch("app.scraping.scrape_hn.webdriver.Chrome")
def test_load_hn_page_success(mock_webdriver, mock_sleep):
    # Create a mock driver
    mock_driver = MagicMock()
    mock_webdriver.return_value = mock_driver

    # Mock the driver.get call to simulate a successful page load
    mock_driver.get.reset_mock()  # Reset any prior mock calls

    # Call the function with page 1
    load_hn_page(mock_driver, 1)

    # Ensure driver.get was called with the correct URL
    mock_driver.get.assert_called_once_with(BASE_URL.format(1))

    # Ensure time.sleep(2) is called
    mock_sleep.assert_called_once_with(2)


# 2. Test ConnectionError when loading the page
@patch("app.scraping.scrape_hn.webdriver.Chrome")  # Patch the Chrome constructor to avoid actual browser initialization
@patch("app.scraping.scrape_hn.time.sleep")  # Patch sleep to prevent delay
def test_load_hn_page_connection_error(mock_sleep, mock_webdriver):
    # Create a mock driver
    mock_driver = MagicMock()
    mock_webdriver.return_value = mock_driver

    # Mock driver.get to raise an exception
    mock_driver.get.side_effect = Exception("Connection error")

    # Call the function with page 1 and expect a ConnectionError
    with pytest.raises(ConnectionError, match=r"Error reaching https://news\.ycombinator\.com/\?p=1\. Check the internet connection\."):
        load_hn_page(mock_driver, 1)

# 3. Test that time.sleep is called after page load
@patch("time.sleep")
@patch("app.scraping.scrape_hn.webdriver.Chrome")
def test_load_hn_page_sleep_called(mock_webdriver, mock_sleep):
    # Create a mock driver
    mock_driver = MagicMock()
    mock_webdriver.return_value = mock_driver

    # Call the function with page 1
    load_hn_page(mock_driver, 1)

    # Ensure time.sleep(2) was called
    mock_sleep.assert_called_once_with(2)
