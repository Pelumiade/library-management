from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..crud import books, lending
from ..crud.users import user as users
from .. import schemas
from ..dependencies import get_db
from ..publisher import publish_event


router = APIRouter()

#User borrowed books
@router.get("/borrowed-books/", response_model=List[schemas.LendingWithUserAndBook])
def read_borrowed_books(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Fetch/List users and the books they have borrowed.
    """
    return lending.get_active_lendings(db, skip=skip, limit=limit)


#Unavailable books
@router.get("/unavailable-books/", response_model=List[schemas.BookWithDueDate])
def read_unavailable_books(db: Session = Depends(get_db)):
    """
    Fetch/List books that are not available for borrowing (showing when they will be available).
    """
    return lending.get_unavailable_books(db)


#Borrowed books by user
@router.get("/user-borrowings/{user_id}", response_model=List[schemas.LendingWithBook])
def read_user_borrowings(user_id: int, db: Session = Depends(get_db)):
    """
    Get all books borrowed by a specific user.
    """
    # Check if user exists
    user_record = users.get(db, id=user_id)
    if not user_record:
        raise HTTPException(status_code=404, detail="User not found")
    
    return lending.get_user_lendings(db, user_id=user_id)  


#Process a book return
@router.post("/return-book/{lending_id}", response_model=schemas.Lending)
def return_book(lending_id: int, db: Session = Depends(get_db)):
    """
    Process a book return.
    """

    # Check if lending exists
    lending_record = lending.get(db, id=lending_id)
    if not lending_record:
        raise HTTPException(status_code=404, detail="Lending record not found")
    
    # Check if book is already returned
    if lending_record.return_date is not None:
        raise HTTPException(status_code=400, detail="This book has already been returned")
    
    updated_lending = lending.mark_as_returned(db, lending_id=lending_id)
    
    # Publish message to notify frontend service
    publish_event("book_returned", {
    "book_id": lending_record.book_id,
    "is_available": True
    })
    
    return updated_lending


#Get all overdue books
@router.get("/overdue-books/", response_model=List[schemas.LendingWithUserAndBook])
def read_overdue_books(db: Session = Depends(get_db)):
    """
    Get all books that are overdue.
    """
    return lending.get_overdue_lendings(db)