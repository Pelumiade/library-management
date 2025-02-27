import pytest
from datetime import date, timedelta

from app.models import Book, User, Lending
from app.crud import books, users, lending

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
    book = books.book.create(db_session, obj_in=book_data)
    
    assert book.title == "Admin Book Test"
    assert book.is_available == True
    
    # Test retrieving the book
    retrieved_book = books.book.get(db_session, id=book.id)
    assert retrieved_book is not None
    assert retrieved_book.id == book.id

def test_update_book(db_session):
    # Create book first
    book = books.book.create(db_session, obj_in={
        "title": "Original Title",
        "author": "Original Author",
        "isbn": "UPDATE123",
        "publisher": "Test",
        "category": "Test",
        "publication_year": 2023
    })
    
    # Update the book
    updated_data = {"title": "Updated Title", "author": "Updated Author"}
    updated_book = books.book.update(db_session, db_obj=book, obj_in=updated_data)
    
    assert updated_book.title == "Updated Title"
    assert updated_book.author == "Updated Author"
    assert updated_book.isbn == "UPDATE123"  # Unchanged field

def test_delete_book(db_session):
    # Create book first
    book = books.book.create(db_session, obj_in={
        "title": "Book to Delete",
        "author": "Delete Author",
        "isbn": "DELETE123",
        "publisher": "Test",
        "category": "Test",
        "publication_year": 2023
    })
    
    # Get book ID
    book_id = book.id
    
    # Delete the book
    deleted_book = books.book.remove(db_session, id=book_id)
    
    assert deleted_book.id == book_id
    
    # Verify book no longer exists
    retrieved_book = books.book.get(db_session, id=book_id)
    assert retrieved_book is None