import pytest
from app.main import app 

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_hello_world(client):
    response = client.get('/')
    assert response.status_code == 200
    data = response.get_json()
    assert "mensaje" in data
    assert "routes" in data