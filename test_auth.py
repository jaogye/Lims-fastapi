#!/usr/bin/env python3
"""
Test script to verify authentication is working
"""

import requests
import json

def test_login():
    url = "http://localhost:8000/auth/login"

    data = {
        "username": "julie",
        "password": "PVS12345"
    }

    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code == 200:
            print("✓ Authentication successful!")
            return True
        else:
            print("✗ Authentication failed!")
            return False

    except Exception as e:
        print(f"Error testing login: {e}")
        return False

if __name__ == "__main__":
    print("Testing authentication...")
    test_login()