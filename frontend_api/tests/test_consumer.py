import pytest
from unittest.mock import patch, MagicMock

from app.consumer import handle_book_created, handle_book_updated, handle_book_deleted

from app.crud.books import book
def test_handle_book_created(db_session):
    # Create a mock book data
    book_data = {
        "title": "Event Book",
        "author": "Event Author",
        "isbn": "EVENT123",
        "publisher": "Event Publisher",
        "category": "Event",
        "publication_year": 2023,
        "description": "Book created via event"
    }
    
    # Mock the get_by_isbn method to return None (book doesn't exist)
    with patch('app.crud.books.book.get_by_isbn', return_value=None):
        # Mock the create method to return a mock book
        mock_book = MagicMock()
        with patch('app.crud.books.book.create', return_value=mock_book):
            # Call the handler
            handle_book_created(book_data, db_session)
            
            # Verify create was called with the correct data
            
            book.create.assert_called_once()

def test_handle_book_updated(db_session):
    # Mock book data
    book_data = {
        "id": 1,
        "title": "Updated Book",
        "author": "Updated Author",
        "isbn": "UPDATE123"
    }
    
    # Mock the get method to return a mock book
    mock_book = MagicMock()
    with patch('app.crud.books.book.get', return_value=mock_book):
        # Call the handler
        handle_book_updated(book_data, db_session)
        
        # Verify book attributes were updated
        assert mock_book.title == "Updated Book"
        assert mock_book.author == "Updated Author"
        assert mock_book.isbn == "UPDATE123"
        assert db_session.add.called
        assert db_session.commit.called

def test_handle_book_deleted(db_session):
    # Mock book data
    book_data = {"id": 1}
    
    # Mock the get method to return a mock book
    mock_book = MagicMock()
    with patch('app.crud.books.book.get', return_value=mock_book):
        # Call the handler
        handle_book_deleted(book_data, db_session)
        
        # Verify the book was deleted
        assert db_session.delete.called
        assert db_session.commit.called