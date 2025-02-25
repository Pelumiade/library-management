from typing import List, Optional 
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.dependencies import get_db
from datetime import datetime, timedelta


router = APIRouter()

@router.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.user.get_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.user.create(db=db, obj_in=user)


@router.get("/books/", response_model=List[schemas.Book])
def read_books(
    skip: int = 0, 
    limit: int = 100, 
    publisher: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    books = crud.book.get_all(
        db, 
        skip=skip, 
        limit=limit,
        publisher=publisher,
        category=category
    )
    return books


@router.get("/books/{book_id}", response_model=schemas.Book)
def read_book(book_id: int, db: Session = Depends(get_db)):
    db_book = crud.book.get(db, id=book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book


@router.post("/borrow/", response_model=schemas.Lending)
def borrow_book(
    lending_in: schemas.LendingCreate, 
    db: Session = Depends(get_db)
):
    # Check if book exists and is available
    book = crud.book.get(db, id=lending_in.book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if not book.is_available:
        raise HTTPException(status_code=400, detail="Book is not available for borrowing")
    
    # Check if user exists
    user = crud.user.get(db, id=lending_in.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create lending record
    return crud.lending.borrow_book(
        db=db, 
        user_id=lending_in.user_id, 
        book_id=lending_in.book_id, 
        duration_days=lending_in.duration_days
    )