import pytest
from fastapi.testclient import TestClient
from app.models import Book

def test_list_available_books(client, db_session):
    
    
    # Create available books
    books_data = [
        {
            "title": "Available Book 1",
            "author": "Test Author",
            "isbn": "TEST001",
            "publisher": "Test Publisher",
            "category": "Test",
            "publication_year": 2023,
            "is_available": True
        },
        {
            "title": "Available Book 2",
            "author": "Test Author",
            "isbn": "TEST002",
            "publisher": "Test Publisher",
            "category": "Test",
            "publication_year": 2023,
            "is_available": True
        }
    ]
    
    for book_data in books_data:
        book = Book(**book_data)
        db_session.add(book)
    
    db_session.commit()
    
    # Use an existing endpoint that returns books
    response = client.get("/books/?is_available=true")

    assert response.status_code == 200
    books = response.json()
    
    # Should have at least the books we created
    assert len(books) >= 2
    
    # All books should have is_available = True
    for book in books:
        assert book["is_available"] == True


def test_get_book_by_id(client, db_session):
    # Create a book directly in the database
    from app.models import Book
    test_book = Book(
        title="Frontend Test Book",
        author="Frontend Author",
        isbn="FRONTEND456",
        publisher="Frontend Publisher",
        category="Frontend",
        publication_year=2023,
        is_available=True
    )
    db_session.add(test_book)
    db_session.commit()
    db_session.refresh(test_book)
    
    book_id = test_book.id
    
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
    

def test_borrow_and_return_flow(client, db_session):
    # Create a user
    user_data = {"email": "borrowflow@test.com", "first_name": "Borrow", "last_name": "Flow"}
    user_response = client.post("/users/", json=user_data)
    user_id = user_response.json()["id"]
    
    # Create a book directly in the database
    from app.models import Book
    book = Book(
        title="Borrow Flow Book",
        author="Borrow Author",
        isbn="BORROWFLOW",
        publisher="Test",
        category="Test",
        publication_year=2023,
        is_available=True  # Make sure it's available
    )
    db_session.add(book)
    db_session.commit()
    db_session.refresh(book)
    book_id = book.id
    
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