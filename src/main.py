from fastapi import FastAPI
from src.api.v1.api import api_router
from src.core.config import settings

app = FastAPI(title="Alumni Association API")

# Include the router
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def root():
    return {"message": "Welcome to the Alumni Association API"}
