#!/usr/bin/env python3
"""
Test script to verify TacticalLink messaging functionality
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:5000"

def test_messaging():
    """Test messaging functionality"""
    print("💬 Testing TacticalLink Messaging...")
    
    # Test users
    users = [
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
    user_ids = []
    
    # Create test users
    print("\n1. Creating test users...")
    for user_data in users:
        try:
            response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
            if response.status_code == 201:
                print(f"✅ Created user: {user_data['username']}")
                data = response.json()
                tokens.append(data['access_token'])
                user_ids.append(data['user_id'])
            else:
                print(f"❌ Failed to create user {user_data['username']}: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Error creating user {user_data['username']}: {e}")
    
    if len(tokens) < 2:
        print("❌ Need at least 2 users for messaging test")
        return
    
    alice_token = tokens[0]
    bob_token = tokens[1]
    alice_id = user_ids[0]
    bob_id = user_ids[1]
    
    # Test 1: Alice sends message to Bob
    print("\n2. Testing message sending...")
    try:
        headers = {"Authorization": f"Bearer {alice_token}"}
        message_data = {
            "recipient_id": bob_id,
            "message": "Hello Bob! This is a test message.",
            "self_destruct_time": 0,
            "read_once": False
        }
        response = requests.post(f"{BASE_URL}/chat/send", json=message_data, headers=headers)
        if response.status_code == 201:
            print("✅ Alice sent message to Bob")
            print(f"   Threat score: {response.json().get('threat_score', 'N/A')}")
        else:
            print(f"❌ Failed to send message: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error sending message: {e}")
    
    # Test 2: Bob receives message
    print("\n3. Testing message receiving...")
    try:
        headers = {"Authorization": f"Bearer {bob_token}"}
        response = requests.get(f"{BASE_URL}/chat/receive", headers=headers)
        if response.status_code == 200:
            messages = response.json()['messages']
            print(f"✅ Bob received {len(messages)} message(s)")
            for msg in messages:
                print(f"   - From: {msg['sender_id']}, Content: {msg['content'][:50]}...")
        else:
            print(f"❌ Failed to receive messages: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error receiving messages: {e}")
    
    # Test 3: Get conversation between Alice and Bob
    print("\n4. Testing conversation retrieval...")
    try:
        headers = {"Authorization": f"Bearer {alice_token}"}
        response = requests.get(f"{BASE_URL}/chat/conversation/{bob_id}", headers=headers)
        if response.status_code == 200:
            messages = response.json()['messages']
            print(f"✅ Alice can see {len(messages)} message(s) in conversation with Bob")
            for msg in messages:
                print(f"   - {msg['sender_id']} -> {msg['recipient_id']}: {msg['content'][:50]}...")
        else:
            print(f"❌ Failed to get conversation: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error getting conversation: {e}")
    
    # Test 4: Bob sends read-once message to Alice
    print("\n5. Testing read-once message...")
    try:
        headers = {"Authorization": f"Bearer {bob_token}"}
        message_data = {
            "recipient_id": alice_id,
            "message": "This is a read-once message that should disappear after reading.",
            "self_destruct_time": 0,
            "read_once": True
        }
        response = requests.post(f"{BASE_URL}/chat/send", json=message_data, headers=headers)
        if response.status_code == 201:
            print("✅ Bob sent read-once message to Alice")
        else:
            print(f"❌ Failed to send read-once message: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error sending read-once message: {e}")
    
    # Test 5: Alice receives and reads the read-once message
    print("\n6. Testing read-once message consumption...")
    try:
        headers = {"Authorization": f"Bearer {alice_token}"}
        response = requests.get(f"{BASE_URL}/chat/receive", headers=headers)
        if response.status_code == 200:
            messages = response.json()['messages']
            print(f"✅ Alice received {len(messages)} message(s)")
            for msg in messages:
                print(f"   - Content: {msg['content'][:50]}...")
                print(f"   - Read once: {msg['read_once']}")
        else:
            print(f"❌ Failed to receive messages: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error receiving messages: {e}")
    
    # Test 6: Verify read-once message is deleted
    print("\n7. Verifying read-once message deletion...")
    try:
        headers = {"Authorization": f"Bearer {alice_token}"}
        response = requests.get(f"{BASE_URL}/chat/receive", headers=headers)
        if response.status_code == 200:
            messages = response.json()['messages']
            print(f"✅ Alice now has {len(messages)} message(s) (read-once should be deleted)")
        else:
            print(f"❌ Failed to verify message deletion: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error verifying message deletion: {e}")
    
    print("\n🎉 Messaging test completed!")
    print("Check the chat interface to see if messages are working properly.")

if __name__ == "__main__":
    test_messaging()
