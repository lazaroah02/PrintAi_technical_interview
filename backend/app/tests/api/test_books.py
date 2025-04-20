import json
import pytest
from unittest.mock import patch, MagicMock
from app.main import app


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


@patch('app.main.redis.Redis')
def test_books_success(mock_redis, client):
    mock_r = MagicMock()
    mock_redis.return_value = mock_r
    mock_r.keys.return_value = [b'book:1']
    mock_r.get.return_value = json.dumps({
        "url": "https://example.com/book1",
        "title": "Python 101",
        "price": "19.99",
        "category": "programming",
        "image_url": "https://example.com/book1.jpg"
    }).encode('utf-8')

    response = client.get('/books')
    assert response.status_code == 200
    data = response.get_json()
    assert "data" in data
    assert data["total_books"] == 1


@patch('app.main.redis.Redis', side_effect=Exception("connection error"))
def test_books_redis_failure(mock_redis, client):
    response = client.get('/books')
    assert response.status_code == 500
    assert "Error retrieving books" in response.get_json()["message"]


@patch('app.main.redis.Redis')
def test_books_search_filter(mock_redis, client):
    mock_r = MagicMock()
    mock_redis.return_value = mock_r
    mock_r.keys.return_value = [b'book:1', b'book:2']
    mock_r.get.side_effect = [
        json.dumps({
            "url": "https://example.com/book1",
            "title": "Python for Beginners",
            "price": "15.99",
            "category": "programming",
            "image_url": "https://example.com/book1.jpg"
        }).encode('utf-8'),
        json.dumps({
            "url": "https://example.com/book2",
            "title": "Cooking Tips",
            "price": "20.00",
            "category": "cooking",
            "image_url": "https://example.com/book2.jpg"
        }).encode('utf-8')
    ]

    response = client.get('/books?search=python')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['data']) == 1
    assert data['data'][0]['title'] == "Python for Beginners"


@patch('app.main.redis.Redis')
def test_books_category_filter(mock_redis, client):
    mock_r = MagicMock()
    mock_redis.return_value = mock_r
    mock_r.keys.return_value = [b'book:1']
    mock_r.get.return_value = json.dumps({
        "url": "https://example.com/book1",
        "title": "Python Advanced",
        "price": "25.99",
        "category": "programming",
        "image_url": "https://example.com/book1.jpg"
    }).encode('utf-8')

    response = client.get('/books?category=programming')
    assert response.status_code == 200
    data = response.get_json()
    assert data['total_books'] == 1
    assert data['data'][0]['category'] == "programming"


@patch('app.main.redis.Redis')
def test_books_pagination(mock_redis, client):
    mock_r = MagicMock()
    mock_redis.return_value = mock_r
    # 15 libros falsos
    mock_r.keys.return_value = [f'book:{i}'.encode('utf-8') for i in range(15)]
    mock_r.get.side_effect = [
        json.dumps({
            "url": f"https://example.com/book{i}",
            "title": f"Book {i}",
            "price": "9.99",
            "category": "fiction",
            "image_url": f"https://example.com/book{i}.jpg"
        }).encode('utf-8') for i in range(15)
    ]

    response = client.get('/books?page=2&limit=5')
    assert response.status_code == 200
    data = response.get_json()
    assert data['page'] == 2
    assert len(data['data']) == 5
    assert data['data'][0]['title'] == "Book 5"


@patch('app.main.redis.Redis')
def test_books_malicious_input(mock_redis, client):
    mock_r = MagicMock()
    mock_redis.return_value = mock_r
    mock_r.keys.return_value = [b'book:1']
    mock_r.get.return_value = json.dumps({
        "url": "https://example.com/book1",
        "title": "<script>alert('XSS')</script>",
        "price": "9.99",
        "category": "programming",
        "image_url": "https://example.com/book1.jpg"
    }).encode('utf-8')

    response = client.get('/books?search=<script>')
    assert response.status_code == 200
    data = response.get_json()
    assert data['total_books'] == 1


@patch('app.main.redis.Redis')
def test_books_no_match(mock_redis, client):
    mock_r = MagicMock()
    mock_redis.return_value = mock_r
    mock_r.keys.return_value = [b'book:1']
    mock_r.get.return_value = json.dumps({
        "url": "https://example.com/book1",
        "title": "Python Programming",
        "price": "29.99",
        "category": "programming",
        "image_url": "https://example.com/book1.jpg"
    }).encode('utf-8')

    response = client.get('/books?search=java')
    assert response.status_code == 200
    data = response.get_json()
    assert data['total_books'] == 0
    assert data['data'] == []
