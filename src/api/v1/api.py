from fastapi import APIRouter
from src.api.v1 import auth, users, committee, content

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(committee.router, prefix="/committees", tags=["Committees"])
api_router.include_router(content.router, prefix="/content", tags=["Content"])
