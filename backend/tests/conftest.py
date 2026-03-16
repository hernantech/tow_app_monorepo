import pytest
from app import create_app
from app.database import reset_memory_db
from config import TestConfig


@pytest.fixture
def app():
    reset_memory_db()
    app = create_app(TestConfig)
    yield app
    reset_memory_db()


@pytest.fixture
def client(app):
    return app.test_client()
