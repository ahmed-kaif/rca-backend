from fastapi import FastAPI
import uvicorn
app = FastAPI(title="RCA API", version="1.0.0", description="API for Rajshahi City Association")

@app.get("/")
async def index():
    return {"msg": "Welcome to RCA Backend"}

@app.get("/healthz")
async def check_api_health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
