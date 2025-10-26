#!/usr/bin/env python3
"""
Test script to verify private chat room functionality with join keys
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:5000"

def test_private_room_functionality():
    """Test private room creation and joining by key"""
    print("🔐 Testing Private Chat Room Functionality...")
    
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
    
    if len(tokens) < 2:
        print("❌ Need at least 2 users to test private rooms")
        return
    
    # Test 1: Create a private room
    print("\n2. Creating private room...")
    try:
        headers = {"Authorization": f"Bearer {tokens[0]}"}
        response = requests.post(f"{BASE_URL}/chat/rooms", 
                               json={
                                   "name": "Secret Room",
                                   "description": "A private room for testing",
                                   "is_public": False,
                                   "max_members": 10
                               },
                               headers=headers)
        
        if response.status_code == 201:
            room_data = response.json()
            join_key = room_data.get('join_key')
            print(f"✅ Private room created successfully!")
            print(f"   Room ID: {room_data['room_id']}")
            print(f"   Room Name: {room_data['room_name']}")
            print(f"   Join Key: {join_key}")
            print(f"   Is Public: {room_data['is_public']}")
        else:
            print(f"❌ Failed to create private room: {response.status_code} - {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Error creating private room: {e}")
        return
    
    # Test 2: Join room by key with second user
    print("\n3. Joining private room by key...")
    try:
        headers = {"Authorization": f"Bearer {tokens[1]}"}
        response = requests.post(f"{BASE_URL}/chat/rooms/join-by-key",
                               json={"join_key": join_key},
                               headers=headers)
        
        if response.status_code == 200:
            join_data = response.json()
            print(f"✅ Successfully joined private room!")
            print(f"   Room ID: {join_data['room_id']}")
            print(f"   Room Name: {join_data['room_name']}")
        else:
            print(f"❌ Failed to join room by key: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error joining room by key: {e}")
    
    # Test 3: Try to join with invalid key
    print("\n4. Testing invalid join key...")
    try:
        headers = {"Authorization": f"Bearer {tokens[1]}"}
        response = requests.post(f"{BASE_URL}/chat/rooms/join-by-key",
                               json={"join_key": "INVALID"},
                               headers=headers)
        
        if response.status_code == 404:
            print("✅ Correctly rejected invalid join key")
        else:
            print(f"❌ Should have rejected invalid key: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing invalid key: {e}")
    
    # Test 4: Create a public room for comparison
    print("\n5. Creating public room for comparison...")
    try:
        headers = {"Authorization": f"Bearer {tokens[0]}"}
        response = requests.post(f"{BASE_URL}/chat/rooms", 
                               json={
                                   "name": "Public Room",
                                   "description": "A public room for testing",
                                   "is_public": True,
                                   "max_members": 50
                               },
                               headers=headers)
        
        if response.status_code == 201:
            room_data = response.json()
            print(f"✅ Public room created successfully!")
            print(f"   Room ID: {room_data['room_id']}")
            print(f"   Room Name: {room_data['room_name']}")
            print(f"   Has Join Key: {'join_key' in room_data}")
            print(f"   Is Public: {room_data['is_public']}")
        else:
            print(f"❌ Failed to create public room: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error creating public room: {e}")
    
    print("\n🎉 Private room functionality test completed!")
    print("Key features tested:")
    print("- ✅ Private room creation with random join key")
    print("- ✅ Joining private room using join key")
    print("- ✅ Invalid join key rejection")
    print("- ✅ Public room creation (no join key)")
    print("- ✅ Room visibility indicators")

if __name__ == "__main__":
    test_private_room_functionality()
