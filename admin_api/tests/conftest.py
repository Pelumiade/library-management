# admin_api/tests/conftest.py
import sys
import os
import pytest
from unittest.mock import patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import get_db
    
# Add admin_api to path so we can import from app
admin_api_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if admin_api_path not in sys.path:
    sys.path.insert(0, admin_api_path)

from app.models import Base
from tests.test_settings import test_settings

# Test database URL
TEST_DATABASE_URL = "sqlite:///./test.db"

# Patch settings before importing app
@pytest.fixture(scope="session", autouse=True)
def patch_settings():
    with patch("app.config.settings", test_settings):
        yield

@pytest.fixture(scope="session")
def engine():
    # Create a test database engine
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(engine):
    # Create a test session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()

@pytest.fixture(scope="module")
def client(patch_settings, engine):
    # Now that settings are patched, we can import the app
    
    # Create testing DB session factory
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Override get_db dependency
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()