from datetime import timedelta
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api import deps
from app.core import security
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.services.auth_service import auth_service
from pydantic import BaseModel

from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.user import UserResponse

router = APIRouter()

class RegisterRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class GoogleLoginRequest(BaseModel):
    id_token: str

@router.post("/login/google", response_model=Token)
async def login_google(
    request_data: GoogleLoginRequest,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    OAuth2 with Google logic.
    """
    user_info = auth_service.verify_google_token(request_data.id_token)
    if not user_info:
        raise HTTPException(status_code=400, detail="Invalid Google token")

    email = user_info.get("email")
    google_id = user_info.get("sub")
    full_name = user_info.get("name")
    avatar = user_info.get("picture")

    # Check if user exists
    query = select(User).where(User.email == email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        # Create new user
        user = User(
            email=email,
            full_name=full_name,
            google_id=google_id,
            avatar_url=avatar,
            is_active=True
        )
        db.add(user)
        try:
            await db.commit()
            await db.refresh(user)
        except Exception as e:
            await db.rollback()
            # If user was created by another parallel request
            result = await db.execute(query)
            user = result.scalar_one_or_none()
            if not user:
                raise e

    # Generate JWT
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }
@router.post("/register", response_model=Any)
async def register(
    request_data: RegisterRequest,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Standard user registration.
    """
    # Check if user exists
    query = select(User).where(User.email == request_data.email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Create new user
    hashed_password = security.get_password_hash(request_data.password)
    user = User(
        email=request_data.email,
        hashed_password=hashed_password,
        is_active=True
    )
    db.add(user)
    try:
        await db.commit()
        await db.refresh(user)
    except Exception as e:
        await db.rollback()
        raise e
    
    return {"status": "ok", "email": user.email}

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Standard OAuth2 token login.
    """
    query = select(User).where(User.email == form_data.username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if not user or not user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    if not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    # Generate JWT
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

# ============================================================
# Profile Management
# ============================================================

class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    social_handle: Optional[str] = None

@router.get("/me", response_model=UserResponse)
async def read_user_me(
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_user_me(
    profile_in: ProfileUpdate,
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    if profile_in.full_name is not None:
        current_user.full_name = profile_in.full_name
    if profile_in.social_handle is not None:
        current_user.social_handle = profile_in.social_handle
    
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user
