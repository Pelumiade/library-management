from fastapi import APIRouter
from .api import books, lending, users

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(books.router, prefix="/books", tags=["books"])
api_router.include_router(lending.router, prefix="/lending", tags=["lending"])