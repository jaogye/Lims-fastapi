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

def get_products_with_auth():
    """Get products using authenticated request"""
    # Step 1: Get access token
    access_token = get_access_token()
    if not access_token:
        return

    print(f"Got access token: {access_token[:50]}...")

    # Step 2: Make authenticated request to products endpoint
    products_url = "http://localhost:8000/api/master-data/products"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    response = requests.get(products_url, headers=headers)

    print(f"Products API Response:")
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        products = response.json()
        print(f"Number of products: {len(products)}")
        print("Products:")
        for product in products:
            print(f"  - ID: {product['id']}, Name: {product['name']}")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    print("Testing authenticated API access...")
    get_products_with_auth()
    