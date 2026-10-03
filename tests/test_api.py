import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_api_docs_available():
    response = client.get("/docs")
    assert response.status_code == 200

def test_landing_page():
    response = client.get("/")
    assert response.status_code == 200
    assert "AI-Powered Resume Intelligence" in response.text

def test_auth_login_admin():
    response = client.post("/api/auth/login", json={
        "email": "admin@resumeai.com",
        "password": "admin123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["role"] == "ADMIN"

def test_auth_login_invalid_credentials():
    response = client.post("/api/auth/login", json={
        "email": "admin@resumeai.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401

def test_jobs_listing():
    response = client.get("/api/jobs")
    assert response.status_code == 200
    jobs = response.json()
    assert isinstance(jobs, list)
    assert len(jobs) >= 1

def test_dashboard_analytics_authenticated():
    # Login as admin
    login_resp = client.post("/api/auth/login", json={
        "email": "admin@resumeai.com",
        "password": "admin123"
    })
    token = login_resp.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.get("/api/analytics/dashboard", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "kpi" in data
    assert "charts" in data
    assert "recent_scans" in data
