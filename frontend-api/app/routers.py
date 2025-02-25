from fastapi import APIRouter
from app.api import books, users, lending

api_router = APIRouter()
api_router.include_router(users.router, tags=["users"])
api_router.include_router(books.router, tags=["books"])
api_router.include_router(lending.router, tags=["lending"])