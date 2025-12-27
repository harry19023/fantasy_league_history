from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_get_leagues_empty():
    """Test getting leagues when none exist."""
    response = client.get("/leagues")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_franchises_empty():
    """Test getting franchises when none exist."""
    response = client.get("/leagues/1/franchises")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_seasons_empty():
    """Test getting seasons when none exist."""
    response = client.get("/leagues/1/seasons")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
