#!/usr/bin/env python3
"""
Utility script to fix truncated bcrypt hashes in the database.
This script will regenerate the hash for a specific user.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
from app.core.config import settings
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def fix_user_hash(username: str, password: str):
    """Fix the hash for a specific user"""

    # Create database connection
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # Find the user
        user = db.query(User).filter(User.code == username).first()
        if not user:
            print(f"User '{username}' not found")
            return False

        print(f"Current hash for {username}: {user.hashcode}")
        print(f"Current hash length: {len(user.hashcode)}")

        # Generate new hash
        new_hash = pwd_context.hash(password)
        print(f"New hash: {new_hash}")
        print(f"New hash length: {len(new_hash)}")

        # Update user
        user.hashcode = new_hash
        db.commit()

        print(f"Successfully updated hash for user '{username}'")

        # Verify the new hash works
        if pwd_context.verify(password, new_hash):
            print("✓ Hash verification successful")
        else:
            print("✗ Hash verification failed")

        return True

    except Exception as e:
        print(f"Error fixing hash: {e}")
        db.rollback()
        return False

    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python fix_user_hash.py <username> <password>")
        print("Example: python fix_user_hash.py julie PVS12345")
        sys.exit(1)

    username = sys.argv[1]
    password = sys.argv[2]

    print(f"Fixing hash for user: {username}")
    success = fix_user_hash(username, password)

    if success:
        print("Hash fix completed successfully!")
    else:
        print("Hash fix failed!")
        sys.exit(1)