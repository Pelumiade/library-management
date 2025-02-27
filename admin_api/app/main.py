from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .consumer import start_consumer

from .routers import api_router
from .config import settings

app = FastAPI(
    title="Library Management - Admin API",
    description="API for administrators to manage the library catalog and users",
    version="1.0.0",
    root_path="/library-management/admin_api",
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

@app.on_event("startup")
async def startup_event():
    # Start the message consumer
    start_consumer()


@app.get("/health")
def health_check():
    return {"status": "healthy"}


