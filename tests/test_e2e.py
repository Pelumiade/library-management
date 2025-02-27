import pytest
import requests
import time

def test_admin_to_frontend_sync(admin_client, frontend_client):
    """Test that a book created in admin API appears in frontend API"""
    
    # Create a book in admin API
    book_data = {
        "title": "E2E Test Book",
        "author": "E2E Author",
        "isbn": "E2E12345",
        "publisher": "E2E Publisher",
        "category": "E2E Test",
        "publication_year": 2023,
        "description": "Book for E2E testing"
    }
    
    admin_response = requests.post(f"{admin_client}/books/", json=book_data)
    assert admin_response.status_code == 200
    book_id = admin_response.json()["id"]
    
    # Wait for event to be processed
    time.sleep(2)
    
    # Check if book appears in frontend API
    max_retries = 5
    for i in range(max_retries):
        frontend_response = requests.get(f"{frontend_client}/books/{book_id}")
        if frontend_response.status_code == 200:
            frontend_book = frontend_response.json()
            assert frontend_book["title"] == "E2E Test Book"
            assert frontend_book["isbn"] == "E2E12345"
            break
        else:
            if i == max_retries - 1:
                pytest.fail("Book didn't sync from admin to frontend")
            time.sleep(2)

def test_frontend_to_admin_sync(admin_client, frontend_client):
    """Test that a book borrowed in frontend API becomes unavailable in admin API"""
    
    # Create user in frontend API
    user_data = {"email": "e2e@test.com", "first_name": "E2E", "last_name": "Test"}
    user_response = requests.post(f"{frontend_client}/users/", json=user_data)
    assert user_response.status_code == 200
    user_id = user_response.json()["id"]
    
    # Create book (via admin API)
    book_data = {
        "title": "Borrow E2E Book",
        "author": "Borrow E2E Author",
        "isbn": "BORROW_E2E",
        "publisher": "E2E Publisher",
        "category": "E2E Test",
        "publication_year": 2023
    }
    book_response = requests.post(f"{admin_client}/books/", json=book_data)
    assert book_response.status_code == 200
    book_id = book_response.json()["id"]
    
    # Wait for book to sync to frontend
    time.sleep(2)
    
    # Borrow book in frontend API
    borrow_data = {"user_id": user_id, "book_id": book_id, "duration_days": 7}
    borrow_response = requests.post(f"{frontend_client}/lending/borrow/", json=borrow_data)
    assert borrow_response.status_code == 200
    
    # Wait for event to be processed
    time.sleep(2)
    
    # Check if book is unavailable in admin API
    max_retries = 5
    for i in range(max_retries):
        admin_book_response = requests.get(f"{admin_client}/books/{book_id}")
        if admin_book_response.status_code == 200:
            admin_book = admin_book_response.json()
            if admin_book["is_available"] == False:
                break
        if i == max_retries - 1:
            pytest.fail("Book availability didn't sync from frontend to admin")
        time.sleep(2)
    
    # Check if book appears in unavailable books list in admin API
    unavailable_response = requests.get(f"{admin_client}/unavailable-books/")
    assert unavailable_response.status_code == 200
    unavailable_books = unavailable_response.json()
    assert any(book["id"] == book_id for book in unavailable_books)