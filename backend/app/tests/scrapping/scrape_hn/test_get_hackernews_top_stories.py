import pytest
from unittest.mock import patch, MagicMock
from selenium.common.exceptions import WebDriverException

# Asume que estas funciones están en el mismo módulo
from app.scraping.scrape_hn import get_hackernews_top_stories

@patch("app.scraping.scrape_hn.webdriver.Chrome")
@patch("app.scraping.scrape_hn.build_chrome_options")
@patch("app.scraping.scrape_hn.load_hn_page")
@patch("app.scraping.scrape_hn.extract_stories")
@patch("app.scraping.scrape_hn.go_to_next_page")
def test_get_hackernews_top_stories_success(mock_next, mock_extract, mock_load, mock_opts, mock_chrome):
    # Setup
    mock_driver = MagicMock()
    mock_chrome.return_value = mock_driver
    mock_extract.return_value = [{"title": "Sample", "url": "https://x.com", "score": 100}]
    
    # Execute
    stories = get_hackernews_top_stories(page=1)

    # Assertions
    mock_chrome.assert_called_once()
    mock_load.assert_called_once_with(mock_driver, 1)
    mock_extract.assert_called_once_with(mock_driver)
    mock_next.assert_called_once_with(mock_driver)
    mock_driver.quit.assert_called_once()

    assert len(stories) == 1
    assert stories[0]["title"] == "Sample"


@patch("app.scraping.scrape_hn.webdriver.Chrome", side_effect=WebDriverException("Driver failed"))
@patch("app.scraping.scrape_hn.build_chrome_options")
def test_get_hackernews_top_stories_webdriver_exception(mock_opts, mock_chrome):
    with pytest.raises(WebDriverException, match="Driver failed"):
        get_hackernews_top_stories()


@patch("app.scraping.scrape_hn.webdriver.Chrome")
@patch("app.scraping.scrape_hn.build_chrome_options")
@patch("app.scraping.scrape_hn.load_hn_page", side_effect=ConnectionError("No internet"))
def test_get_hackernews_top_stories_connection_error(mock_load, mock_opts, mock_chrome):
    with pytest.raises(ConnectionError, match="No internet"):
        get_hackernews_top_stories()


@patch("app.scraping.scrape_hn.webdriver.Chrome")
@patch("app.scraping.scrape_hn.build_chrome_options")
@patch("app.scraping.scrape_hn.load_hn_page", side_effect=Exception("Something broke"))
def test_get_hackernews_top_stories_unexpected_error(mock_load, mock_opts, mock_chrome):
    with pytest.raises(Exception, match="Something broke"):
        get_hackernews_top_stories()


@patch("app.scraping.scrape_hn.webdriver.Chrome")
@patch("app.scraping.scrape_hn.build_chrome_options")
@patch("app.scraping.scrape_hn.load_hn_page", side_effect=Exception("Something broke"))
def test_get_hackernews_top_stories_unexpected_error(mock_load, mock_opts, mock_chrome):
    with pytest.raises(Exception, match="Something broke"):
        get_hackernews_top_stories()


@patch("app.scraping.scrape_hn.webdriver.Chrome")
@patch("app.scraping.scrape_hn.build_chrome_options")
@patch("app.scraping.scrape_hn.load_hn_page", side_effect=ConnectionError("fail"))
def test_driver_quit_called_on_exception(mock_load, mock_opts, mock_chrome):
    mock_driver = MagicMock()
    mock_chrome.return_value = mock_driver

    with pytest.raises(ConnectionError):
        get_hackernews_top_stories()

    assert mock_driver.quit.call_count == 3

