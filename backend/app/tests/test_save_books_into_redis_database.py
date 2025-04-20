import pytest
from unittest.mock import patch, MagicMock
import redis
import json
import hashlib
from app.redis_storage import save_books_into_redis_database
from dotenv import load_dotenv


# Sample book data for testing
books_data = [
    {"url": "https://books.toscrape.com/catalogue/book/1", "title": "Book 1", "price": "19.99"},
    {"url": "https://books.toscrape.com/catalogue/book/2", "title": "Book 2", "price": "29.99"},
]


# 1. Test Successful Data Storage in Redis
@patch("redis.Redis")
@patch("app.redis_storage.logging.info")
def test_save_books_into_redis_database_success(mock_logging_info, mock_redis):
    # Mock Redis set method
    mock_redis_instance = MagicMock()
    mock_redis.return_value = mock_redis_instance

    # Call the function with sample data
    save_books_into_redis_database(books_data)
    
    # Ensure Redis set is called for each book
    for book in books_data:
        book_id = hashlib.md5(book['url'].encode('utf-8')).hexdigest()
        redis_key = f"book:{book_id}"
        mock_redis_instance.set.assert_any_call(redis_key, json.dumps(book, ensure_ascii=False))

    # Check if the success logging is done
    mock_logging_info.assert_called_once_with(f"Stored {len(books_data)} books into Redis.")


# 2. Test Redis Connection Failure
@patch("redis.Redis", side_effect=redis.ConnectionError("Redis connection failed"))
@patch("app.redis_storage.logging.error")
def test_save_books_into_redis_database_redis_connection_error(mock_logging_error, mock_redis):
    with pytest.raises(redis.ConnectionError):
        save_books_into_redis_database(books_data)

    # Ensure the error is logged
    mock_logging_error.assert_called_once_with("Failed to store data in Redis: Redis connection failed")


# 3. Test Empty Books Data
@patch("redis.Redis")
@patch("app.redis_storage.logging.info")
def test_save_books_into_redis_database_empty_books(mock_logging_info, mock_redis):
    # Call the function with an empty list
    save_books_into_redis_database([])

    # Ensure Redis set is never called
    mock_redis_instance = MagicMock()
    mock_redis_instance.assert_not_called()

    # Check if the success logging is done (no books to store)
    mock_logging_info.assert_called_once_with(f"Stored 0 books into Redis.")


# 4. Test Correct Data Format in Redis
@patch("redis.Redis")
def test_save_books_into_redis_database_data_format(mock_redis):
    # Mock Redis set method
    mock_redis_instance = MagicMock()
    mock_redis.return_value = mock_redis_instance

    # Call the function with sample data
    save_books_into_redis_database(books_data)

    # Ensure the data is stored as a JSON string
    for book in books_data:
        book_id = hashlib.md5(book['url'].encode('utf-8')).hexdigest()
        redis_key = f"book:{book_id}"
        mock_redis_instance.set.assert_any_call(redis_key, json.dumps(book, ensure_ascii=False))


# 5. Test Logging Success
@patch("redis.Redis")
@patch("app.redis_storage.logging.info")
def test_save_books_into_redis_database_logging_success(mock_logging_info, mock_redis):
    # Mock Redis set method
    mock_redis_instance = MagicMock()
    mock_redis.return_value = mock_redis_instance

    # Call the function with sample data
    save_books_into_redis_database(books_data)

    # Ensure logging is called with correct success message
    mock_logging_info.assert_called_once_with(f"Stored {len(books_data)} books into Redis.")


# 6. Test Logging Failure
@patch("redis.Redis", side_effect=redis.ConnectionError("Connection failed"))
@patch("app.redis_storage.logging.error")
def test_save_books_into_redis_database_logging_failure(mock_logging_error, mock_redis):
    with pytest.raises(redis.ConnectionError):
        save_books_into_redis_database(books_data)

    # Ensure error logging is called
    mock_logging_error.assert_called_once_with("Failed to store data in Redis: Connection failed")
