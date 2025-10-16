"""
Security utilities module.

This module provides security-related utility functions including JWT token
creation/validation, password hashing/verification, and MATLAB-compatible
hash generation for legacy system integration.
"""

from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Any, Union
from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.

    Args:
        subject (Union[str, Any]): Subject identifier (usually username or user ID).
        expires_delta (Optional[timedelta]): Custom expiration time. Uses default if None.

    Returns:
        str: Encoded JWT token string.
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def create_matlab_hash(username: str, password: str) -> str:
    """Create hash compatible with MATLAB getHashCode function"""
    # This mimics the MATLAB hash generation
    combined = f"{username}{password}"
    return get_password_hash(combined)


def verify_matlab_hash(username: str, password: str, stored_hash: str) -> bool:
    """Verify password using MATLAB-compatible hash"""
    # For MATLAB compatibility, we might need to implement the exact
    # hash algorithm used in the original MATLAB code
    # This is a placeholder implementation
    generated_hash = create_matlab_hash(username, password)
    return generated_hash == stored_hash