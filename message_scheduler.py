"""
TacticalLink Message Scheduler
Handles self-destructing messages and automatic cleanup
"""

import threading
import time
import schedule
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import uuid
from database import Database
from encryption import EncryptionManager

class MessageScheduler:
    """Scheduler for self-destructing messages and cleanup tasks"""
    
    def __init__(self):
        self.db = Database()
        self.encryption_manager = EncryptionManager()
        self.scheduled_messages = {}
        self.running = False
        self.cleanup_thread = None
        self.scheduler_thread = None
        
        # Schedule cleanup tasks
        self._setup_cleanup_schedules()
    
    def _setup_cleanup_schedules(self):
        """Setup automatic cleanup schedules"""
        try:
            # Clean up expired messages every minute
            schedule.every().minute.do(self._cleanup_expired_messages)
            
            # Clean up expired session keys every 5 minutes
            schedule.every(5).minutes.do(self._cleanup_expired_keys)
            
            # Clean up old threat logs every hour
            schedule.every().hour.do(self._cleanup_old_threat_logs)
            
            # Clean up old system logs every day
            schedule.every().day.at("02:00").do(self._cleanup_old_system_logs)
            
            print("Cleanup schedules configured")
            
        except Exception as e:
            print(f"Error setting up cleanup schedules: {e}")
    
    def start(self):
        """Start the message scheduler"""
        try:
            if self.running:
                return
            
            self.running = True
            
            # Start scheduler thread
            self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self.scheduler_thread.start()
            
            # Start cleanup thread
            self.cleanup_thread = threading.Thread(target=self._run_cleanup, daemon=True)
            self.cleanup_thread.start()
            
            print("Message scheduler started")
            
        except Exception as e:
            print(f"Error starting message scheduler: {e}")
    
    def stop(self):
        """Stop the message scheduler"""
        try:
            self.running = False
            
            if self.scheduler_thread and self.scheduler_thread.is_alive():
                self.scheduler_thread.join(timeout=5)
            
            if self.cleanup_thread and self.cleanup_thread.is_alive():
                self.cleanup_thread.join(timeout=5)
            
            print("Message scheduler stopped")
            
        except Exception as e:
            print(f"Error stopping message scheduler: {e}")
    
    def schedule_destruction(self, message_id: str, destruct_time: int, read_once: bool = False):
        """Schedule message for self-destruction"""
        try:
            # Calculate destruction time
            destruct_at = datetime.utcnow() + timedelta(seconds=destruct_time)
            
            # Create destruction task
            destruction_task = {
                'message_id': message_id,
                'destruct_at': destruct_at,
                'read_once': read_once,
                'created_at': datetime.utcnow(),
                'status': 'scheduled'
            }
            
            # Store in memory for quick access
            self.scheduled_messages[message_id] = destruction_task
            
            # Update database
            from bson import ObjectId
            self.db.db.messages.update_one(
                {'_id': ObjectId(message_id)},
                {'$set': {'destruct_at': destruct_at}}
            )
            
            print(f"Scheduled message {message_id} for destruction at {destruct_at}")
            
        except Exception as e:
            print(f"Error scheduling message destruction: {e}")
    
    def cancel_destruction(self, message_id: str):
        """Cancel scheduled message destruction"""
        try:
            if message_id in self.scheduled_messages:
                del self.scheduled_messages[message_id]
            
            # Update database
            from bson import ObjectId
            self.db.db.messages.update_one(
                {'_id': ObjectId(message_id)},
                {'$unset': {'destruct_at': 1}}
            )
            
            print(f"Cancelled destruction for message {message_id}")
            
        except Exception as e:
            print(f"Error cancelling message destruction: {e}")
    
    def _run_scheduler(self):
        """Main scheduler loop"""
        try:
            while self.running:
                # Check for messages that need to be destroyed
                self._check_scheduled_destructions()
                
                # Run scheduled tasks
                schedule.run_pending()
                
                # Sleep for 1 second
                time.sleep(1)
                
        except Exception as e:
            print(f"Error in scheduler loop: {e}")
    
    def _run_cleanup(self):
        """Main cleanup loop"""
        try:
            while self.running:
                # Clean up expired messages
                self._cleanup_expired_messages()
                
                # Clean up expired keys
                self._cleanup_expired_keys()
                
                # Sleep for 30 seconds
                time.sleep(30)
                
        except Exception as e:
            print(f"Error in cleanup loop: {e}")
    
    def _check_scheduled_destructions(self):
        """Check for messages that need to be destroyed"""
        try:
            current_time = datetime.utcnow()
            messages_to_destroy = []
            
            # Check scheduled messages
            for message_id, task in self.scheduled_messages.items():
                if task['destruct_at'] <= current_time and task['status'] == 'scheduled':
                    messages_to_destroy.append(message_id)
            
            # Destroy messages
            for message_id in messages_to_destroy:
                self._destroy_message(message_id)
                
        except Exception as e:
            print(f"Error checking scheduled destructions: {e}")
    
    def _destroy_message(self, message_id: str):
        """Securely destroy a message"""
        try:
            # Get message from database
            message = self.db.get_message_by_id(message_id)
            if not message:
                print(f"Message {message_id} not found for destruction")
                return
            
            # Destroy encryption key
            if message.get('session_key'):
                self.encryption_manager.destroy_key(message['session_key'])
            
            # Mark message as deleted in database
            self.db.delete_message(message_id)
            
            # Remove from scheduled messages
            if message_id in self.scheduled_messages:
                self.scheduled_messages[message_id]['status'] = 'destroyed'
                del self.scheduled_messages[message_id]
            
            # Log destruction
            self._log_message_destruction(message_id, message)
            
            print(f"Message {message_id} destroyed successfully")
            
        except Exception as e:
            print(f"Error destroying message {message_id}: {e}")
    
    def _log_message_destruction(self, message_id: str, message: Dict):
        """Log message destruction event"""
        try:
            log_entry = {
                'event_type': 'message_destruction',
                'message_id': message_id,
                'sender_id': message.get('sender_id'),
                'recipient_id': message.get('recipient_id'),
                'destruction_reason': 'scheduled_self_destruct',
                'timestamp': datetime.utcnow(),
                'metadata': {
                    'self_destruct_time': message.get('self_destruct_time'),
                    'read_once': message.get('read_once'),
                    'message_length': len(message.get('content', ''))
                }
            }
            
            # Store in system logs collection
            self.db.db.system_logs.insert_one(log_entry)
            
        except Exception as e:
            print(f"Error logging message destruction: {e}")
    
    def _cleanup_expired_messages(self):
        """Clean up expired self-destruct messages"""
        try:
            current_time = datetime.utcnow()
            
            # Find expired messages
            expired_messages = list(self.db.db.messages.find({
                'destruct_at': {'$lt': current_time},
                'is_deleted': False
            }))
            
            destroyed_count = 0
            for message in expired_messages:
                try:
                    # Destroy encryption key
                    if message.get('session_key'):
                        self.encryption_manager.destroy_key(message['session_key'])
                    
                    # Mark as deleted
                    self.db.db.messages.update_one(
                        {'_id': message['_id']},
                        {'$set': {'is_deleted': True, 'deleted_at': current_time}}
                    )
                    
                    # Log destruction
                    self._log_message_destruction(str(message['_id']), message)
                    
                    destroyed_count += 1
                    
                except Exception as e:
                    print(f"Error destroying expired message {message['_id']}: {e}")
            
            if destroyed_count > 0:
                print(f"Cleaned up {destroyed_count} expired messages")
                
        except Exception as e:
            print(f"Error cleaning up expired messages: {e}")
    
    def _cleanup_expired_keys(self):
        """Clean up expired session keys"""
        try:
            current_time = datetime.utcnow()
            
            # Find expired keys
            expired_keys = list(self.db.db.session_keys.find({
                'expires_at': {'$lt': current_time},
                'is_destroyed': False
            }))
            
            destroyed_count = 0
            for key in expired_keys:
                try:
                    # Mark as destroyed
                    self.db.db.session_keys.update_one(
                        {'_id': key['_id']},
                        {'$set': {'is_destroyed': True, 'destroyed_at': current_time}}
                    )
                    
                    destroyed_count += 1
                    
                except Exception as e:
                    print(f"Error destroying expired key {key['_id']}: {e}")
            
            if destroyed_count > 0:
                print(f"Cleaned up {destroyed_count} expired session keys")
                
        except Exception as e:
            print(f"Error cleaning up expired keys: {e}")
    
    def _cleanup_old_threat_logs(self):
        """Clean up old threat logs (older than 30 days)"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            
            result = self.db.db.threat_logs.delete_many({
                'timestamp': {'$lt': cutoff_date},
                'is_resolved': True
            })
            
            if result.deleted_count > 0:
                print(f"Cleaned up {result.deleted_count} old threat logs")
                
        except Exception as e:
            print(f"Error cleaning up old threat logs: {e}")
    
    def _cleanup_old_system_logs(self):
        """Clean up old system logs (older than 7 days)"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=7)
            
            result = self.db.db.system_logs.delete_many({
                'timestamp': {'$lt': cutoff_date}
            })
            
            if result.deleted_count > 0:
                print(f"Cleaned up {result.deleted_count} old system logs")
                
        except Exception as e:
            print(f"Error cleaning up old system logs: {e}")
    
    def get_scheduled_messages(self) -> List[Dict]:
        """Get list of scheduled messages"""
        try:
            scheduled = []
            for message_id, task in self.scheduled_messages.items():
                scheduled.append({
                    'message_id': message_id,
                    'destruct_at': task['destruct_at'].isoformat(),
                    'read_once': task['read_once'],
                    'status': task['status'],
                    'created_at': task['created_at'].isoformat()
                })
            
            return scheduled
            
        except Exception as e:
            print(f"Error getting scheduled messages: {e}")
            return []
    
    def get_cleanup_statistics(self) -> Dict:
        """Get cleanup statistics"""
        try:
            current_time = datetime.utcnow()
            
            # Count expired messages
            expired_messages = self.db.db.messages.count_documents({
                'destruct_at': {'$lt': current_time},
                'is_deleted': False
            })
            
            # Count expired keys
            expired_keys = self.db.db.session_keys.count_documents({
                'expires_at': {'$lt': current_time},
                'is_destroyed': False
            })
            
            # Count scheduled messages
            scheduled_count = len(self.scheduled_messages)
            
            return {
                'expired_messages': expired_messages,
                'expired_keys': expired_keys,
                'scheduled_messages': scheduled_count,
                'last_cleanup': current_time.isoformat(),
                'scheduler_running': self.running
            }
            
        except Exception as e:
            print(f"Error getting cleanup statistics: {e}")
            return {'error': str(e)}
    
    def force_cleanup(self):
        """Force immediate cleanup of all expired items"""
        try:
            print("Starting forced cleanup...")
            
            # Clean up expired messages
            self._cleanup_expired_messages()
            
            # Clean up expired keys
            self._cleanup_expired_keys()
            
            # Clean up old logs
            self._cleanup_old_threat_logs()
            self._cleanup_old_system_logs()
            
            print("Forced cleanup completed")
            
        except Exception as e:
            print(f"Error in forced cleanup: {e}")
    
    def schedule_bulk_destruction(self, message_ids: List[str], destruct_time: int):
        """Schedule multiple messages for destruction"""
        try:
            for message_id in message_ids:
                self.schedule_destruction(message_id, destruct_time)
            
            print(f"Scheduled {len(message_ids)} messages for destruction")
            
        except Exception as e:
            print(f"Error scheduling bulk destruction: {e}")
    
    def get_destruction_queue(self) -> List[Dict]:
        """Get messages in destruction queue"""
        try:
            current_time = datetime.utcnow()
            
            # Get messages scheduled for destruction
            queued_messages = list(self.db.db.messages.find({
                'destruct_at': {'$gt': current_time},
                'is_deleted': False
            }).sort('destruct_at', 1))
            
            queue = []
            for message in queued_messages:
                queue.append({
                    'message_id': str(message['_id']),
                    'sender_id': message['sender_id'],
                    'recipient_id': message['recipient_id'],
                    'destruct_at': message['destruct_at'].isoformat(),
                    'time_remaining': (message['destruct_at'] - current_time).total_seconds(),
                    'read_once': message.get('read_once', False)
                })
            
            return queue
            
        except Exception as e:
            print(f"Error getting destruction queue: {e}")
            return []
