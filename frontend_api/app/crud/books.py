from datetime import date, datetime, timedelta
from typing import List, Optional, Dict, Any

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from ..models import Lending, Book, User
from ..schemas import BookCreate, BookUpdate


# Book operations
class BookCRUD:
    def get(self, db: Session, id: int) -> Optional[Book]:
        """
        Get a book by its ID using select statement.
        """
        statement = select(Book).where(Book.id == id)
        return db.execute(statement).scalar_one_or_none()

    def get_by_isbn(self, db: Session, isbn: str) -> Optional[Book]:
        """
        Get a book by ISBN using select statement.
        """
        statement = select(Book).where(Book.isbn == isbn)
        return db.execute(statement).scalar_one_or_none()

    def get_all(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        publisher: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[Book]:
        """
        Get all available books with optional filtering.
        """
        # Start with base query for available books
        statement = select(Book).where(Book.is_available == True)
        
        # Add optional filters
        if publisher:
            statement = statement.where(Book.publisher == publisher)
        if category:
            statement = statement.where(Book.category == category)
        
        # Add pagination
        statement = statement.offset(skip).limit(limit)
        
        # Execute and return results
        return list(db.execute(statement).scalars().all())

    def create(self, db: Session, *, obj_in: BookCreate) -> Book:
        """
        Create a new book.
        """
        db_obj = Book(
            title=obj_in.title,
            author=obj_in.author,
            isbn=obj_in.isbn,
            publisher=obj_in.publisher,
            category=obj_in.category,
            publication_year=obj_in.publication_year,
            description=obj_in.description,
            is_available=True
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: Book, obj_in: BookUpdate) -> Book:
        """
        Update an existing book.
        """
        # Use model_dump for Pydantic V2 compatibility
        update_data = obj_in.model_dump(exclude_unset=True)
        for field in update_data:
            setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> Book:
        """
        Remove a book by its ID.
        """
        # Use db.get() instead of query().get()
        obj = db.get(Book, id)
        if obj is None:
            raise ValueError(f"Book with id {id} not found")
        db.delete(obj)
        db.commit()
        return obj


book = BookCRUD()