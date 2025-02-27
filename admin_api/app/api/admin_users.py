from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..dependencies import get_db

router = APIRouter()

#Fetch all users
@router.get("/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Fetch all users enrolled in the library.
    """
    users = crud.user.get_multi(db, skip=skip, limit=limit)
    return users


#Get a specific user by ID
@router.get("/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """
    Get a specific user by ID.
    """
    db_user = crud.user.get(db, id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


#Update user information
@router.put("/{user_id}", response_model=schemas.User)
def update_user(
    user_id: int, user_data: schemas.UserCreate, db: Session = Depends(get_db)
):
    """
    Update a user's information.
    """
    db_user = crud.user.get(db, id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    updated_user = crud.user.update(db=db, db_obj=db_user, obj_in=user_data)
    return updated_user

