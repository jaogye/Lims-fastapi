"""
User service module for user management operations.

This module provides services for user CRUD operations, access control,
password management, and signature image handling.
"""

from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import HTTPException, UploadFile, status
from typing import List, Dict, Any, Optional
import os
import logging
from datetime import datetime

from ..models.user import User, UserOption, OptionMenu
from ..core.security import get_password_hash

logger = logging.getLogger(__name__)


class UserService:
    """
    Service class for user management operations.

    Handles user CRUD, password management, signature upload,
    and access control.

    Attributes:
        db (Session): SQLAlchemy database session.
    """

    def __init__(self, db: Session):
        self.db = db

    async def get_all_users(self) -> List[Dict[str, Any]]:
        """Get list of all users with their access options"""
        query = """
            SELECT
                u.id, u.code, u.name, u.is_admin, u.status
            FROM tuser u
            ORDER BY u.name
        """
        result = self.db.execute(text(query))
        users = []

        for row in result:
            user_id = row[0]
            # Get user options
            options = await self.get_user_options(user_id)

            users.append({
                "id": user_id,
                "code": row[1],
                "name": row[2],
                "is_admin": row[3],
                "status": row[4],
                "signature_path": None,  # Signature stored as BLOB in DB
                "options": options
            })

        return users

    async def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID with options"""
        query = """
            SELECT
                u.id, u.code, u.name, u.is_admin, u.status
            FROM tuser u
            WHERE u.id = :user_id
        """
        result = self.db.execute(text(query), {"user_id": user_id})
        row = result.fetchone()

        if not row:
            return None

        # Get user options
        options = await self.get_user_options(user_id)

        return {
            "id": row[0],
            "code": row[1],
            "name": row[2],
            "is_admin": row[3],
            "status": row[4],
            "signature_path": None,  # Signature stored as BLOB in DB
            "options": options
        }

    async def get_user_options(self, user_id: int) -> List[str]:
        """Get list of access options for a user"""
        query = """
            SELECT o.name
            FROM optionuser a
            JOIN optionmenu o ON a.option_id = o.id
            WHERE a.user_id = :user_id
        """
        result = self.db.execute(text(query), {"user_id": user_id})
        options = [row[0] for row in result]
        return options

    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user"""
        # Check if user code already exists
        check_query = "SELECT id FROM tuser WHERE code = :code"
        existing = self.db.execute(text(check_query), {"code": user_data["code"]}).fetchone()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with code '{user_data['code']}' already exists"
            )

        # Hash the password
        hashed_password = get_password_hash(user_data["password"])

        # Insert user
        insert_query = """
            INSERT INTO tuser (code, name, hashcode, is_admin, status)
            VALUES (:code, :name, :hashcode, :is_admin, :active)
        """
        self.db.execute(text(insert_query), {
            "code": user_data["code"],
            "name": user_data["name"],
            "hashcode": hashed_password,
            "is_admin": user_data["is_admin"],
            "active": user_data["active"]
        })
        self.db.commit()

        # Get the created user ID
        result = self.db.execute(text("SELECT @@IDENTITY AS id"))
        user_id = result.fetchone()[0]

        # Set access options
        if user_data.get("options"):
            await self.update_user_access(user_id, user_data["options"])

        return await self.get_user_by_id(user_id)

    async def update_user(self, user_id: int, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing user"""
        # Check if user exists
        existing = await self.get_user_by_id(user_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Update user
        update_query = """
            UPDATE tuser
            SET code = :code, name = :name, is_admin = :is_admin, status = :active
            WHERE id = :user_id
        """
        self.db.execute(text(update_query), {
            "code": user_data["code"],
            "name": user_data["name"],
            "is_admin": user_data["is_admin"],
            "active": user_data["active"],
            "user_id": user_id
        })

        # Update password if provided
        if user_data.get("password"):
            hashed_password = get_password_hash(user_data["password"])
            pwd_query = "UPDATE tuser SET hashcode = :hashcode WHERE id = :user_id"
            self.db.execute(text(pwd_query), {
                "hashcode": hashed_password,
                "user_id": user_id
            })

        self.db.commit()

        # Update access options
        if user_data.get("options"):
            await self.update_user_access(user_id, user_data["options"])

        return await self.get_user_by_id(user_id)

    async def reset_password(self, user_id: int, new_password: str) -> Dict[str, str]:
        """Reset user password"""
        # Check if user exists
        existing = await self.get_user_by_id(user_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Hash and update password
        hashed_password = get_password_hash(new_password)
        update_query = "UPDATE tuser SET hashcode = :hashcode WHERE id = :user_id"
        self.db.execute(text(update_query), {
            "hashcode": hashed_password,
            "user_id": user_id
        })
        self.db.commit()

        return {"message": "Password reset successfully"}

    async def upload_signature(self, user_id: int, file: UploadFile) -> Dict[str, str]:
        """Upload user signature image"""
        # Check if user exists
        existing = await self.get_user_by_id(user_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Read file contents
        contents = await file.read()

        # Update user record with binary data
        update_query = "UPDATE tuser SET signature = :signature WHERE id = :user_id"
        self.db.execute(text(update_query), {
            "signature": contents,
            "user_id": user_id
        })
        self.db.commit()

        return {
            "message": "Signature uploaded successfully",
            "file_size": len(contents)
        }

    async def get_signature_path(self, user_id: int) -> Optional[bytes]:
        """Get user signature binary data"""
        query = "SELECT signature FROM tuser WHERE id = :user_id"
        result = self.db.execute(text(query), {"user_id": user_id})
        row = result.fetchone()

        if not row or not row[0]:
            return None

        return row[0]

    async def get_user_access(self, user_id: int) -> List[Dict[str, Any]]:
        """Get user access permissions"""
        # Get all options
        options_query = "SELECT id, name FROM optionmenu ORDER BY name"
        result = self.db.execute(text(options_query))
        all_options = [(row[0], row[1]) for row in result]

        # Get user's access
        access_query = """
            SELECT option_id
            FROM optionuser
            WHERE user_id = :user_id
        """
        result = self.db.execute(text(access_query), {"user_id": user_id})
        user_option_ids = {row[0] for row in result}

        # Build response
        access_list = []
        for option_id, option_name in all_options:
            access_list.append({
                "option_name": option_name,
                "has_access": option_id in user_option_ids
            })

        return access_list

    async def update_user_access(self, user_id: int, options: List[str]) -> Dict[str, str]:
        """Update user access permissions"""
        # Delete existing access
        delete_query = "DELETE FROM optionuser WHERE user_id = :user_id"
        self.db.execute(text(delete_query), {"user_id": user_id})

        # Insert new access
        for option_name in options:
            # Get option ID
            option_query = "SELECT id FROM optionmenu WHERE name = :name"
            result = self.db.execute(text(option_query), {"name": option_name})
            row = result.fetchone()

            if row:
                option_id = row[0]
                insert_query = """
                    INSERT INTO optionuser (user_id, option_id)
                    VALUES (:user_id, :option_id)
                """
                self.db.execute(text(insert_query), {
                    "user_id": user_id,
                    "option_id": option_id
                })

        self.db.commit()

        return {"message": "User access updated successfully"}
