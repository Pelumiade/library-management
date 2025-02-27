from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import models, schemas
from ..crud import books
from ..dependencies import get_db
from ..publisher import publish_event

router = APIRouter()


@router.get("/", response_model=List[schemas.Book])
def read_books(
    skip: int = 0, 
    limit: int = 100,
    publisher: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get books list with optional publisher and category filters.
    """

    book_list = books.book.get_all(
        db, 
        skip=skip, 
        limit=limit,
        publisher=publisher,
        category=category
    )
    return book_list


@router.get("/{book_id}", response_model=schemas.Book)

def read_book(book_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific book by its ID.
    """
    db_book = books.book.get(db, id=book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book

