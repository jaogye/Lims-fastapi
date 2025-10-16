"""
Authentication API endpoints module.

This module defines FastAPI routes for user authentication including login,
logout, and current user retrieval. Handles JWT token generation and
user session management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta

from ..database.connection import get_db
from ..services.auth_service import AuthService
from ..core.config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()


class LoginRequest(BaseModel):
    """Login request schema."""
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class UserResponse(BaseModel):
    id: int
    code: str
    name: str
    is_admin: bool
    status: bool
    options: list[str]


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    User login endpoint.

    Validates user credentials and returns a JWT access token for authentication.

    Args:
        login_data (LoginRequest): Username and password.
        db (Session): Database session dependency.

    Returns:
        TokenResponse: Access token, token type, and expiration time.

    Raises:
        HTTPException: 401 if credentials are invalid.
    """
    auth_service = AuthService(db)
    
    user, options = await auth_service.validate_user_password(
        login_data.username, 
        login_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth_service.create_access_token(
        data={"sub": user.code, "user_id": user.id}
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/logout")
async def logout():
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    user = await auth_service.get_current_user(credentials.credentials)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_options = await auth_service.get_user_options(user.id)
    
    return UserResponse(
        id=user.id,
        code=user.code,
        name=user.name,
        is_admin=user.is_admin,
        status=user.status,
        options=user_options
    )