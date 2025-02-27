import pytest
from fastapi.testclient import TestClient

def test_list_books(client):
    response = client.get("/books/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_book(client):
    book_data = {
        "title": "API Test Book",
        "author": "API Author",
        "isbn": "APITEST123",
        "publisher": "API Publisher",
        "category": "API Test",
        "publication_year": 2023,
        "description": "Book created via API test"
    }
    
    response = client.post("/books/", json=book_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "API Test Book"
    assert data["is_available"] == True
    
    # Test get book by ID
    book_id = data["id"]
    get_response = client.get(f"/books/{book_id}")
    assert get_response.status_code == 200
    assert get_response.json()["title"] == "API Test Book"

def test_remove_book(client):
    # First create a book
    book_data = {
        "title": "Book to Remove",
        "author": "Remove Author",
        "isbn": "REMOVE123",
        "publisher": "Test Publisher",
        "category": "Test",
        "publication_year": 2023
    }
    create_response = client.post("/books/", json=book_data)
    assert create_response.status_code == 200
    book_id = create_response.json()["id"]
    
    # Now delete it
    delete_response = client.delete(f"/books/{book_id}")
    assert delete_response.status_code == 200
    
    # Verify it's gone
    get_response = client.get(f"/books/{book_id}")
    assert get_response.status_code == 404

def test_list_users(client):
    response = client.get("/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_borrowed_books(client):
    # First create test data: user, book, and lending
    user_data = {"email": "borrower@admin.test", "first_name": "Borrower", "last_name": "Test"}
    user_response = client.post("/users/", json=user_data)
    assert user_response.status_code == 200
    user_id = user_response.json()["id"]
    
    book_data = {
        "title": "Borrowed Book Test",
        "author": "Borrow Author",
        "isbn": "BORROW123",
        "publisher": "Test Publisher",
        "category": "Test",
        "publication_year": 2023
    }
    book_response = client.post("/books/", json=book_data)
    assert book_response.status_code == 200
    book_id = book_response.json()["id"]
    
    # Create lending
    lending_data = {"user_id": user_id, "book_id": book_id, "duration_days": 14}
    lending_response = client.post("/lendings/", json=lending_data)
    assert lending_response.status_code == 200
    
    # Test borrowed books endpoint
    borrowed_response = client.get("/borrowed-books/")
    assert borrowed_response.status_code == 200
    
    # Check if our borrowed book is in the response
    borrowed_books = borrowed_response.json()
    assert any(lending["book_id"] == book_id and lending["user_id"] == user_id for lending in borrowed_books)

def test_unavailable_books(client):
    # Create and borrow a book first
    book_data = {
        "title": "Unavailable Book Test",
        "author": "Unavailable Author",
        "isbn": "UNAVAIL123",
        "publisher": "Test Publisher",
        "category": "Test",
        "publication_year": 2023
    }
    book_response = client.post("/books/", json=book_data)
    book_id = book_response.json()["id"]
    
    user_data = {"email": "unavail@admin.test", "first_name": "Unavail", "last_name": "Test"}
    user_response = client.post("/users/", json=user_data)
    user_id = user_response.json()["id"]
    
    # Create lending
    lending_data = {"user_id": user_id, "book_id": book_id, "duration_days": 7}
    client.post("/lendings/", json=lending_data)
    
    # Test unavailable books endpoint
    unavailable_response = client.get("/unavailable-books/")
    assert unavailable_response.status_code == 200
    
    # Check if our book is in the unavailable list
    unavailable_books = unavailable_response.json()
    assert any(book["id"] == book_id for book in unavailable_books)