from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.dependencies import get_db
from app.publisher import publish_event

from datetime import date

from app import crud, models, schemas

router = APIRouter()

@router.post("/books/", response_model=schemas.Book)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    # Create book in the database
    db_book = crud.book.create(db=db, obj_in=book)
    
    # Publish message to notify frontend service
    publish_event("book_created", db_book.dict())
    
    return db_book

@router.delete("/books/{book_id}", response_model=schemas.Book)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    # Check if book exists
    db_book = crud.book.get(db, id=book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # Remove book from the database
    db_book = crud.book.remove(db=db, id=book_id)
    
    # Publish message to notify frontend service
    publish_event("book_deleted", {"id": book_id})
    
    return db_book


@router.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.user.get_multi(db, skip=skip, limit=limit)
    return users


@router.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.user.get(db, id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.get("/borrowed-books/", response_model=List[schemas.LendingWithUserAndBook])
def read_borrowed_books(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.lending.get_active_lendings(db, skip=skip, limit=limit)


@router.get("/unavailable-books/", response_model=List[schemas.BookWithDueDate])
def read_unavailable_books(db: Session = Depends(get_db)):
    return crud.lending.get_unavailable_books(db)


@router.get("/user-borrowings/{user_id}", response_model=List[schemas.LendingWithBook])
def read_user_borrowings(user_id: int, db: Session = Depends(get_db)):
    # Check if user exists
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return crud.lending.get_user_lendings(db, user_id=user_id)

