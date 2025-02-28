from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select

from .. import models, schemas
from ..crud import books, users, lending
from ..dependencies import get_db
from ..publisher import publish_event

router = APIRouter()


@router.post("/borrow/", response_model=schemas.Lending)
def borrow_book(
    lending_in: schemas.LendingCreate,
    db: Session = Depends(get_db)
):
    """
    Borrow a book for a specific user.
    """
    # Check if book exists and is available
    book_stmt = select(models.Book).where(models.Book.id == lending_in.book_id)
    book = db.execute(book_stmt).scalar_one_or_none()
    
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if not book.is_available:
        raise HTTPException(status_code=400, detail="Book is not available for borrowing")
        
    # Check if user exists
    user_stmt = select(models.User).where(models.User.id == lending_in.user_id)
    user = db.execute(user_stmt).scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Create lending record
    lending_record = lending.borrow_book(
        db=db,
        obj_in=lending_in
    )
    
    # Convert lending object to dictionary for event publishing
    lending_data = {
        column.name: getattr(lending_record, column.name) 
        for column in lending_record.__table__.columns
    }
    
    # Serialize date objects
    lending_data['borrow_date'] = lending_data['borrow_date'].isoformat()
    lending_data['due_date'] = lending_data['due_date'].isoformat()
    if lending_data.get('return_date'):
        lending_data['return_date'] = lending_data['return_date'].isoformat()
    
    publish_event("book_borrowed", lending_data)
    
    return lending_record


@router.post("/return/{lending_id}", response_model=schemas.Lending)
def return_book(lending_id: int, db: Session = Depends(get_db)):
    """
    Return a previously borrowed book.
    """
    # Find the lending record using select statement
    lending_stmt = select(models.Lending).where(models.Lending.id == lending_id)
    lending_record = db.execute(lending_stmt).scalar_one_or_none()
    
    if not lending_record:
        raise HTTPException(status_code=404, detail="Lending record not found")
        
    # Check if the book is already returned
    if lending_record.return_date is not None:
        raise HTTPException(status_code=400, detail="Book already returned")
    
    try:
        # Return the book
        returned_lending = lending.return_book(db=db, lending_id=lending_id)
        
        # Convert lending object to dictionary for event publishing
        lending_data = {
            column.name: getattr(returned_lending, column.name) 
            for column in returned_lending.__table__.columns
        }
        
        # Make sure date objects are serializable
        lending_data['borrow_date'] = lending_data['borrow_date'].isoformat()
        lending_data['due_date'] = lending_data['due_date'].isoformat()
        if lending_data.get('return_date'):
            lending_data['return_date'] = lending_data['return_date'].isoformat()
        
        # Publish event to notify admin service
        publish_event("book_returned", {
            **lending_data,
            "book_id": returned_lending.book_id,  # Ensure book_id is included
            "is_available": True  # Explicitly set availability to True
        })
        
        return returned_lending
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))