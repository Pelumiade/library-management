import pytest
import logging

from unittest.mock import patch, MagicMock

from app.consumer import handle_book_created, handle_book_updated, handle_book_deleted

from app.crud.books import book
from app.models import Book


# Create a logger for this module
logger = logging.getLogger(__name__)


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
    #Create a real book in the database
    real_book = Book(
        title="Original Title",
        author="Original Author",
        isbn="UPDATE123",
        publisher="Test Publisher",
        category="Test",
        publication_year=2023
    )
    db_session.add(real_book)
    db_session.flush()  # This assigns an ID without committing
    
    # Store the ID for our test
    book_id = real_book.id
    
    # Create the book data for updating
    book_data = {
        "id": book_id,
        "title": "Updated Book",
        "author": "Updated Author",
        "isbn": "UPDATE123"
    }
    
    # Call the handler - this will update the book
    handle_book_updated(book_data, db_session)
    
    # Refresh our reference to get the latest data
    db_session.refresh(real_book)
    
    # Verify book attributes were updated
    assert real_book.title == "Updated Book"
    assert real_book.author == "Updated Author"
    assert real_book.isbn == "UPDATE123"
    

def handle_book_deleted(data, db):
    """Handle a book_deleted event from the admin API"""
    logger.info(f"Processing book_deleted event: {data}")
    book_id = data.get("id")
    if not book_id:
        logger.error("Book ID missing in book_deleted event")
        return

    # Get the book
    book_obj = book.get(db, id=book_id)
    if not book_obj:
        logger.error(f"Book with ID {book_id} not found for deletion")
        return  
    
    # Delete the book
    db.delete(book_obj)
    db.commit()