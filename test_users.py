#!/usr/bin/env python3
"""
Test script to verify user creation and retrieval
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:5000"

def test_user_creation_and_retrieval():
    """Test user creation and retrieval"""
    print("👥 Testing User Creation and Retrieval...")
    
    # Test users
    test_users = [
        {
            "username": "alice",
            "email": "alice@example.com",
            "password": "AlicePassword123!"
        },
        {
            "username": "bob",
            "email": "bob@example.com",
            "password": "BobPassword123!"
        },
        {
            "username": "charlie",
            "email": "charlie@example.com",
            "password": "CharliePassword123!"
        }
    ]
    
    tokens = []
    
    # Create test users
    print("\n1. Creating test users...")
    for user_data in test_users:
        try:
            response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
            if response.status_code == 201:
                print(f"✅ Created user: {user_data['username']}")
                tokens.append(response.json()['access_token'])
            else:
                print(f"❌ Failed to create user {user_data['username']}: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Error creating user {user_data['username']}: {e}")
    
    if not tokens:
        print("❌ No users created, cannot test retrieval")
        return
    
    # Test user retrieval
    print("\n2. Testing user retrieval...")
    for i, token in enumerate(tokens):
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{BASE_URL}/chat/users", headers=headers)
            if response.status_code == 200:
                users = response.json()['users']
                print(f"✅ User {test_users[i]['username']} can see {len(users)} other users:")
                for user in users:
                    print(f"   - {user['username']} ({'Admin' if user.get('is_admin') else 'User'})")
            else:
                print(f"❌ Failed to get users for {test_users[i]['username']}: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Error getting users for {test_users[i]['username']}: {e}")
    
    print("\n🎉 User creation and retrieval test completed!")
    print("Now you should be able to see other users in the chat interface.")

if __name__ == "__main__":
    test_user_creation_and_retrieval()
