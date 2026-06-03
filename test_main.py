from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_classify():
    response = client.post("/classify", json={"text": "This is a test"})
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "text" in data
    assert "label" in data

def test_get_results():
    post_response = client.post("/classify", json={"text": "Test text"})
    record_id = post_response.json()["id"]
    
    get_response = client.get(f"/results/{record_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == record_id
    assert data["status"] == "complete"

def test_get_results_not_found():
    response = client.get("/results/99999")
    assert response.status_code == 404