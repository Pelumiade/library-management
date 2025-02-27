import pytest
from unittest.mock import patch, MagicMock

from app.consumer import handle_user_created, handle_book_borrowed, handle_book_returned
# from app.crud.user import create
from app.crud.users import user

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
            
            user.create.assert_called_once()

def test_handle_book_borrowed(db_session):
    # Create mock data
    borrow_data = {
        "book_id": 1,
        "user_id": 1,
        "borrow_date": "2025-02-27",
        "due_date": "2025-03-13"
    }
    
    # Mock the book and user retrieval
    mock_book = MagicMock()
    mock_user = MagicMock()
    
    with patch('app.crud.book.get', return_value=mock_book), \
         patch('app.crud.user.get', return_value=mock_user):
        
        # Call the handler
        handle_book_borrowed(borrow_data, db_session)
        
        # Verify book availability was updated
        assert mock_book.is_available == False
        assert db_session.add.called
        assert db_session.commit.called

def test_handle_book_returned(db_session):
    # Create mock data
    return_data = {
        "book_id": 1,
        "is_available": True
    }
    
    # Mock the book retrieval
    mock_book = MagicMock()
    mock_lending = MagicMock()
    
    with patch('app.crud.book.get', return_value=mock_book), \
         patch('app.crud.lending.get_active_lending_by_book', return_value=mock_lending):
        
        # Call the handler
        handle_book_returned(return_data, db_session)
        
        # Verify book availability was updated
        assert mock_book.is_available == True
        assert db_session.add.called
        assert db_session.commit.called