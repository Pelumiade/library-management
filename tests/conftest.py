import pytest
import time
import requests
from fastapi.testclient import TestClient

@pytest.fixture(scope="module")
def admin_client():
    # Could use TestClient or real HTTP client to actual running service
    # This example uses requests to an actual running service
    base_url = "http://localhost:8000"  # Admin API URL
    
    # Wait for service to be ready
    max_retries = 5
    for i in range(max_retries):
        try:
            response = requests.get(f"{base_url}/health")
            if response.status_code == 200:
                break
        except requests.exceptions.ConnectionError:
            if i == max_retries - 1:
                pytest.fail("Admin API is not available")
            time.sleep(2)
    
    return base_url

@pytest.fixture(scope="module")
def frontend_client():
    # Could use TestClient or real HTTP client to actual running service
    base_url = "http://localhost:8001"  # Frontend API URL
    
    # Wait for service to be ready
    max_retries = 5
    for i in range(max_retries):
        try:
            response = requests.get(f"{base_url}/health")
            if response.status_code == 200:
                break
        except requests.exceptions.ConnectionError:
            if i == max_retries - 1:
                pytest.fail("Frontend API is not available")
            time.sleep(2)
    
    return base_url