from datetime import date, datetime, timedelta
from typing import List, Optional, Dict, Any

from sqlalchemy import and_
from sqlalchemy.orm import Session

from ..models import Lending, Book, User
from ..schemas import BookCreate, BookUpdate


# Book operations
class BookCRUD:
    def get(self, db: Session, id: int) -> Optional[Book]:
        return db.query(Book).filter(Book.id == id).first()

    def get_by_isbn(self, db: Session, isbn: str) -> Optional[Book]:
        return db.query(Book).filter(Book.isbn == isbn).first()

    def get_all(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        publisher: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[Book]:
        query = db.query(Book).filter(Book.is_available == True)
        
        if publisher:
            query = query.filter(Book.publisher == publisher)
        if category:
            query = query.filter(Book.category == category)
        
        return query.offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: BookCreate) -> Book:
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
        update_data = obj_in.dict(exclude_unset=True)
        for field in update_data:
            setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> Book:
        obj = db.query(Book).get(id)
        db.delete(obj)
        db.commit()
        return obj

book = BookCRUD()