from fastapi import APIRouter
from .api import admin_books, admin_users, admin_lending

api_router = APIRouter()
api_router.include_router(admin_users.router, prefix="/users", tags=["admin-users"])
api_router.include_router(admin_books.router, prefix="/books", tags=["admin-books"])
api_router.include_router(admin_lending.router, prefix="/lending", tags=["admin-lending"])