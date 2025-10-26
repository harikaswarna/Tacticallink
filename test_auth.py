#!/usr/bin/env python3
"""
Simple test script to verify TacticalLink authentication
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:5000"
TEST_USER = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "TestPassword123!"
}

def test_auth():
    """Test authentication flow"""
    print("🔐 Testing TacticalLink Authentication...")
    
    # Test 1: Health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test 2: Register user
    print("\n2. Testing user registration...")
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=TEST_USER)
        if response.status_code == 201:
            print("✅ User registration successful")
            data = response.json()
            token = data.get('access_token')
            user_id = data.get('user_id')
        else:
            print(f"❌ Registration failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ Registration failed: {e}")
        return
    
    # Test 3: Verify token
    print("\n3. Testing token verification...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/auth/verify", headers=headers)
        if response.status_code == 200:
            print("✅ Token verification successful")
            data = response.json()
            print(f"   User ID: {data.get('user_id')}")
            print(f"   Username: {data.get('username')}")
        else:
            print(f"❌ Token verification failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ Token verification failed: {e}")
        return
    
    # Test 4: Login
    print("\n4. Testing user login...")
    try:
        login_data = {
            "username": TEST_USER["username"],
            "password": TEST_USER["password"]
        }
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            print("✅ User login successful")
            data = response.json()
            new_token = data.get('access_token')
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return
    
    # Test 5: Verify new token
    print("\n5. Testing new token verification...")
    try:
        headers = {"Authorization": f"Bearer {new_token}"}
        response = requests.get(f"{BASE_URL}/auth/verify", headers=headers)
        if response.status_code == 200:
            print("✅ New token verification successful")
        else:
            print(f"❌ New token verification failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ New token verification failed: {e}")
        return
    
    print("\n🎉 All authentication tests passed!")
    print("The login/logout issue should be fixed now.")

if __name__ == "__main__":
    test_auth()
