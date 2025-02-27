from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import models, schemas
from ..crud import books, users, lending
from ..dependencies import get_db
from ..publisher import publish_event

router = APIRouter()

@router.post("/", response_model=schemas.User)
def create_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    # Use the 'user' instance from the users module
    db_user = users.user.get_by_email(db, email=user_in.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create the user
    new_user = users.user.create(db=db, obj_in=user_in)
    
    # Convert user object to dictionary for event publishing
    user_data = {column.name: getattr(new_user, column.name) for column in new_user.__table__.columns}
    
    # Publish event to notify admin service
    publish_event("user_created", user_data)
    
    return new_user

