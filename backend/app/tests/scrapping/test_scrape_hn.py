import pytest
from unittest.mock import patch, MagicMock
from app.scraping.scrape_hn import get_hackernews_top_stories


@pytest.fixture
def mock_webdriver():
    with patch("app.scraping.scrape_hn.webdriver.Chrome") as mock_driver:
        mock_instance = MagicMock()
        mock_driver.return_value = mock_instance
        yield mock_instance


def test_get_hackernews_top_stories_success(mock_webdriver):
    # Mock the elements returned by Selenium
    mock_item = MagicMock()
    mock_item.find_element.return_value.text = "Test Story"
    mock_item.find_element.return_value.get_attribute.return_value = (
        "http://example.com"
    )

    mock_subtext = MagicMock()
    mock_subtext.find_element.return_value.text = "100 points"

    mock_webdriver.find_elements.side_effect = [[mock_item], [mock_subtext]]

    stories = get_hackernews_top_stories(page=1)

    assert len(stories) == 1
    assert stories[0]["title"] == "Test Story"
    assert stories[0]["url"] == "http://example.com"
    assert stories[0]["score"] == 100


def test_get_hackernews_top_stories_no_items(mock_webdriver):
    # Mock no items found
    mock_webdriver.find_elements.side_effect = [[], []]

    stories = get_hackernews_top_stories(page=1)

    assert len(stories) == 0


def test_get_hackernews_top_stories_connection_error(mock_webdriver):
    # Simulate a connection error
    mock_webdriver.get.side_effect = Exception(
        "Connection Error: Error reaching https://news.ycombinator.com/?p=1. "
        "Check the internet connection"
    )

    with pytest.raises(
        Exception,
        match=(
            r"Connection Error: Error reaching https://news\.ycombinator\.com/"
            r"\?p=1\. Check the internet connection"
        )
    ):
        get_hackernews_top_stories(page=1)
