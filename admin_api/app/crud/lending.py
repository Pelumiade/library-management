from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_

from .base import CRUDBase
from .. import models, schemas


class CRUDLending(CRUDBase[models.Lending, schemas.LendingCreate, schemas.LendingCreate]):
    """
    CRUD operations for Lending model
    """
    
    def create_lending(
        self, db: Session, *, user_id: int, book_id: int, duration_days: int
    ) -> models.Lending:
        """
        Create a new lending record.
        """
        # Check if book is available
        book = db.query(models.Book).filter(models.Book.id == book_id).first()
        if not book or not book.is_available:
            return None
        
        # Create lending record
        today = date.today()
        db_obj = models.Lending(
            user_id=user_id,
            book_id=book_id,
            borrow_date=today,
            due_date=today + timedelta(days=duration_days),
            return_date=None
        )
        
        # Update book availability
        book.is_available = False
        
        db.add(db_obj)
        db.add(book)
        db.commit()
        db.refresh(db_obj)
        
        return db_obj
    
    def get_active_lendings(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get all active lendings with user and book information.
        """
        results = (
            db.query(models.Lending)
            .options(joinedload(models.Lending.user), joinedload(models.Lending.book))
            .filter(models.Lending.return_date == None)
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        return results
    
    def get_user_lendings(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get all books borrowed by a user.
        """
        results = (
            db.query(models.Lending)
            .options(joinedload(models.Lending.book))
            .filter(models.Lending.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        return results
    
    def get_user_active_lendings(
        self, db: Session, *, user_id: int
    ) -> List[models.Lending]:
        """
        Get all active lendings for a user.
        """
        return (
            db.query(models.Lending)
            .filter(
                models.Lending.user_id == user_id,
                models.Lending.return_date == None
            )
            .all()
        )
    def get_active_lending_by_book(self, db: Session, book_id: int) -> Optional[models.Lending]:
        """
        Get active lending record for a specific book.
        """
        return db.query(models.Lending).filter(
            models.Lending.book_id == book_id,
            models.Lending.return_date == None
        ).first()
        
    def get_unavailable_books(self, db: Session) -> List[Dict[str, Any]]:
        """
        Get all unavailable books with their due dates.
        """
        results = []
        
        # Get all unreturned lendings
        lendings = (
            db.query(models.Lending)
            .options(joinedload(models.Lending.book))
            .filter(models.Lending.return_date == None)
            .all()
        )
        
        # Format results
        for lending in lendings:
            book_with_due_date = {
                **lending.book.__dict__,
                "due_date": lending.due_date
            }
            # Remove SQLAlchemy state attributes
            book_with_due_date.pop('_sa_instance_state', None)
            results.append(book_with_due_date)
        
        return results
    
    def mark_as_returned(
        self, db: Session, *, lending_id: int
    ) -> Optional[models.Lending]:
        """
        Mark a lending as returned.
        """
        lending = db.query(models.Lending).filter(models.Lending.id == lending_id).first()
        if not lending:
            return None
        
        # Update lending record
        lending.return_date = date.today()
        
        # Update book availability
        book = db.query(models.Book).filter(models.Book.id == lending.book_id).first()
        if book:
            book.is_available = True
            db.add(book)
        
        db.add(lending)
        db.commit()
        db.refresh(lending)
        
        return lending
    
    def get_overdue_lendings(self, db: Session) -> List[Dict[str, Any]]:
        """
        Get all overdue lendings.
        """
        today = date.today()
        
        results = (
            db.query(models.Lending)
            .options(joinedload(models.Lending.user), joinedload(models.Lending.book))
            .filter(
                models.Lending.due_date < today,
                models.Lending.return_date == None
            )
            .all()
        )
        
        return results


lending = CRUDLending(models.Lending)