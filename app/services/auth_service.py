"""
Authentication service module.

This module provides authentication and authorization services including user
validation, password hashing, JWT token management, and user permission handling.
Compatible with legacy MATLAB password hashing system.
"""

from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Tuple, List
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ..models.user import User, UserOption, OptionMenu
from ..core.config import settings
from ..database.connection import get_db

pwd_context = CryptContext(schemes=["bcrypt"])
security = HTTPBearer()


class AuthService:
    """
    Service class for authentication and authorization.

    Provides methods for user authentication, password validation, JWT token
    generation and validation, and user permission management.

    Attributes:
        db (Session): SQLAlchemy database session.
    """

    def __init__(self, db: Session):
        """
        Initialize the authentication service.

        Args:
            db (Session): SQLAlchemy database session.
        """
        self.db = db

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.

        Args:
            plain_password (str): Plain text password to verify.
            hashed_password (str): Bcrypt password hash.

        Returns:
            bool: True if password matches, False otherwise.
        """
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """
        Generate a bcrypt hash for a password.

        Args:
            password (str): Plain text password.

        Returns:
            str: Bcrypt password hash.
        """
        return pwd_context.hash(password)

    def create_hash_code(self, username: str, password: str) -> str:
        """
        Create hash code compatible with MATLAB getHashCode function.

        Combines username and password before hashing for legacy compatibility.

        Args:
            username (str): User's username.
            password (str): User's password.

        Returns:
            str: Combined hash code.
        """
        # Mimics the MATLAB getHashCode function
        combined = f"{username}{password}"
        return self.get_password_hash(combined)

    async def validate_user_password(
        self, username: str, password: str
    ) -> Tuple[Optional[User], List[str]]:
        """
        Validate user credentials and retrieve user options.
    
        Args:
            username (str): User's username/code.
            password (str): User's plain text password.

        Returns:
            Tuple[Optional[User], List[str]]: User object and list of user options if valid,
                (None, []) otherwise.
        """
        username = username.strip()
        
        # Get user from database
        user = self.db.query(User).filter(User.code == username).first()
        if not user:
            return None, []

        # Verify password using MATLAB-style hash comparison
        # Combine username and password as per MATLAB getHashCode function
        combined = f"{username}{password}"

        # Strip any padding from the hash (SQL Server pads strings with spaces)
        hash_code = user.hashcode.strip() if user.hashcode else ""

        # Check if hash is properly formatted
        if not hash_code or len(hash_code) < 60:
            return None, []

        try:
            if not pwd_context.verify(combined, hash_code):
                return None, []
        except ValueError as e:
            # Log error but don't reveal to client
            print(f"Hash verification error for user {username}: {e}")
            return None, []

        # Get user options
        options = await self.get_user_options(user.id)
        
        return user, options

    async def get_user_options(self, user_id: int) -> List[str]:
        options_query = (
            self.db.query(OptionMenu.name)
            .join(UserOption)
            .filter(UserOption.user_id == user_id)
        )

        options = [option.name.strip() for option in options_query.all()]
        return options

    async def change_password(self, username: str, new_password: str) -> bool:
        """
        Change a user's password.

        Creates a new hash using MATLAB-style username+password combination
        and updates the user's hashcode in the database.

        Args:
            username (str): User's username/code.
            new_password (str): New plain text password.

        Returns:
            bool: True if password was successfully changed, False otherwise.
        """
        username = username.strip()
        
        # Get user from database
        user = self.db.query(User).filter(User.code == username).first()
        if not user:
            return False
        
        # Create new hash using MATLAB-style combination
        new_hash_code = self.create_hash_code(username, new_password)
        
        # Update user's hashcode
        user.hashcode = new_hash_code
        user.updated_at = datetime.utcnow()
        
        try:
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(f"Error changing password for user {username}: {e}")
            return False
      
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.SECRET_KEY, 
            algorithm=settings.ALGORITHM
        )
        
        return encoded_jwt
    
    async def get_current_user(self, token: str) -> Optional[User]:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=[settings.ALGORITHM]
            )
            username: str = payload.get("sub")
            
            if username is None:
                raise credentials_exception
                
        except JWTError:
            raise credentials_exception
    
        user = self.db.query(User).filter(User.code == username).first()
        
        if user is None:
            raise credentials_exception
            
        return user
    
    def is_active_user(self, user: User) -> bool:
        return user.status


# Dependency to get current user
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    auth_service = AuthService(db)
    user = await auth_service.get_current_user(credentials.credentials)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not auth_service.is_active_user(user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return user


# Dependency to get current admin user
async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user