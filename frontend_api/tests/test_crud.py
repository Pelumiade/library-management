import pytest
from datetime import date

from app.crud import books, users, lending
from app.models import Book, User, Lending

def test_create_user(db_session):
    # Test creating a user
    user_data = {
        "email": "test@frontend.com",
        "first_name": "Frontend",
        "last_name": "Test"
    }
    user = users.user.create(db_session, obj_in=user_data)
    
    assert user.email == "test@frontend.com"
    assert user.first_name == "Frontend"
    assert user.is_active == True
    
    # Test getting user by email
    retrieved_user = users.user.get_by_email(db_session, email="test@frontend.com")
    assert retrieved_user is not None
    assert retrieved_user.id == user.id

def test_borrow_book(db_session):
    # Create a user and book first
    user = users.user.create(db_session, obj_in={
        "email": "borrower@frontend.com", 
        "first_name": "Borrower", 
        "last_name": "Frontend"
    })
    
    book = books.book.create(db_session, obj_in={
        "title": "Frontend Book",
        "author": "Frontend Author",
        "isbn": "FRONTEND123",
        "publisher": "Frontend Publisher",
        "category": "Test",
        "publication_year": 2023
    })
    
    # Test borrowing the book
    lending_in = {
        "user_id": user.id,
        "book_id": book.id,
        "duration_days": 14
    }
    
    lending_record = lending.borrow_book(db_session, obj_in=lending_in)
    
    assert lending_record.user_id == user.id
    assert lending_record.book_id == book.id
    assert lending_record.return_date is None
    
    # Check that due date is correctly set
    assert (lending_record.due_date - lending_record.borrow_date).days == 14
    
    # Check that book is marked as unavailable
    db_session.refresh(book)
    assert book.is_available == False

def test_return_book(db_session):
    # Create user, book, and lending
    user = users.user.create(db_session, obj_in={
        "email": "returner@frontend.com", 
        "first_name": "Returner", 
        "last_name": "Frontend"
    })
    
    book = books.book.create(db_session, obj_in={
        "title": "Return Book",
        "author": "Return Author",
        "isbn": "RETURN123",
        "publisher": "Frontend Publisher",
        "category": "Test",
        "publication_year": 2023
    })
    
    # Borrow the book
    lending_in = {"user_id": user.id, "book_id": book.id, "duration_days": 7}
    lending_record = lending.borrow_book(db_session, obj_in=lending_in)
    
    # Test returning the book
    returned = lending.return_book(db_session, lending_id=lending_record.id)
    
    assert returned.return_date is not None
    assert returned.id == lending_record.id
    
    # Check that book is available again
    db_session.refresh(book)
    assert book.is_available == True