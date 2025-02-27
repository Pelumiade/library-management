from fastapi import APIRouter
from .api import admin_books, admin_users, admin_lending

api_router = APIRouter()
api_router.include_router(admin_users.router, prefix="/admin/users", tags=["admin-users"])
api_router.include_router(admin_books.router, prefix="/admin/books", tags=["admin-books"])
api_router.include_router(admin_lending.router, prefix="/admin/lending", tags=["admin-lending"])