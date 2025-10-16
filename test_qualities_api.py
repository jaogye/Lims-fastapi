#!/usr/bin/env python3
"""
Example script showing how to access protected endpoints with authentication
"""

import requests
import json

def get_access_token():
    """Get access token by logging in"""
    login_url = "http://localhost:8000/auth/login"
    login_data = {
        "username": "julie",
        "password": "PVS12345"
    }

    response = requests.post(login_url, json=login_data)
    if response.status_code == 200:
        token_data = response.json()
        return token_data["access_token"]
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
        return None

def get_qualities_with_auth():
    """Get qualities using authenticated request"""
    # Step 1: Get access token
    access_token = get_access_token()
    if not access_token:
        return

    print(f"Got access token: {access_token[:50]}...")

    # Step 2: Make authenticated request to qualities endpoint
    qualities_url = "http://localhost:8000/api/master-data/qualities"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    response = requests.get(qualities_url, headers=headers)

    print(f"Qualities API Response:")
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        qualities = response.json()
        print(f"Number of qualities: {len(qualities)}")
        print("qualities:")
        for qualitie in qualities:
            print(f"  - ID: {qualitie['id']}, Name: {qualitie['name']}")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    print("Testing authenticated API access...")
    get_qualities_with_auth()
    