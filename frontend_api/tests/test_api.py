import pytest
from fastapi.testclient import TestClient

def test_list_available_books(client):
    response = client.get("/books/available/")
    assert response.status_code == 200
    books = response.json()
    
    # All books should have is_available = True
    for book in books:
        assert book["is_available"] == True

def test_get_book_by_id(client):
    # We need to make sure a book exists in our test DB
    # First create via event consumer or directly
    book_data = {
        "title": "Frontend Test Book",
        "author": "Frontend Author",
        "isbn": "FRONTEND456",
        "publisher": "Frontend Publisher",
        "category": "Frontend",
        "publication_year": 2023
    }
    # Simulate book creation (in real test we'd use RabbitMQ event or direct DB access)
    create_response = client.post("/test-helper/create-book/", json=book_data)
    book_id = create_response.json()["id"]
    
    # Test getting the book
    response = client.get(f"/books/{book_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Frontend Test Book"

def test_filter_books_by_publisher(client):
    # Create some test books with different publishers
    test_publishers = ["O'Reilly", "Manning", "Apress"]
    for i, publisher in enumerate(test_publishers):
        book_data = {
            "title": f"Publisher Test Book {i}",
            "author": "Test Author",
            "isbn": f"PUB{i}123",
            "publisher": publisher,
            "category": "Test",
            "publication_year": 2023
        }
        client.post("/test-helper/create-book/", json=book_data)
    
    # Test filtering by publisher
    response = client.get("/books/?publisher=Manning")
    assert response.status_code == 200
    books = response.json()
    
    # All returned books should have publisher = Manning
    for book in books:
        assert book["publisher"] == "Manning"

def test_create_user(client):
    user_data = {
        "email": "frontend_user@test.com",
        "first_name": "Frontend",
        "last_name": "User"
    }
    
    response = client.post("/users/", json=user_data)
    assert response.status_code == 200
    user = response.json()
    assert user["email"] == "frontend_user@test.com"
    
    # Test duplicate email
    duplicate_response = client.post("/users/", json=user_data)
    assert duplicate_response.status_code == 400  # Email already registered

def test_borrow_and_return_flow(client):
    # Create a user
    user_data = {"email": "borrowflow@test.com", "first_name": "Borrow", "last_name": "Flow"}
    user_response = client.post("/users/", json=user_data)
    user_id = user_response.json()["id"]
    
    # Create a book via helper
    book_data = {
        "title": "Borrow Flow Book",
        "author": "Borrow Author",
        "isbn": "BORROWFLOW",
        "publisher": "Test",
        "category": "Test",
        "publication_year": 2023
    }
    book_response = client.post("/test-helper/create-book/", json=book_data)
    book_id = book_response.json()["id"]
    
    # Borrow the book
    borrow_data = {"user_id": user_id, "book_id": book_id, "duration_days": 10}
    borrow_response = client.post("/lending/borrow/", json=borrow_data)
    assert borrow_response.status_code == 200
    lending_id = borrow_response.json()["id"]
    
    # Check book is unavailable
    book_check = client.get(f"/books/{book_id}")
    assert book_check.json()["is_available"] == False
    
    # Return the book
    return_response = client.post(f"/lending/return/{lending_id}")
    assert return_response.status_code == 200
    
    # Check book is available again
    book_check = client.get(f"/books/{book_id}")
    assert book_check.json()["is_available"] == True