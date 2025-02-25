from fastapi import APIRouter
from app.api import books, users, lending

api_router = APIRouter()
api_router.include_router(books.router, prefix="/admin", tags=["admin-books"])
api_router.include_router(users.router, prefix="/admin", tags=["admin-users"])
api_router.include_router(lending.router, prefix="/admin", tags=["admin-lending"])