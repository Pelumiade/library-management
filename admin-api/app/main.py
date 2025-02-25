from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import api_router
from app.config import settings

app = FastAPI(
    title="Library Management - Admin API",
    description="API for administrators to manage the library catalog and users",
    version="1.0.0",
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router)

@app.get("/health")
def health_check():
    return {"status": "healthy"}