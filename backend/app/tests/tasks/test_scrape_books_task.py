from app.tasks import scrape_books_task
from unittest.mock import patch

@patch("app.tasks.scrape_books")
def test_scrape_books_task_success(mock_scrape_books):
    result = scrape_books_task()
    assert result == "Task Finished. Access to the books on /books"
    mock_scrape_books.assert_called_once()

@patch("app.tasks.scrape_books", side_effect=Exception("boom"))
def test_scrape_books_task_failure(mock_scrape_books):
    result = scrape_books_task()
    assert result == "Error in the task"
