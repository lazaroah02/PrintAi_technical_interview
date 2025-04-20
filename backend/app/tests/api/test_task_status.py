import pytest
from unittest.mock import patch, MagicMock
from app.main import app 

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

@patch('app.tasks.celery.AsyncResult')
def test_task_status(mock_async_result, client):
    mock_result = MagicMock()
    mock_result.id = "abc123"
    mock_result.status = "SUCCESS"
    mock_result.result = {"done": True}
    mock_async_result.return_value = mock_result

    response = client.get('/status/abc123')
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "SUCCESS"
    assert data["result"] == {"done": True}


