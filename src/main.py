from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import uvicorn
from db import get_db

app = FastAPI(title="RCA API", version="1.0.0", description="API for Rajshahi City Association")

@app.get("/")
async def index():
    return {"msg": "Welcome to RCA Backend"}

@app.get("/healthz")
async def check_api_health():
    return {"status": "ok"}

@app.get("/login")
async def login(db: Session = Depends(get_db())):
    return {"msg": "Login Route Implementation"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
