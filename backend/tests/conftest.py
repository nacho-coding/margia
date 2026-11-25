import pytest
from fastapi.testclient import TestClient

from app.datos.generador import generar
from app.main import app
from app.persistencia.db import SessionLocal


@pytest.fixture(scope="session")
def mundo():
    return generar()


@pytest.fixture(scope="session")
def client():
    return TestClient(app)


@pytest.fixture
def db():
    with SessionLocal() as session:
        yield session
