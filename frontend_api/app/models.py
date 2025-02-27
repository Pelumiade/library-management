from sqlalchemy import Column, Integer, ForeignKey, Date, func
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta


Base = declarative_base()

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String, index=True)
    isbn = Column(String, unique=True, index=True)
    publisher = Column(String, index=True)
    category = Column(String, index=True)
    publication_year = Column(Integer)
    description = Column(String)
    is_available = Column(Boolean, default=True)
    lendings = relationship("Lending", back_populates="book")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    is_active = Column(Boolean, default=True)
    lendings = relationship("Lending", back_populates="user")


class Lending(Base):
    __tablename__ = "lendings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    book_id = Column(Integer, ForeignKey("books.id"))
    borrow_date = Column(Date, default=func.current_date())
    due_date = Column(Date)
    return_date = Column(Date, nullable=True)
    
    user = relationship("User", back_populates="lendings")
    book = relationship("Book", back_populates="lendings")