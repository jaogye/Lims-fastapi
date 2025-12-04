"""
User administration API endpoints module.

This module defines FastAPI routes for user management including
creating users, managing access permissions, and uploading signature images.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List

from ..database.connection import get_db
from ..services.user_service import UserService
from ..services.auth_service import get_current_user
from ..models.user import User

router = APIRouter(prefix="/api/users", tags=["users"])


class MenuOptionResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class UserCreateRequest(BaseModel):
    code: str
    name: str
    password: str
    is_admin: bool
    active: bool
    email: Optional[str] = None
    reset_password: bool = False  # Only used during update
    options: List[str]  # Access options/permissions


class UserResponse(BaseModel):
    id: int
    code: str
    name: str
    is_admin: bool
    status: bool
    email: Optional[str]
    temp_password: bool
    signature_path: Optional[str]
    options: List[str]

    class Config:
        from_attributes = True


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class UserAccessResponse(BaseModel):
    option_name: str
    has_access: bool


@router.get("/", response_model=List[UserResponse])
async def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of all users (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can view users"
        )

    user_service = UserService(db)
    users = await user_service.get_all_users()
    return users


@router.get("/menu-options", response_model=List[MenuOptionResponse])
async def get_menu_options(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all available menu options"""
    user_service = UserService(db)
    options = await user_service.get_menu_options()
    return options


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user by ID (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can view users"
        )

    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new user (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create users"
        )

    user_service = UserService(db)
    user = await user_service.create_user(user_data.model_dump())
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can update users"
        )

    user_service = UserService(db)
    user = await user_service.update_user(user_id, user_data.model_dump())
    return user


@router.post("/{user_id}/reset-password")
async def reset_user_password(
    user_id: int,
    new_password: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reset user password (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can reset passwords"
        )

    user_service = UserService(db)
    result = await user_service.reset_password(user_id, new_password)
    return result


@router.post("/{user_id}/signature")
async def upload_signature(
    user_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload user signature image (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can upload signatures"
        )

    # Validate file format
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only image files are supported"
        )

    user_service = UserService(db)
    result = await user_service.upload_signature(user_id, file)
    return result


@router.get("/{user_id}/signature")
async def get_signature(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user signature image"""
    user_service = UserService(db)
    signature_data = await user_service.get_signature_path(user_id)

    if not signature_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Signature not found"
        )

    return Response(
        content=signature_data,
        media_type='image/png'
    )


@router.get("/{user_id}/access", response_model=List[UserAccessResponse])
async def get_user_access(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user access permissions (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can view user access"
        )

    user_service = UserService(db)
    access_list = await user_service.get_user_access(user_id)
    return access_list


@router.put("/{user_id}/access")
async def update_user_access(
    user_id: int,
    options: List[str],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user access permissions (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can update user access"
        )

    user_service = UserService(db)
    result = await user_service.update_user_access(user_id, options)
    return result


@router.post("/change-password")
async def change_own_password(
    password_data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Change current user's own password"""
    user_service = UserService(db)
    result = await user_service.change_own_password(
        current_user.id,
        password_data.old_password,
        password_data.new_password
    )
    return result


@router.delete("/{user_id}/signature")
async def delete_signature(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete user signature (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete signatures"
        )

    user_service = UserService(db)
    result = await user_service.delete_signature(user_id)
    return result
