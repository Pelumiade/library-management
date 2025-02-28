# admin_api/tests/conftest.py
import sys
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the admin_api directory to Python path
admin_api_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if admin_api_path not in sys.path:
    sys.path.insert(0, admin_api_path)

# Import and create the test settings
from tests.test_settings import test_settings

# Set environment variables immediately before any imports
os.environ["POSTGRES_SERVER"] = test_settings.POSTGRES_SERVER
os.environ["POSTGRES_USER"] = test_settings.POSTGRES_USER
os.environ["POSTGRES_PASSWORD"] = test_settings.POSTGRES_PASSWORD
os.environ["POSTGRES_DB"] = test_settings.POSTGRES_DB
os.environ["POSTGRES_PORT"] = str(test_settings.POSTGRES_PORT)
os.environ["DATABASE_URL"] = test_settings.DATABASE_URL
os.environ["RABBITMQ_HOST"] = test_settings.RABBITMQ_HOST
os.environ["RABBITMQ_PORT"] = str(test_settings.RABBITMQ_PORT)
os.environ["RABBITMQ_USER"] = test_settings.RABBITMQ_USER
os.environ["RABBITMQ_PASSWORD"] = test_settings.RABBITMQ_PASSWORD
os.environ["PROJECT_NAME"] = test_settings.PROJECT_NAME

# Now we can safely import app modules
from app.models import Base

# Mock RabbitMQ consumer to avoid connecting to actual RabbitMQ during tests
import unittest.mock as mock
with mock.patch('app.consumer.start_consumer'):
    from app.main import app
    
from app.dependencies import get_db
from fastapi.testclient import TestClient

# Test database URL
TEST_DATABASE_URL = "sqlite:///./test.db"

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
def client(engine):
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