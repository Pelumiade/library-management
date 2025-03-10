import pytest
from unittest.mock import patch, MagicMock
from datetime import date, timedelta
from app.models import Book, User
from app.crud import lending
from app.models import Book, User, Lending
from app.consumer import handle_book_returned

from app.consumer import handle_user_created


def test_handle_user_created(db_session):
    # Create mock user data
    user_data = {
        "email": "consumer_test@admin.com",
        "first_name": "Consumer",
        "last_name": "Test"
    }
     
    # Mock the get_by_email method to return None (user doesn't exist)
    with patch('app.crud.user.get_by_email', return_value=None):
        # Mock the create method
        mock_user = MagicMock()
        with patch('app.crud.user.create', return_value=mock_user):
            # Call the handler
            handle_user_created(user_data, db_session)
                     
            # Verify create was called with the correct data
            from app.crud import user
            user.create.assert_called_once()


def test_handle_book_returned(db_session):
    
    # Create book, user, and lending
    test_book = Book(
        title="Return Test Book",
        author="Return Test Author",
        isbn="RETURN123",
        publisher="Test Publisher",
        category="Test",
        publication_year=2023,
        is_available=False  # Book is borrowed
    )
    
    test_user = User(
        email="returner@example.com",
        first_name="Return",
        last_name="Test",
        is_active=True
    )
    
    db_session.add_all([test_book, test_user])
    db_session.commit()
    
    # Create lending
    test_lending = Lending(
        user_id=test_user.id,
        book_id=test_book.id,
        borrow_date=date.today() - timedelta(days=10),
        due_date=date.today() + timedelta(days=4),
        return_date=None
    )
    
    db_session.add(test_lending)
    db_session.commit()
    
    # Test data
    return_data = {
        "book_id": test_book.id,
        "is_available": True
    }
    
    # Call the handler
    handle_book_returned(return_data, db_session)
    
    # Verify book is now available
    db_session.refresh(test_book)
    assert test_book.is_available is True