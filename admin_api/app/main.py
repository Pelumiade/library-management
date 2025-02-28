from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .consumer import start_consumer
from .routers import api_router
from .config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    try:
        # Start the message consumer
        start_consumer()
        print("Message consumer started successfully")
        
        yield
    except Exception as e:
        print(f"Error during startup: {e}")
        raise
    finally:
        # Optional: Add any cleanup logic if needed
        print("Application shutdown initiated")

# Create FastAPI app with lifespan
app = FastAPI(
    title="Library Management - Admin API",
    description="API for administrators to manage the library catalog and users",
    version="1.0.0",
    root_path='/admin',
    lifespan=lifespan  # Use the new lifespan method
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