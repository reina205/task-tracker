import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.storage.memory import storage


@pytest.fixture(autouse=True)
def reset_storage():
    """Ensure each test starts with empty in-memory storage."""
    storage.reset()
    yield
    storage.reset()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def created_task(client):
    """Create a default task and return its JSON response body."""
    response = client.post(
        "/tasks",
        json={
            "title": "Write tests",
            "description": "Add pytest coverage",
            "priority": "High",
        },
    )
    assert response.status_code == 201
    return response.json()
