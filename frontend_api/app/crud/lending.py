from datetime import date, datetime, timedelta
from typing import List, Optional, Dict, Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Lending, Book, User
from ..schemas import LendingCreate


# Lending operations
class LendingCRUD:
    def borrow_book(self, db: Session, *, obj_in: LendingCreate) -> Lending:
        """
        Borrow a book and create a lending record.
        """
        # Check if book is available using select statement
        book_stmt = select(Book).where(Book.id == obj_in.book_id)
        book = db.execute(book_stmt).scalar_one_or_none()
        
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
        # Find lending record using select statement
        lending_stmt = select(Lending).where(Lending.id == lending_id)
        lending = db.execute(lending_stmt).scalar_one_or_none()
        
        if not lending:
            raise ValueError("Lending record not found")
        
        # Check if already returned
        if lending.return_date is not None:
            raise ValueError("Book already returned")
        
        # Update lending record
        lending.return_date = date.today()
        
        # Update book availability 
        book_stmt = select(Book).where(Book.id == lending.book_id)
        book = db.execute(book_stmt).scalar_one_or_none()
        
        if book:
            book.is_available = True  
            db.add(book)
        
        db.add(lending)
        db.commit()
        db.refresh(lending)
        
        return lending


lending = LendingCRUD()