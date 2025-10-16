#!/usr/bin/env python3
"""
Simple utility script to fix truncated bcrypt hashes in the database using raw SQL.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def fix_user_hash_simple(username: str, password: str):
    """Fix the hash for a specific user using raw SQL"""

    # Create database connection
    engine = create_engine(settings.DATABASE_URL)

    try:
        with engine.connect() as conn:
            # Check current hash
            result = conn.execute(
                text("SELECT hashcode FROM tuser WHERE code = :username"),
                {"username": username}
            )
            row = result.fetchone()

            if not row:
                print(f"User '{username}' not found")
                return False

            current_hash = row[0]
            print(f"Current hash for {username}: {current_hash}")
            print(f"Current hash length: {len(current_hash) if current_hash else 0}")

            # Generate new hash
            new_hash = pwd_context.hash(password)
            print(f"New hash: {new_hash}")
            print(f"New hash length: {len(new_hash)}")

            # Update user
            conn.execute(
                text("UPDATE tuser SET hashcode = :new_hash WHERE code = :username"),
                {"new_hash": new_hash, "username": username}
            )
            conn.commit()

            print(f"Successfully updated hash for user '{username}'")

            # Verify the new hash works
            if pwd_context.verify(password, new_hash):
                print("✓ Hash verification successful")
            else:
                print("✗ Hash verification failed")

            return True

    except Exception as e:
        print(f"Error fixing hash: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python fix_hash_simple.py <username> <password>")
        print("Example: python fix_hash_simple.py julie PVS12345")
        sys.exit(1)

    username = sys.argv[1]
    password = sys.argv[2]

    print(f"Fixing hash for user: {username}")
    success = fix_user_hash_simple(username, password)

    if success:
        print("Hash fix completed successfully!")
    else:
        print("Hash fix failed!")
        sys.exit(1)