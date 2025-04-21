from unittest.mock import MagicMock, patch
from app.scraping.scrape_hn import extract_stories
from selenium.common.exceptions import NoSuchElementException


# Sample mock data for the test
items = [
    MagicMock(),
    MagicMock()
]


subtexts = [
    MagicMock(),
    MagicMock()
]


# 1. Test Successful Story Extraction
@patch("app.scraping.scrape_hn.webdriver.Chrome")
def test_extract_stories_success(mock_chrome):
    # Create a mock driver instance
    mock_driver = MagicMock()

    # Prepare mock elements for items and subtexts
    items = [
        MagicMock(),
        MagicMock()
    ]
    subtexts = [
        MagicMock(),
        MagicMock()
    ]

    # Mock the return values for elements
    example_url1 = "https://example.com/story1"
    example_url2 = "https://example.com/story2"
    return_value1 = items[0].find_element.return_value
    return_value1.text = "Story Title 1"
    return_value1.get_attribute.return_value = example_url1
    subtexts[0].find_element.return_value.text = "100 points"

    return_value2 = items[1].find_element.return_value
    return_value2.text = "Story Title 2"
    return_value2.get_attribute.return_value = example_url2
    subtexts[1].find_element.return_value.text = "200 points"

    # Mock `find_elements` on the driver to return both items and subtexts
    # First return items, then subtexts
    mock_driver.find_elements.side_effect = [items, subtexts]

    # Patch the driver object and call extract_stories
    mock_chrome.return_value = mock_driver
    response = extract_stories(mock_driver)

    # Ensure stories are extracted correctly
    assert response.total == 2
    assert response.stories[0].title == "Story Title 1"
    assert str(response.stories[0].url) == "https://example.com/story1"  # Convert HttpUrl to string
    assert response.stories[0].score == 100
    assert response.stories[1].title == "Story Title 2"
    assert str(response.stories[1].url) == "https://example.com/story2"  # Convert HttpUrl to string
    assert response.stories[1].score == 200


# 2. Test Missing Elements (e.g., No Title or Score)
@patch("app.scraping.scrape_hn.webdriver.Chrome")
def test_extract_stories_missing_elements(mock_find_elements):
    # Prepare mock elements
    items[0].find_element.side_effect = NoSuchElementException(
        "Missing title element"
        )
    subtexts[0].find_element.side_effect = NoSuchElementException(
        "Missing score element"
        )

    # Mock both items and subtexts
    mock_find_elements.return_value = items + subtexts

    # Call the function and check that no story is extracted
    response = extract_stories(mock_find_elements)
    assert response.total == 0


# 3. Test Empty Page
@patch("app.scraping.scrape_hn.webdriver.Chrome")
def test_extract_stories_empty_page(mock_find_elements):
    # Prepare mock elements with empty lists
    mock_find_elements.return_value = []

    # Call the function with an empty page
    response = extract_stories(mock_find_elements)

    # Ensure no stories are returned
    assert response.total == 0


# 4. Test Invalid Score Format
@patch("app.scraping.scrape_hn.webdriver.Chrome")
def test_extract_stories_invalid_score(mock_find_elements):
    # Prepare mock elements with invalid score format (e.g., no number)
    items[0].find_element.return_value.text = "Story Title 1"
    example_url = "https://example.com/story1"
    items[0].find_element.return_value.get_attribute.return_value = example_url
    subtexts[0].find_element.return_value.text = "Invalid score format"

    # Mock both items and subtexts
    mock_find_elements.return_value = items + subtexts

    # Call the function and check if it handles the invalid score gracefully
    response = extract_stories(mock_find_elements)

    # Ensure that the story is not included due to invalid score
    assert response.total == 0
