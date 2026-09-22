import asyncio
from fastapi.testclient import TestClient
from app.main import app

def test_health_sync():
    client = TestClient(app)
    response = client.get("/health")
    print(f"Health check status code: {response.status_code}")
    print(f"Health check response body: {response.json()}")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "connected"}
    print("FastAPI /health check verified successfully via TestClient!")

if __name__ == "__main__":
    test_health_sync()
