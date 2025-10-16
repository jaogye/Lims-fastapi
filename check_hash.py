#!/usr/bin/env python3
"""
Check what's actually stored in the database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.core.config import settings

def check_hash():
    """Check the current hash in database"""

    engine = create_engine(settings.DATABASE_URL)

    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT code, hashcode, LEN(hashcode) as hash_length FROM tuser WHERE code = :username"),
                {"username": "julie"}
            )
            row = result.fetchone()

            if row:
                print(f"User: {row[0]}")
                print(f"Hash: {row[1]}")
                print(f"Length: {row[2]}")
                print(f"Python len: {len(row[1])}")
            else:
                print("User not found")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_hash()