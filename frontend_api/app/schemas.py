from typing import Optional, List
from datetime import date
from pydantic import BaseModel, Field, EmailStr

class BookBase(BaseModel):
    title: str
    author: str
    isbn: str
    publisher: str
    category: str
    publication_year: int
    description: Optional[str] = None

class BookCreate(BookBase):
    pass

class Book(BookBase):
    id: int
    is_available: bool

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True

class LendingBase(BaseModel):
    book_id: int
    duration_days: int

class LendingCreate(LendingBase):
    user_id: int

class Lending(BaseModel):
    id: int
    user_id: int
    book_id: int
    borrow_date: date
    due_date: date
    return_date: Optional[date] = None

    class Config:
        orm_mode = True


class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    publisher: Optional[str] = None
    category: Optional[str] = None
    publication_year: Optional[int] = None
    description: Optional[str] = None
    is_available: Optional[bool] = None
    

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None
