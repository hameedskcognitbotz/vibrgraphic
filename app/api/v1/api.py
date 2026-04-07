from fastapi import APIRouter
from app.api.v1.endpoints import generate, auth

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(generate.router, prefix="/infographics", tags=["infographics"])
