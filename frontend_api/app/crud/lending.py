from datetime import date, datetime, timedelta
from typing import List, Optional, Dict, Any

from sqlalchemy import and_
from sqlalchemy.orm import Session

from ..models import Lending, Book, User
from ..schemas import LendingCreate


# Lending operations
class LendingCRUD:
    def borrow_book(self, db: Session, *, obj_in: LendingCreate) -> Lending:
        # Check if book is available
        book = db.query(Book).filter(Book.id == obj_in.book_id).first()
        if not book or not book.is_available:
            raise ValueError("Book is not available for borrowing")
        
        # Create lending record
        borrow_date = date.today()
        due_date = borrow_date + timedelta(days=obj_in.duration_days)
        
        db_obj = Lending(
            user_id=obj_in.user_id,
            book_id=obj_in.book_id,
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
    
    def return_book(self, db: Session, *, lending_id: int) -> Optional[Lending]:
        """
        Mark a lending as returned and update book availability.
        """
        lending = db.query(Lending).filter(Lending.id == lending_id).first()
        if not lending:
            raise ValueError("Lending record not found")
        
        # Check if already returned
        if lending.return_date is not None:
            raise ValueError("Book already returned")
        
        # Update lending record
        lending.return_date = date.today()
        
        # Update book availability 
        book = db.query(Book).filter(Book.id == lending.book_id).first()
        if book:
            book.is_available = True  
            db.add(book)
        
        db.add(lending)
        db.commit()
        db.refresh(lending)
        
        return lending


lending = LendingCRUD()