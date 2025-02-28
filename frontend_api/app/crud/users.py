from datetime import date, datetime, timedelta
from typing import List, Optional, Dict, Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Lending, Book, User
from ..schemas import UserCreate, UserUpdate


# User operations
class UserCRUD:
    def get(self, db: Session, id: int) -> Optional[User]:
        """
        Get a user by ID using select statement.
        """
        statement = select(User).where(User.id == id)
        return db.execute(statement).scalar_one_or_none()

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """
        Get a user by email using select statement.
        """
        statement = select(User).where(User.email == email)
        return db.execute(statement).scalar_one_or_none()

    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Get multiple users with pagination using select statement.
        """
        statement = select(User).offset(skip).limit(limit)
        return list(db.execute(statement).scalars().all())

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """
        Create a new user.
        """
        db_obj = User(
            email=obj_in.email,
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            is_active=True
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: User, obj_in: UserUpdate) -> User:
        """
        Update an existing user.
        """
        # Use model_dump for Pydantic V2 compatibility
        update_data = obj_in.model_dump(exclude_unset=True)
        for field in update_data:
            setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> User:
        """
        Remove a user by ID.
        """
        # Use db.get() instead of query().get()
        obj = db.get(User, id)
        if obj is None:
            raise ValueError(f"User with id {id} not found")
        db.delete(obj)
        db.commit()
        return obj


user = UserCRUD()