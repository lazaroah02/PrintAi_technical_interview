import pytest
from unittest.mock import patch
from app.main import app 

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

@patch('app.main.requests.get')
@patch('app.main.requests.post')
def test_start_initial_books_scrape_with_books(mock_post, mock_get, client):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"total_books": 5}

    response = client.post('/start-initial-books-scrape')
    assert response.status_code == 200
    assert "Skipping scraper" in response.get_json()["message"]

@patch('app.main.requests.get')
@patch('app.main.requests.post')
def test_start_initial_books_scrape_without_books(mock_post, mock_get, client):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"total_books": 0}
    mock_post.return_value.status_code = 200

    response = client.post('/start-initial-books-scrape')
    assert response.status_code == 200
    assert "Scraper initialized" in response.get_json()["message"]

@patch('app.main.requests.get', side_effect=Exception("boom"))
def test_start_initial_books_scrape_exception(mock_get, client):
    response = client.post('/start-initial-books-scrape')
    assert response.status_code == 500
    assert "unexpected" in response.get_json()["message"].lower()
