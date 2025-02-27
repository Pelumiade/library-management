from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from .base import CRUDBase
from .. import models, schemas


class CRUDBook(CRUDBase[models.Book, schemas.BookCreate, schemas.BookCreate]):
    """
    CRUD operations for Book model
    """
    
    def get_by_isbn(self, db: Session, *, isbn: str) -> Optional[models.Book]:
        """
        Get a book by ISBN.
        """
        return db.query(models.Book).filter(models.Book.isbn == isbn).first()
    
    def get_by_category(
        self, db: Session, *, category: str, skip: int = 0, limit: int = 100
    ) -> List[models.Book]:
        """
        Get books by category.
        """
        return (
            db.query(models.Book)
            .filter(models.Book.category == category)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_publisher(
        self, db: Session, *, publisher: str, skip: int = 0, limit: int = 100
    ) -> List[models.Book]:
        """
        Get books by publisher.
        """
        return (
            db.query(models.Book)
            .filter(models.Book.publisher == publisher)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_available_books(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[models.Book]:
        """
        Get all available books.
        """
        return (
            db.query(models.Book)
            .filter(models.Book.is_available == True)
            .offset(skip)
            .limit(limit)
            .all()
        )
    

    def get_unavailable_books(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[models.Book]:
        """
        Get all unavailable books.
        """
        return (
            db.query(models.Book)
            .filter(models.Book.is_available == False)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def create(self, db: Session, *, obj_in: schemas.BookCreate) -> models.Book:
        """
        Create a new book with availability set to True.
        """
        db_obj = models.Book(
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
    
    def get_categories(self, db: Session) -> List[str]:
        """
        Get a list of all unique categories.
        """
        return [r[0] for r in db.query(models.Book.category).distinct().all()]
    
    def get_publishers(self, db: Session) -> List[str]:
        """
        Get a list of all unique publishers.
        """
        return [r[0] for r in db.query(models.Book.publisher).distinct().all()]


book = CRUDBook(models.Book)