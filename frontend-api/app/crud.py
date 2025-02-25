from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.schemas import BookCreate, BookUpdate, UserCreate, UserUpdate

from datetime import date, datetime, timedelta

from app.models import Lending, Book, User


def get(db: Session, id: int) -> Optional[Book]:
    return db.query(Book).filter(Book.id == id).first()

def get_by_isbn(db: Session, isbn: str) -> Optional[Book]:
    return db.query(Book).filter(Book.isbn == isbn).first()

def get_all(
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


def create(db: Session, *, obj_in: BookCreate) -> Book:
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


def update(db: Session, *, db_obj: Book, obj_in: BookUpdate) -> Book:
    update_data = obj_in.dict(exclude_unset=True)
    for field in update_data:
        setattr(db_obj, field, update_data[field])
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def remove(db: Session, *, id: int) -> Book:
    obj = db.query(Book).get(id)
    db.delete(obj)
    db.commit()
    return obj


def get(db: Session, id: int) -> Optional[User]:
    return db.query(User).filter(User.id == id).first()

def get_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def get_multi(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()

def create(db: Session, *, obj_in: UserCreate) -> User:
    db_obj = User(
        email=obj_in.email,
        first_name=obj_in.first_name,
        last_name=obj_in.last_name,
        is_active=True
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(db: Session, *, db_obj: User, obj_in: UserUpdate) -> User:
    update_data = obj_in.dict(exclude_unset=True)
    for field in update_data:
        setattr(db_obj, field, update_data[field])
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def remove(db: Session, *, id: int) -> User:
    obj = db.query(User).get(id)
    db.delete(obj)
    db.commit()
    return obj


def borrow_book(db: Session, user_id: int, book_id: int, duration_days: int) -> Lending:
    # Check if book is available
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book or not book.is_available:
        raise ValueError("Book is not available for borrowing")
    
    # Create lending record
    borrow_date = date.today()
    due_date = borrow_date + timedelta(days=duration_days)
    
    db_obj = Lending(
        user_id=user_id,
        book_id=book_id,
        borrow_date=borrow_date,
        due_date=due_date,
        return_date=None
    )
    
    # Mark book as unavailable
    book.is_available = False
    
    db.add(db_obj)
    db.add(book)
    db.commit()
    db.refresh(db_obj)
    
    return db_obj

def return_book(db: Session, lending_id: int) -> Lending:
    lending = db.query(Lending).filter(Lending.id == lending_id).first()
    if not lending:
        raise ValueError("Lending record not found")
    
    # Mark book as available again
    book = db.query(Book).filter(Book.id == lending.book_id).first()
    book.is_available = True
    
    # Update lending record
    lending.return_date = date.today()
    
    db.add(lending)
    db.add(book)
    db.commit()
    db.refresh(lending)
    
    return lending

def get_active_lendings(db: Session, skip: int = 0, limit: int = 100) -> List[Lending]:
    return db.query(Lending)\
        .filter(Lending.return_date == None)\
        .offset(skip).limit(limit).all()

def get_user_lendings(db: Session, user_id: int) -> List[Lending]:
    return db.query(Lending)\
        .filter(Lending.user_id == user_id)\
        .all()

def get_unavailable_books(db: Session) -> List[dict]:
    results = db.query(Book, Lending)\
        .join(Lending, Book.id == Lending.book_id)\
        .filter(Book.is_available == False, Lending.return_date == None)\
        .all()
    
    return [{
        "book": book,
        "due_date": lending.due_date
    } for book, lending in results]