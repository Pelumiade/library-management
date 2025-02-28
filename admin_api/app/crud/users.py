from typing import List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import select

from .base import CRUDBase
from .. import models, schemas


class CRUDUser(CRUDBase[models.User, schemas.UserCreate, schemas.UserCreate]):
    """
    CRUD operations for User model
    """
    def get(self, db: Session, id: int) -> Optional[models.User]:  
        """
        Get a user by ID using select statement.
        """
        statement = select(models.User).where(models.User.id == id)
        return db.execute(statement).scalar_one_or_none()
    
    def get_by_email(self, db: Session, *, email: str) -> Optional[models.User]:
        """
        Get a user by email using select statement.
        """
        statement = select(models.User).where(models.User.email == email)
        return db.execute(statement).scalar_one_or_none()
    
    def create(self, db: Session, *, obj_in: Union[schemas.UserCreate, Dict[str, Any]]) -> models.User:
        """
        Create a new user from either a dictionary or UserCreate schema.
        """
        if isinstance(obj_in, dict):
            # Convert dictionary to User model
            db_obj = models.User(
                email=obj_in.get("email"),
                first_name=obj_in.get("first_name"),
                last_name=obj_in.get("last_name"),
                is_active=obj_in.get("is_active", True)
            )
        else:
            # Handle UserCreate schema object
            db_obj = models.User(
                email=obj_in.email,
                first_name=obj_in.first_name,
                last_name=obj_in.last_name,
                is_active=True
            )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_active_users(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[models.User]:
        """
        Get all active users using select statement.
        """
        statement = (
            select(models.User)
            .where(models.User.is_active == True)
            .offset(skip)
            .limit(limit)
        )
        return list(db.execute(statement).scalars().all())


user = CRUDUser(models.User)