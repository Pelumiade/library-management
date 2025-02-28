#test_crud.py
import pytest
from datetime import date, timedelta

from app.models import Book, User, Lending
from app.crud import books, users, lending
from app.schemas import BookCreate, UserCreate, LendingCreate

def test_create_book(db_session):
    # Test creating a book
    book_data = {
        "title": "Admin Book Test",
        "author": "Admin Author",
        "isbn": "ADMIN123456",
        "publisher": "Admin Publisher",
        "category": "Admin Test",
        "publication_year": 2023,
        "description": "Admin test book"
    }
    # Convert dict to Pydantic model
    book_in = BookCreate(**book_data)
    book = books.book.create(db_session, obj_in=book_in)
    
    assert book.title == book_data["title"]
    assert book.isbn == book_data["isbn"]

def test_update_book(db_session):
    # Create book first
    book_data = {
        "title": "Original Title",
        "author": "Original Author",
        "isbn": "UPDATE123",
        "publisher": "Test",
        "category": "Test",
        "publication_year": 2023
    }
    # Convert dict to Pydantic model
    book_in = BookCreate(**book_data)
    book = books.book.create(db_session, obj_in=book_in)
    
    # Update the book
    updated_data = {"title": "Updated Title", "author": "Updated Author"}
    updated_book = books.book.update(db_session, db_obj=book, obj_in=updated_data)
    
    assert updated_book.title == "Updated Title"
    assert updated_book.author == "Updated Author"
    assert updated_book.isbn == "UPDATE123"  # Unchanged field


def test_handle_book_borrowed(db_session):
    # Create a real Book and User instance for testing
    
    # Add real (but test) instances to the DB
    test_book = Book(
        title="Test Book",
        author="Test Author",
        isbn="TEST123",
        publisher="Test Publisher",
        category="Test",
        publication_year=2023,
        is_available=True
    )
    test_user = User(
        email="test@example.com",
        first_name="Test",
        last_name="User",
        is_active=True
    )
    db_session.add_all([test_book, test_user])
    db_session.commit()
    
    # Create test data with Python date objects (not strings)
    borrow_data = {
        "book_id": test_book.id,
        "user_id": test_user.id,
        "borrow_date": date(2025, 2, 27),
        "due_date": date(2025, 3, 13)
    }
    
    # Call the handler
    from app.consumer import handle_book_borrowed
    handle_book_borrowed(borrow_data, db_session)
    
    # Verify the book is now unavailable
    db_session.refresh(test_book)
    assert test_book.is_available is False