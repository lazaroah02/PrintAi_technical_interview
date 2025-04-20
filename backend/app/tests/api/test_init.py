from unittest.mock import patch, MagicMock
from app.main import app 
import pytest

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

@patch('app.tasks.scrape_books_task.delay')
def test_init_success(mock_scrape_task, client):
    mock_task = MagicMock()
    mock_task.id = "1234"
    mock_scrape_task.return_value = mock_task
    response = client.post('/init')
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Books Scraping Started!"
    assert data["task_id"] == "1234"

@patch('app.tasks.scrape_books_task.delay', side_effect=Exception("error"))
def test_init_failure(mock_scrape_task, client):
    response = client.post('/init')
    assert response.status_code == 500
    data = response.get_json()
    assert "Error" in data["message"]