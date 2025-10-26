"""
TacticalLink Database Manager
MongoDB operations for users, messages, and threat logs
"""

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, ConnectionFailure
from bson import ObjectId
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv
from models import User, Message, ThreatLog, SessionKey, ChatRoom, GroupMessage

load_dotenv()

class Database:
    """MongoDB database manager for TacticalLink"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.connect()
        self.create_indexes()
    
    def connect(self):
        """Connect to MongoDB"""
        try:
            # Use Railway MongoDB URL or local fallback
            mongodb_url = os.getenv('MONGODB_URL', 'mongodb://localhost:27017/tactical_link')
            self.client = MongoClient(mongodb_url, serverSelectionTimeoutMS=5000)
            self.db = self.client.tactical_link
            
            # Test connection
            self.client.admin.command('ping')
            print("Connected to MongoDB successfully")
            
        except ConnectionFailure as e:
            print(f"Failed to connect to MongoDB: {e}")
            raise
    
    def create_indexes(self):
        """Create database indexes for performance"""
        try:
            # Users collection indexes
            self.db.users.create_index("username", unique=True)
            self.db.users.create_index("email", unique=True)
            self.db.users.create_index("created_at")
            
            # Messages collection indexes
            self.db.messages.create_index("sender_id")
            self.db.messages.create_index("recipient_id")
            self.db.messages.create_index("timestamp")
            self.db.messages.create_index("destruct_at")
            self.db.messages.create_index([("sender_id", 1), ("recipient_id", 1)])
            
            # Threat logs collection indexes
            self.db.threat_logs.create_index("user_id")
            self.db.threat_logs.create_index("timestamp")
            self.db.threat_logs.create_index("threat_score")
            
            # Session keys collection indexes
            self.db.session_keys.create_index("key_id", unique=True)
            self.db.session_keys.create_index("expires_at")
            
            # Chat rooms collection indexes
            self.db.chat_rooms.create_index("name", unique=True)
            self.db.chat_rooms.create_index("join_key", unique=True)
            self.db.chat_rooms.create_index("created_by")
            self.db.chat_rooms.create_index("is_active")
            
            # Group messages collection indexes
            self.db.group_messages.create_index("room_id")
            self.db.group_messages.create_index("sender_id")
            self.db.group_messages.create_index("timestamp")
            
            print("Database indexes created successfully")
            
        except Exception as e:
            print(f"Error creating indexes: {e}")
    
    # User operations
    def create_user(self, user: User) -> str:
        """Create a new user"""
        try:
            user_dict = user.to_dict()
            result = self.db.users.insert_one(user_dict)
            return str(result.inserted_id)
        except DuplicateKeyError:
            raise ValueError("Username or email already exists")
        except Exception as e:
            raise Exception(f"Error creating user: {e}")
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        try:
            user = self.db.users.find_one({"_id": ObjectId(user_id)})
            if user:
                user['_id'] = str(user['_id'])
            return user
        except Exception as e:
            print(f"Error getting user by ID: {e}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        try:
            user = self.db.users.find_one({"username": username})
            if user:
                user['_id'] = str(user['_id'])
            return user
        except Exception as e:
            print(f"Error getting user by username: {e}")
            return None
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user with username and password"""
        try:
            user = self.get_user_by_username(username)
            if not user:
                return None
            
            # Create User object to check password
            user_obj = User.from_dict(user)
            if user_obj.check_password(password):
                return user
            return None
            
        except Exception as e:
            print(f"Error authenticating user: {e}")
            return None
    
    def update_last_login(self, user_id: str):
        """Update user's last login timestamp"""
        try:
            self.db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"last_login": datetime.utcnow()}}
            )
        except Exception as e:
            print(f"Error updating last login: {e}")
    
    def get_all_users(self) -> List[Dict]:
        """Get all users (admin function)"""
        try:
            users = list(self.db.users.find({"is_active": True}))
            for user in users:
                user['_id'] = str(user['_id'])
                # Remove sensitive data
                user.pop('password_hash', None)
                user.pop('private_key', None)
            return users
        except Exception as e:
            print(f"Error getting all users: {e}")
            return []
    
    def get_total_users(self) -> int:
        """Get total number of active users"""
        try:
            return self.db.users.count_documents({"is_active": True})
        except Exception as e:
            print(f"Error getting total users: {e}")
            return 0
    
    def delete_user(self, user_id: str) -> bool:
        """Delete a user and all their data"""
        try:
            # Delete user
            result = self.db.users.delete_one({"_id": ObjectId(user_id)})
            
            # Delete user's messages
            self.db.messages.delete_many({
                "$or": [
                    {"sender_id": user_id},
                    {"recipient_id": user_id}
                ]
            })
            
            # Delete user's threat logs
            self.db.threat_logs.delete_many({"user_id": user_id})
            
            return result.deleted_count > 0
            
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False
    
    # Message operations
    def create_message(self, message: Message) -> str:
        """Create a new message"""
        try:
            message_dict = message.to_dict()
            result = self.db.messages.insert_one(message_dict)
            return str(result.inserted_id)
        except Exception as e:
            raise Exception(f"Error creating message: {e}")
    
    def get_message_by_id(self, message_id: str) -> Optional[Dict]:
        """Get message by ID"""
        try:
            message = self.db.messages.find_one({"_id": ObjectId(message_id)})
            if message:
                message['_id'] = str(message['_id'])
            return message
        except Exception as e:
            print(f"Error getting message by ID: {e}")
            return None
    
    def get_pending_messages(self, user_id: str) -> List[Dict]:
        """Get pending messages for a user"""
        try:
            messages = list(self.db.messages.find({
                "recipient_id": user_id,
                "is_read": False,
                "is_deleted": False,
                "$or": [
                    {"destruct_at": {"$gt": datetime.utcnow()}},
                    {"destruct_at": None}
                ]
            }).sort("timestamp", 1))
            
            for message in messages:
                message['_id'] = str(message['_id'])
            
            return messages
        except Exception as e:
            print(f"Error getting pending messages: {e}")
            return []
    
    def mark_message_as_read(self, message_id: str):
        """Mark message as read"""
        try:
            self.db.messages.update_one(
                {"_id": ObjectId(message_id)},
                {"$set": {"is_read": True}}
            )
        except Exception as e:
            print(f"Error marking message as read: {e}")
    
    def delete_message(self, message_id: str):
        """Delete a message"""
        try:
            self.db.messages.update_one(
                {"_id": ObjectId(message_id)},
                {"$set": {"is_deleted": True, "deleted_at": datetime.utcnow()}}
            )
        except Exception as e:
            print(f"Error deleting message: {e}")
    
    def get_user_recent_messages(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get user's recent messages for threat analysis"""
        try:
            messages = list(self.db.messages.find({
                "$or": [
                    {"sender_id": user_id},
                    {"recipient_id": user_id}
                ],
                "is_deleted": False
            }).sort("timestamp", -1).limit(limit))
            
            for message in messages:
                message['_id'] = str(message['_id'])
            
            return messages
        except Exception as e:
            print(f"Error getting user recent messages: {e}")
            return []
    
    def get_conversation_messages(self, user1_id: str, user2_id: str, limit: int = 100) -> List[Dict]:
        """Get conversation messages between two users"""
        try:
            messages = list(self.db.messages.find({
                "$or": [
                    {"sender_id": user1_id, "recipient_id": user2_id},
                    {"sender_id": user2_id, "recipient_id": user1_id}
                ],
                "is_deleted": False
            }).sort("timestamp", 1).limit(limit))
            
            for message in messages:
                message['_id'] = str(message['_id'])
            
            return messages
        except Exception as e:
            print(f"Error getting conversation messages: {e}")
            return []
    
    def get_message_statistics(self) -> Dict:
        """Get message statistics for admin dashboard"""
        try:
            total_messages = self.db.messages.count_documents({"is_deleted": False})
            messages_today = self.db.messages.count_documents({
                "timestamp": {"$gte": datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)},
                "is_deleted": False
            })
            
            # Get messages by hour for the last 24 hours
            hourly_stats = []
            for i in range(24):
                hour_start = datetime.utcnow() - timedelta(hours=i+1)
                hour_end = datetime.utcnow() - timedelta(hours=i)
                count = self.db.messages.count_documents({
                    "timestamp": {"$gte": hour_start, "$lt": hour_end},
                    "is_deleted": False
                })
                hourly_stats.append({
                    "hour": hour_start.hour,
                    "count": count
                })
            
            return {
                "total_messages": total_messages,
                "messages_today": messages_today,
                "hourly_stats": hourly_stats
            }
        except Exception as e:
            print(f"Error getting message statistics: {e}")
            return {"total_messages": 0, "messages_today": 0, "hourly_stats": []}
    
    # Threat log operations
    def create_threat_log(self, threat_log: ThreatLog) -> str:
        """Create a new threat log"""
        try:
            threat_dict = threat_log.to_dict()
            result = self.db.threat_logs.insert_one(threat_dict)
            return str(result.inserted_id)
        except Exception as e:
            raise Exception(f"Error creating threat log: {e}")
    
    def get_recent_threat_logs(self, limit: int = 20) -> List[Dict]:
        """Get recent threat logs"""
        try:
            threat_logs = list(self.db.threat_logs.find().sort("timestamp", -1).limit(limit))
            for log in threat_logs:
                log['_id'] = str(log['_id'])
            return threat_logs
        except Exception as e:
            print(f"Error getting recent threat logs: {e}")
            return []
    
    def get_user_threat_logs(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get threat logs for a specific user"""
        try:
            threat_logs = list(self.db.threat_logs.find({
                "user_id": user_id
            }).sort("timestamp", -1).limit(limit))
            
            for log in threat_logs:
                log['_id'] = str(log['_id'])
            
            return threat_logs
        except Exception as e:
            print(f"Error getting user threat logs: {e}")
            return []
    
    # Session key operations
    def create_session_key(self, session_key: SessionKey) -> str:
        """Create a new session key"""
        try:
            key_dict = session_key.to_dict()
            result = self.db.session_keys.insert_one(key_dict)
            return str(result.inserted_id)
        except Exception as e:
            raise Exception(f"Error creating session key: {e}")
    
    def get_session_key(self, key_id: str) -> Optional[Dict]:
        """Get session key by ID"""
        try:
            key = self.db.session_keys.find_one({"key_id": key_id})
            if key:
                key['_id'] = str(key['_id'])
            return key
        except Exception as e:
            print(f"Error getting session key: {e}")
            return None
    
    def destroy_session_key(self, key_id: str):
        """Mark session key as destroyed"""
        try:
            self.db.session_keys.update_one(
                {"key_id": key_id},
                {"$set": {"is_destroyed": True, "destroyed_at": datetime.utcnow()}}
            )
        except Exception as e:
            print(f"Error destroying session key: {e}")
    
    # Cleanup operations
    def cleanup_expired_messages(self):
        """Clean up expired self-destruct messages"""
        try:
            result = self.db.messages.update_many(
                {
                    "destruct_at": {"$lt": datetime.utcnow()},
                    "is_deleted": False
                },
                {"$set": {"is_deleted": True, "deleted_at": datetime.utcnow()}}
            )
            return result.modified_count
        except Exception as e:
            print(f"Error cleaning up expired messages: {e}")
            return 0
    
    def cleanup_expired_keys(self):
        """Clean up expired session keys"""
        try:
            result = self.db.session_keys.update_many(
                {
                    "expires_at": {"$lt": datetime.utcnow()},
                    "is_destroyed": False
                },
                {"$set": {"is_destroyed": True, "destroyed_at": datetime.utcnow()}}
            )
            return result.modified_count
        except Exception as e:
            print(f"Error cleaning up expired keys: {e}")
            return 0
    
    # Group chat operations
    def create_chat_room(self, room: ChatRoom) -> str:
        """Create a new chat room"""
        try:
            room_dict = room.to_dict()
            result = self.db.chat_rooms.insert_one(room_dict)
            return str(result.inserted_id)
        except Exception as e:
            raise Exception(f"Error creating chat room: {e}")
    
    def get_chat_room_by_id(self, room_id: str) -> Optional[Dict]:
        """Get chat room by ID"""
        try:
            room = self.db.chat_rooms.find_one({"_id": ObjectId(room_id)})
            if room:
                room['_id'] = str(room['_id'])
            return room
        except Exception as e:
            print(f"Error getting chat room by ID: {e}")
            return None
    
    def get_chat_room_by_name(self, name: str) -> Optional[Dict]:
        """Get chat room by name"""
        try:
            room = self.db.chat_rooms.find_one({"name": name})
            if room:
                room['_id'] = str(room['_id'])
            return room
        except Exception as e:
            print(f"Error getting chat room by name: {e}")
            return None
    
    def get_chat_room_by_join_key(self, join_key: str) -> Optional[Dict]:
        """Get chat room by join key"""
        try:
            room = self.db.chat_rooms.find_one({"join_key": join_key})
            if room:
                room['_id'] = str(room['_id'])
            return room
        except Exception as e:
            print(f"Error getting chat room by join key: {e}")
            return None
    
    def get_public_chat_rooms(self) -> List[Dict]:
        """Get all public chat rooms"""
        try:
            rooms = list(self.db.chat_rooms.find({
                "is_public": True,
                "is_active": True
            }).sort("created_at", -1))
            
            for room in rooms:
                room['_id'] = str(room['_id'])
            
            return rooms
        except Exception as e:
            print(f"Error getting public chat rooms: {e}")
            return []
    
    def get_user_chat_rooms(self, user_id: str) -> List[Dict]:
        """Get chat rooms where user is a member"""
        try:
            rooms = list(self.db.chat_rooms.find({
                "members": user_id,
                "is_active": True
            }).sort("created_at", -1))
            
            for room in rooms:
                room['_id'] = str(room['_id'])
            
            return rooms
        except Exception as e:
            print(f"Error getting user chat rooms: {e}")
            return []
    
    def join_chat_room(self, room_id: str, user_id: str) -> bool:
        """Add user to chat room"""
        try:
            room = self.get_chat_room_by_id(room_id)
            if not room:
                return False
            
            if len(room['members']) >= room['max_members']:
                return False
            
            if user_id not in room['members']:
                result = self.db.chat_rooms.update_one(
                    {"_id": ObjectId(room_id)},
                    {"$addToSet": {"members": user_id}}
                )
                return result.modified_count > 0
            
            return True
        except Exception as e:
            print(f"Error joining chat room: {e}")
            return False
    
    def leave_chat_room(self, room_id: str, user_id: str) -> bool:
        """Remove user from chat room"""
        try:
            result = self.db.chat_rooms.update_one(
                {"_id": ObjectId(room_id)},
                {"$pull": {"members": user_id}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error leaving chat room: {e}")
            return False
    
    def create_group_message(self, message: GroupMessage) -> str:
        """Create a new group message"""
        try:
            message_dict = message.to_dict()
            result = self.db.group_messages.insert_one(message_dict)
            return str(result.inserted_id)
        except Exception as e:
            raise Exception(f"Error creating group message: {e}")
    
    def get_room_messages(self, room_id: str, limit: int = 100) -> List[Dict]:
        """Get messages from a chat room"""
        try:
            messages = list(self.db.group_messages.find({
                "room_id": room_id,
                "is_deleted": False
            }).sort("timestamp", -1).limit(limit))
            
            for message in messages:
                message['_id'] = str(message['_id'])
            
            return messages
        except Exception as e:
            print(f"Error getting room messages: {e}")
            return []
    
    def delete_group_message(self, message_id: str) -> bool:
        """Delete a group message"""
        try:
            result = self.db.group_messages.update_one(
                {"_id": ObjectId(message_id)},
                {"$set": {"is_deleted": True, "deleted_at": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error deleting group message: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
