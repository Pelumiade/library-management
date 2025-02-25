from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import api_router
from app.consumer import start_consumer
from app.config import settings

app = FastAPI(
    title="Library Management - Frontend API",
    description="API for library users to browse and borrow books",
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

@app.on_event("startup")
async def startup_event():
    # Start the message consumer
    start_consumer()

@app.get("/health")
def health_check():
    return {"status": "healthy"}

