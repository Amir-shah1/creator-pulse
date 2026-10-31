import pytest
from fastapi.testclient import TestClient

from app import config
from app.main import app
from app.store import store


@pytest.fixture(autouse=True)
def clean_state(monkeypatch):
    """Fresh store for every test; never call the real Gemini API from tests."""
    monkeypatch.setattr(config, "GEMINI_API_KEY", "")
    monkeypatch.setattr(config, "DEMO_MODE", True)
    store.reset()
    yield
    store.reset()


@pytest.fixture
def client():
    return TestClient(app)
