from fastapi.testclient import TestClient
from .app import app, index, prediction, get_stream



client = TestClient(app)


def test_index():
    response = client.get("/")
    assert response.status_code == 200
