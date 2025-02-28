import pytest
from fastapi.testclient import TestClient
from app.models import User, Book

def test_list_books(client):
    response = client.get("/admin/books/")
    assert response.status_code == 200

def test_create_book(client, monkeypatch):
    # Mock the publish_event function to avoid RabbitMQ dependency
    monkeypatch.setattr("app.api.admin_books.publish_event", lambda *args, **kwargs: None)
    
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
    create_response = client.post("/admin/books/", json=book_data)
    assert create_response.status_code == 200
    
    book_id = create_response.json()["id"]
    
    # Now remove the book
    delete_response = client.delete(f"/admin/books/{book_id}")
    assert delete_response.status_code == 200


def test_list_users(client):
    response = client.get("/admin/users/")
    assert response.status_code == 200


def test_borrowed_books(client, db_session):

    # Create user directly in DB instead of via API
    user = User(email="borrower@admin.test", first_name="Borrower", last_name="Test")
    db_session.add(user)
    
    # Create a book
    book = Book(
        title="Borrowed Book",
        author="Borrow Author",
        isbn="BORROW123",
        publisher="Test Publisher",
        category="Test",
        publication_year=2023
    )
    db_session.add(book)
    db_session.commit()
    
    # Now test the API endpoint for borrowed books
    response = client.get("/admin/lending/borrowed-books/")
    assert response.status_code == 200
    
    
def test_unavailable_books(client, db_session):
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
    assert book_response.status_code == 200
    book_id = book_response.json()["id"]
    
    # Create a user directly in the database
    user = User(
        email="unavail@admin.test", 
        first_name="Unavail", 
        last_name="Test"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    user_id = user.id
    
    # Check unavailable books
    response = client.get("/admin/lending/unavailable-books/")
    assert response.status_code == 200