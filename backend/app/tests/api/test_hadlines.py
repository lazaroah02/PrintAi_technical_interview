import pytest
from unittest.mock import patch
from app.main import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

# Mock con noticias realistas
mock_news = [
    {"title": "Noticia 1", "url": "https://example.com/1", "score": 120},
    {"title": "Noticia 2", "url": "https://example.com/2", "score": 95},
    {"title": "Noticia 3", "url": "https://example.com/3", "score": 88},
]

@patch('app.main.get_hackernews_top_stories')
def test_headlines_success(mock_get_hn, client):
    mock_get_hn.return_value = mock_news

    response = client.get('/headlines')
    assert response.status_code == 200
    data = response.get_json()

    assert data["message"] == "Success!"
    assert isinstance(data["data"], list)
    assert len(data["data"]) == 3

    for story in data["data"]:
        assert "title" in story
        assert "url" in story
        assert "score" in story

@patch('app.main.get_hackernews_top_stories', side_effect=Exception("error"))
def test_headlines_failure(mock_get_hn, client):
    response = client.get('/headlines')
    assert response.status_code == 500
    assert "Error getting the news" in response.get_json()["message"]

@patch('app.main.get_hackernews_top_stories')
def test_headlines_custom_page(mock_get_hn, client):
    mock_get_hn.return_value = mock_news

    response = client.get('/headlines?page=2')
    assert response.status_code == 200
    data = response.get_json()

    assert isinstance(data["data"], list)
    assert "title" in data["data"][0]
    assert "url" in data["data"][0]
    assert "score" in data["data"][0]
