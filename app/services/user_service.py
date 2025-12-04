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
from ..core.security import get_password_hash, verify_password
from .email_service import EmailService

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
                u.id, u.code, u.name, u.is_admin, u.status, u.email, u.temp_password
            FROM tuser u
            ORDER BY u.name
        """
        result = self.db.execute(text(query))
        rows = result.fetchall()  # Consume all results before nested queries
        users = []

        for row in rows:
            user_id = row[0]
            # Get user options
            options = await self.get_user_options(user_id)

            users.append({
                "id": user_id,
                "code": row[1],
                "name": row[2],
                "is_admin": row[3],
                "status": row[4],
                "email": row[5],
                "temp_password": row[6],
                "signature_path": None,  # Signature stored as BLOB in DB
                "options": options
            })

        return users

    async def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID with options"""
        query = """
            SELECT
                u.id, u.code, u.name, u.is_admin, u.status, u.email, u.temp_password
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
            "email": row[5],
            "temp_password": row[6],
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

        # Hash the password using MATLAB-style (username + password)
        combined = f"{user_data['code']}{user_data['password']}"
        hashed_password = get_password_hash(combined)

        # Insert user
        insert_query = """
            INSERT INTO tuser (code, name, hashcode, is_admin, status, email, temp_password)
            VALUES (:code, :name, :hashcode, :is_admin, :active, :email, :temp_password)
        """
        self.db.execute(text(insert_query), {
            "code": user_data["code"],
            "name": user_data["name"],
            "hashcode": hashed_password,
            "is_admin": user_data["is_admin"],
            "active": user_data["active"],
            "email": user_data.get("email"),
            "temp_password": False
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

        # Handle password reset if requested
        reset_password = user_data.get("reset_password", False)
        temp_password = None

        if reset_password:
            # Check if user has email
            email = user_data.get("email") or existing.get("email")
            if not email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User must have an email address to reset password"
                )

            # Generate temporary password
            temp_password = EmailService.generate_temp_password()
            # Use MATLAB-style hash (username + password)
            combined = f"{user_data['code']}{temp_password}"
            hashed_password = get_password_hash(combined)

            # Update password and set temp_password flag
            pwd_query = """
                UPDATE tuser
                SET hashcode = :hashcode, temp_password = 1
                WHERE id = :user_id
            """
            self.db.execute(text(pwd_query), {
                "hashcode": hashed_password,
                "user_id": user_id
            })

            # Send email with temporary password
            email_sent = await EmailService.send_temp_password_email(
                to_email=email,
                username=user_data["code"],
                temp_password=temp_password,
                user_name=user_data["name"]
            )

            if not email_sent:
                # Rollback if email fails
                self.db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to send password reset email. Please check SMTP configuration."
                )

        # Update user basic info
        update_query = """
            UPDATE tuser
            SET code = :code, name = :name, is_admin = :is_admin, status = :active, email = :email
            WHERE id = :user_id
        """
        self.db.execute(text(update_query), {
            "code": user_data["code"],
            "name": user_data["name"],
            "is_admin": user_data["is_admin"],
            "active": user_data["active"],
            "email": user_data.get("email"),
            "user_id": user_id
        })

        # Update password if provided manually (not via reset)
        if user_data.get("password") and not reset_password:
            # Use MATLAB-style hash (username + password)
            combined = f"{user_data['code']}{user_data['password']}"
            hashed_password = get_password_hash(combined)
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
        """Reset user password (admin function)"""
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

    async def change_own_password(self, user_id: int, old_password: str, new_password: str) -> Dict[str, str]:
        """Change user's own password and clear temp_password flag"""
        # Get user from database
        query = "SELECT code, hashcode FROM tuser WHERE id = :user_id"
        result = self.db.execute(text(query), {"user_id": user_id})
        row = result.fetchone()

        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        username = row[0].strip() if row[0] else ""
        current_hash = row[1].strip() if row[1] else ""

        # Verify old password using MATLAB-style hash (username + password)
        combined_old = f"{username}{old_password}"
        if not verify_password(combined_old, current_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )

        # Create new hash using MATLAB-style combination
        combined_new = f"{username}{new_password}"
        hashed_password = get_password_hash(combined_new)

        # Update password and clear temp_password flag
        update_query = """
            UPDATE tuser
            SET hashcode = :hashcode, temp_password = 0
            WHERE id = :user_id
        """
        self.db.execute(text(update_query), {
            "hashcode": hashed_password,
            "user_id": user_id
        })
        self.db.commit()

        return {"message": "Password changed successfully"}

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

    async def delete_signature(self, user_id: int) -> Dict[str, str]:
        """Delete user signature"""
        # Check if user exists
        existing = await self.get_user_by_id(user_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Delete signature
        update_query = "UPDATE tuser SET signature = NULL WHERE id = :user_id"
        self.db.execute(text(update_query), {"user_id": user_id})
        self.db.commit()

        return {"message": "Signature deleted successfully"}

    async def get_user_access(self, user_id: int) -> List[Dict[str, Any]]:
        """Get user access permissions"""
        # Get all options
        options_query = "SELECT id, name FROM optionmenu ORDER BY name"
        result = self.db.execute(text(options_query))
        all_options = [(row[0], row[1]) for row in result.fetchall()]

        # Get user's access
        access_query = """
            SELECT option_id
            FROM optionuser
            WHERE user_id = :user_id
        """
        result = self.db.execute(text(access_query), {"user_id": user_id})
        user_option_ids = {row[0] for row in result.fetchall()}

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

    async def get_menu_options(self):
        """Get all available menu options"""
        query = "SELECT id, name FROM optionmenu ORDER BY name"
        result = self.db.execute(text(query))

        options = []
        for row in result:
            options.append({
                "id": row[0],
                "name": row[1]
            })

        return options
