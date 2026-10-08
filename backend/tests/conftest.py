import os

# Must be set BEFORE the app is imported
os.environ["DATABASE_URL"] = "sqlite:///./test_uptimewatch.db"
os.environ["SCHEDULER_ENABLED"] = "0"
os.environ["ALLOW_PRIVATE_URLS"] = "1"

import pytest
from fastapi.testclient import TestClient

from app import checker
from app.config import settings
from app.database import Base, engine
from app.main import app


@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def auth_headers(client):
    r = client.post("/api/auth/register", json={"email": "a@example.com", "password": "password123"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture()
def fake_fetch(monkeypatch):
    """Replace the real HTTP request so tests never touch the network."""
    state = {"result": (200, 25, None)}
    monkeypatch.setattr(checker, "fetch", lambda url: state["result"])
    monkeypatch.setattr(settings, "failure_threshold", 2)
    return state
