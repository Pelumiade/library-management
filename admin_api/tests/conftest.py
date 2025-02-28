import sys
import os
import pytest
import unittest.mock as mock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock
from tests.test_settings import test_settings
from app.models import Base
from app.dependencies import get_db
from fastapi.testclient import TestClient

# Add the admin_api directory to Python path
admin_api_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if admin_api_path not in sys.path:
    sys.path.insert(0, admin_api_path)


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


# Mock RabbitMQ consumer to avoid connecting to actual RabbitMQ during tests
with mock.patch('app.consumer.start_consumer'):
    from app.main import app
    

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


@pytest.fixture(autouse=True)
def mock_rabbitmq():
    """Mock all RabbitMQ-related functions."""
    # Create a mock connection with a channel method
    mock_connection = MagicMock()
    mock_channel = MagicMock()
    mock_connection.channel.return_value = mock_channel
    
    with patch('app.publisher.get_connection', return_value=mock_connection), \
         patch('app.consumer.start_consumer', return_value=None):
        yield


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