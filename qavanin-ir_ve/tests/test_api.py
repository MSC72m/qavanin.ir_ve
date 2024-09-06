import pytest
import requests

@pytest.fixture
def base_url():
    """Fixture that returns the base URL of the FastAPI application."""
    return "http://localhost:8000"

def test_get_closest_match(base_url):
    """Test that the /get_closest_match endpoint can return the closest matching documents for a given input text."""
    response = requests.post(f"{base_url}/api/get_closest_match", json={"text": "Test input"}, params={"limit": 2})
    assert response.status_code == 200
    data = response.json()
    assert "closest_documents" in data
    assert "total_documents" in data

def test_update_document(base_url):
    """Test that the /update_document/{document_id} endpoint can update the content of a specific document."""
    response = requests.put(f"{base_url}/api/update_document/1", json={"text": "Test input"})
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Document updated successfully"
    assert "document" in data

def test_delete_document(base_url):
    """Test that the /delete_document/{document_id} endpoint can delete a specific document."""
    response = requests.delete(f"{base_url}/api/delete_document/1")
    assert response.status_code == 204

def test_get_document_by_id(base_url):
    """Test that the /get_document/{document_id} endpoint can retrieve a specific document by its ID."""
    response = requests.get(f"{base_url}/api/get_document/1")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Document retrieved successfully"
    assert "id" in data
    assert "content" in data
