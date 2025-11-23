#!/usr/bin/env python3
"""
Utility script to generate a proper bcrypt hash for testing.
This will help fix the malformed hash issue.
"""

from passlib.context import CryptContext

#pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

pwd_context = CryptContext(schemes=["bcrypt"])

def generate_hash(password: str) -> str:
    """Generate a proper bcrypt hash for the given password."""
    return pwd_context.hash(password)

def verify_hash(password: str, hash_str: str) -> bool:
    """Verify a password against a hash."""
    try:
        return pwd_context.verify(password, hash_str)
    except Exception as e:
        print(f"Error verifying hash: {e}")
        return False

if __name__ == "__main__":
    # Generate hash for the test password
    test_password = "PVS12345"

    print(f"Generating hash for password: {test_password}")
    new_hash = generate_hash(test_password)
    print(f"Generated hash: {new_hash}")
    print(f"Hash length: {len(new_hash)}")

    # Verify it works
    is_valid = verify_hash(test_password, new_hash)
    print(f"Verification successful: {is_valid}")

    # Test the problematic hash from database
    old_hash = "$2b$12$qIisE3k.91bI7uCiQpXVDewJe5VzZ237EEBdcJuRyEmUOjJg0nusS"
    print(f"\nTesting old hash: {old_hash}")
    print(f"Old hash length: {len(old_hash)}")

    try:
        is_valid_old = verify_hash(test_password, old_hash)
        print(f"Old hash verification: {is_valid_old}")
    except Exception as e:
        print(f"Old hash is malformed: {e}")

    print(f"\nUse this SQL to update the user's hash:")
    print(f"UPDATE tuser SET hashcode = '{new_hash}' WHERE code = 'julie';")