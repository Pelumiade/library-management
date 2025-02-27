from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..crud import books
from .. import schemas
from ..dependencies import get_db
from ..publisher import publish_event

router = APIRouter()

#Create a new book
@router.post("/", response_model=schemas.Book)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    """
    Add a new book to the library catalog.
    """
    db_book = books.book.create(db=db, obj_in=book)
    
     # Convert SQLAlchemy object to dictionary
    book_data = {column.name: getattr(db_book, column.name) for column in db_book.__table__.columns}

    # Publish message to notify frontend service
    publish_event("book_created", book_data)

    return db_book


#Fetch all books
@router.get("/", response_model=List[schemas.Book])
def read_books(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve all books in the catalog.
    """
    book_list = books.book.get_multi(db, skip=skip, limit=limit)
    return book_list


#Fetch all available books
@router.get("/available/", response_model=List[schemas.Book])
def read_available_books(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve all books that are currently available for borrowing.
    """
    return books.book.get_available_books(db, skip=skip, limit=limit)


#Fetch all unavailable books
@router.get("/unavailable/", response_model=List[schemas.Book])
def read_unavailable_books(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve all books that are currently unavailable (checked out).
    """
    return books.book.get_unavailable_books(db, skip=skip, limit=limit)


#Get a specific book by ID
@router.get("/{book_id}", response_model=schemas.Book)
def read_book(book_id: int, db: Session = Depends(get_db)):
    """
    Get a specific book by ID.
    """
    db_book = books.book.get(db, id=book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book


#Update book information
@router.put("/{book_id}", response_model=schemas.Book)
def update_book(
    book_id: int, book_data: schemas.BookCreate, db: Session = Depends(get_db)
):
    """
    Update a book's information.
    """
    db_book = books.book.get(db, id=book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    
    updated_book = books.book.update(db=db, db_obj=db_book, obj_in=book_data)
    
    # Convert SQLAlchemy object to dictionary
    book_data = {column.name: getattr(updated_book, column.name) for column in updated_book.__table__.columns}

    # Publish message to notify frontend service
    publish_event("book_updated", book_data)

    return updated_book  


#Delete a book
@router.delete("/{book_id}", response_model=schemas.Book)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    """
    Remove a book from the library catalog.
    """
    # Check if book exists
    db_book = books.book.get(db, id=book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # Remove book from the database
    db_book = books.book.remove(db=db, id=book_id)
    
    # Publish message to notify frontend service
    publish_event("book_deleted", {"id": book_id})
    
    return db_book
