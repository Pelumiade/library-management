from typing import Optional, List
from datetime import date
from pydantic import BaseModel, Field, EmailStr, ConfigDict

# Book schemas
class BookBase(BaseModel):
    title: str
    author: str
    isbn: str
    publisher: str
    category: str
    publication_year: int
    description: Optional[str] = None

    class Config:
        from_attributes = True


class BookCreate(BookBase):
    pass


# Book inherits from BookBase
class Book(BookBase):
    id: int
    is_available: bool

    model_config = ConfigDict(from_attributes=True)  


# User schemas
class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str


# UserCreate inherits from UserBase
class UserCreate(UserBase):
    pass


# User inherits from UserBase
class User(UserBase):
    id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True) 
    

# Lending schemas
class LendingBase(BaseModel):
    book_id: int
    duration_days: int


# LendingCreate inherits from LendingBase
class LendingCreate(LendingBase):
    user_id: int


# Lending schemas
class Lending(BaseModel):
    id: int
    user_id: int
    book_id: int
    borrow_date: date
    due_date: date
    return_date: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)


 # Lending with book
class LendingWithBook(Lending):
    book: Book
    
    model_config = ConfigDict(from_attributes=True) 


# Relationship with User and Book models
class LendingWithUserAndBook(Lending):
    user: User
    book: Book
    
    model_config = ConfigDict(from_attributes=True)  


#Book with due date
class BookWithDueDate(Book):
    due_date: date
    
    model_config = ConfigDict(from_attributes=True)  
