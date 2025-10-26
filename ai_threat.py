"""
TacticalLink AI Threat Detection
Implements machine learning models for anomaly detection and threat assessment
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import joblib
import os
import json
from collections import defaultdict, deque
import threading
import time

class ThreatDetector:
    """AI-powered threat detection using machine learning"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=10)
        self.is_trained = False
        self.model_path = 'models/threat_detection_model.pkl'
        self.scaler_path = 'models/scaler.pkl'
        self.pca_path = 'models/pca.pkl'
        
        # User behavior tracking
        self.user_behavior = defaultdict(lambda: {
            'message_frequency': deque(maxlen=100),
            'message_lengths': deque(maxlen=100),
            'time_patterns': deque(maxlen=100),
            'ip_addresses': set(),
            'last_activity': None,
            'suspicious_count': 0
        })
        
        # Global threat indicators
        self.global_threat_level = 0.0
        self.threat_history = deque(maxlen=1000)
        
        # Load or train model
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize or load the threat detection model"""
        try:
            # Create models directory if it doesn't exist
            os.makedirs('models', exist_ok=True)
            
            # Try to load existing model
            if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                self.pca = joblib.load(self.pca_path)
                self.is_trained = True
                print("Loaded existing threat detection model")
            else:
                # Train new model with synthetic data
                self._train_model_with_synthetic_data()
                
        except Exception as e:
            print(f"Error initializing model: {e}")
            self._train_model_with_synthetic_data()
    
    def _train_model_with_synthetic_data(self):
        """Train the model with synthetic data for initial deployment"""
        try:
            print("Training threat detection model with synthetic data...")
            
            # Generate synthetic training data
            normal_data = self._generate_normal_behavior_data(1000)
            anomalous_data = self._generate_anomalous_behavior_data(200)
            
            # Combine data
            X = np.vstack([normal_data, anomalous_data])
            y = np.hstack([np.ones(len(normal_data)), -np.ones(len(anomalous_data))])
            
            # Preprocess data
            X_scaled = self.scaler.fit_transform(X)
            X_pca = self.pca.fit_transform(X_scaled)
            
            # Train Isolation Forest
            self.model = IsolationForest(
                contamination=0.1,
                random_state=42,
                n_estimators=100
            )
            self.model.fit(X_pca)
            
            # Save models
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.scaler, self.scaler_path)
            joblib.dump(self.pca, self.pca_path)
            
            self.is_trained = True
            print("Threat detection model trained successfully")
            
        except Exception as e:
            print(f"Error training model: {e}")
            # Fallback to simple rule-based detection
            self.is_trained = False
    
    def _generate_normal_behavior_data(self, n_samples: int) -> np.ndarray:
        """Generate synthetic normal behavior data"""
        np.random.seed(42)
        
        # Normal behavior patterns
        data = []
        for _ in range(n_samples):
            # Message frequency (messages per hour)
            msg_freq = np.random.normal(5, 2)
            msg_freq = max(0, msg_freq)
            
            # Average message length
            avg_length = np.random.normal(50, 20)
            avg_length = max(10, avg_length)
            
            # Time pattern (hour of day)
            time_pattern = np.random.normal(12, 4)
            time_pattern = max(0, min(23, time_pattern))
            
            # Message length variance
            length_variance = np.random.normal(100, 50)
            length_variance = max(10, length_variance)
            
            # Response time (seconds)
            response_time = np.random.exponential(30)
            
            # Session duration (minutes)
            session_duration = np.random.normal(30, 15)
            session_duration = max(5, session_duration)
            
            # Number of unique recipients
            unique_recipients = np.random.poisson(3)
            unique_recipients = max(1, unique_recipients)
            
            # Login frequency (logins per day)
            login_freq = np.random.normal(2, 1)
            login_freq = max(0.5, login_freq)
            
            # Geographic consistency (simulated)
            geo_consistency = np.random.normal(0.8, 0.1)
            geo_consistency = max(0, min(1, geo_consistency))
            
            # Device consistency (simulated)
            device_consistency = np.random.normal(0.9, 0.05)
            device_consistency = max(0, min(1, device_consistency))
            
            data.append([
                msg_freq, avg_length, time_pattern, length_variance,
                response_time, session_duration, unique_recipients,
                login_freq, geo_consistency, device_consistency
            ])
        
        return np.array(data)
    
    def _generate_anomalous_behavior_data(self, n_samples: int) -> np.ndarray:
        """Generate synthetic anomalous behavior data"""
        np.random.seed(123)
        
        data = []
        for _ in range(n_samples):
            # Anomalous patterns
            anomaly_type = np.random.choice(['high_freq', 'unusual_time', 'bot_like', 'suspicious_content'])
            
            if anomaly_type == 'high_freq':
                # Extremely high message frequency
                msg_freq = np.random.normal(50, 10)
                avg_length = np.random.normal(20, 5)
                time_pattern = np.random.normal(12, 2)
                length_variance = np.random.normal(50, 10)
                response_time = np.random.exponential(1)
                session_duration = np.random.normal(5, 2)
                unique_recipients = np.random.poisson(20)
                login_freq = np.random.normal(10, 2)
                geo_consistency = np.random.normal(0.3, 0.1)
                device_consistency = np.random.normal(0.4, 0.1)
                
            elif anomaly_type == 'unusual_time':
                # Unusual time patterns
                msg_freq = np.random.normal(2, 1)
                avg_length = np.random.normal(100, 30)
                time_pattern = np.random.choice([2, 3, 4, 22, 23])  # Very early/late hours
                length_variance = np.random.normal(200, 50)
                response_time = np.random.exponential(300)
                session_duration = np.random.normal(120, 30)
                unique_recipients = np.random.poisson(1)
                login_freq = np.random.normal(0.5, 0.2)
                geo_consistency = np.random.normal(0.2, 0.1)
                device_consistency = np.random.normal(0.3, 0.1)
                
            elif anomaly_type == 'bot_like':
                # Bot-like behavior
                msg_freq = np.random.normal(30, 5)
                avg_length = np.random.normal(15, 3)
                time_pattern = np.random.normal(12, 1)
                length_variance = np.random.normal(10, 2)
                response_time = np.random.exponential(0.1)
                session_duration = np.random.normal(2, 0.5)
                unique_recipients = np.random.poisson(50)
                login_freq = np.random.normal(20, 5)
                geo_consistency = np.random.normal(0.1, 0.05)
                device_consistency = np.random.normal(0.95, 0.02)
                
            else:  # suspicious_content
                # Suspicious content patterns
                msg_freq = np.random.normal(8, 3)
                avg_length = np.random.normal(200, 50)
                time_pattern = np.random.normal(12, 3)
                length_variance = np.random.normal(500, 100)
                response_time = np.random.exponential(60)
                session_duration = np.random.normal(15, 5)
                unique_recipients = np.random.poisson(2)
                login_freq = np.random.normal(1, 0.5)
                geo_consistency = np.random.normal(0.4, 0.2)
                device_consistency = np.random.normal(0.6, 0.2)
            
            # Ensure positive values
            msg_freq = max(0, msg_freq)
            avg_length = max(5, avg_length)
            time_pattern = max(0, min(23, time_pattern))
            length_variance = max(5, length_variance)
            response_time = max(0.1, response_time)
            session_duration = max(1, session_duration)
            unique_recipients = max(1, unique_recipients)
            login_freq = max(0.1, login_freq)
            geo_consistency = max(0, min(1, geo_consistency))
            device_consistency = max(0, min(1, device_consistency))
            
            data.append([
                msg_freq, avg_length, time_pattern, length_variance,
                response_time, session_duration, unique_recipients,
                login_freq, geo_consistency, device_consistency
            ])
        
        return np.array(data)
    
    def analyze_message_metadata(self, sender_id: str, recipient_id: str, 
                               message_length: int, timestamp: datetime) -> float:
        """Analyze message metadata for threat detection"""
        try:
            # Update user behavior tracking
            self._update_user_behavior(sender_id, message_length, timestamp)
            
            # Extract features
            features = self._extract_features(sender_id, recipient_id, message_length, timestamp)
            
            if not self.is_trained:
                # Fallback to rule-based detection
                return self._rule_based_threat_score(features)
            
            # Use ML model for prediction
            features_scaled = self.scaler.transform([features])
            features_pca = self.pca.transform(features_scaled)
            
            # Get anomaly score
            anomaly_score = self.model.decision_function(features_pca)[0]
            
            # Convert to threat score (0-100)
            threat_score = max(0, min(100, (1 - anomaly_score) * 50))
            
            # Update global threat level
            self._update_global_threat_level(threat_score)
            
            return threat_score
            
        except Exception as e:
            print(f"Error analyzing message metadata: {e}")
            return 0.0
    
    def analyze_user_activity(self, user_id: str, messages: List[Dict]) -> float:
        """Analyze overall user activity for threat assessment"""
        try:
            if not messages:
                return 0.0
            
            # Calculate activity metrics
            total_messages = len(messages)
            avg_message_length = np.mean([len(msg.get('content', '')) for msg in messages])
            
            # Time analysis
            timestamps = [msg.get('timestamp', datetime.utcnow()) for msg in messages]
            time_variance = np.var([ts.hour for ts in timestamps if isinstance(ts, datetime)])
            
            # Recipient analysis
            unique_recipients = len(set([msg.get('recipient_id') for msg in messages]))
            
            # Frequency analysis
            if len(timestamps) > 1:
                time_diffs = [(timestamps[i] - timestamps[i-1]).total_seconds() 
                             for i in range(1, len(timestamps))]
                avg_frequency = np.mean(time_diffs) if time_diffs else 0
            else:
                avg_frequency = 0
            
            # Create feature vector
            features = [
                total_messages / 10,  # Normalize
                avg_message_length / 100,
                time_variance / 100,
                unique_recipients / 10,
                avg_frequency / 3600,  # Convert to hours
                0.8,  # Default geo consistency
                0.9,  # Default device consistency
                2.0,  # Default login frequency
                30.0,  # Default session duration
                100.0  # Default length variance
            ]
            
            if self.is_trained:
                features_scaled = self.scaler.transform([features])
                features_pca = self.pca.transform(features_scaled)
                anomaly_score = self.model.decision_function(features_pca)[0]
                threat_score = max(0, min(100, (1 - anomaly_score) * 50))
            else:
                threat_score = self._rule_based_threat_score(features)
            
            return threat_score
            
        except Exception as e:
            print(f"Error analyzing user activity: {e}")
            return 0.0
    
    def _update_user_behavior(self, user_id: str, message_length: int, timestamp: datetime):
        """Update user behavior tracking"""
        try:
            behavior = self.user_behavior[user_id]
            
            # Update message frequency (messages per hour)
            current_hour = timestamp.hour
            behavior['message_frequency'].append(current_hour)
            
            # Update message lengths
            behavior['message_lengths'].append(message_length)
            
            # Update time patterns
            behavior['time_patterns'].append(current_hour)
            
            # Update last activity
            behavior['last_activity'] = timestamp
            
        except Exception as e:
            print(f"Error updating user behavior: {e}")
    
    def _extract_features(self, sender_id: str, recipient_id: str, 
                         message_length: int, timestamp: datetime) -> List[float]:
        """Extract features for threat detection"""
        try:
            behavior = self.user_behavior[sender_id]
            
            # Message frequency (messages per hour)
            if len(behavior['message_frequency']) > 1:
                msg_freq = len(behavior['message_frequency']) / max(1, 
                    (timestamp - behavior['last_activity']).total_seconds() / 3600)
            else:
                msg_freq = 1.0
            
            # Average message length
            avg_length = np.mean(behavior['message_lengths']) if behavior['message_lengths'] else message_length
            
            # Time pattern (current hour)
            time_pattern = timestamp.hour
            
            # Message length variance
            length_variance = np.var(behavior['message_lengths']) if len(behavior['message_lengths']) > 1 else 0
            
            # Response time (simulated)
            response_time = 30.0  # Default response time
            
            # Session duration (simulated)
            session_duration = 30.0  # Default session duration
            
            # Number of unique recipients (simulated)
            unique_recipients = 3.0  # Default
            
            # Login frequency (simulated)
            login_freq = 2.0  # Default
            
            # Geographic consistency (simulated)
            geo_consistency = 0.8  # Default
            
            # Device consistency (simulated)
            device_consistency = 0.9  # Default
            
            return [
                msg_freq, avg_length, time_pattern, length_variance,
                response_time, session_duration, unique_recipients,
                login_freq, geo_consistency, device_consistency
            ]
            
        except Exception as e:
            print(f"Error extracting features: {e}")
            return [0.0] * 10
    
    def _rule_based_threat_score(self, features: List[float]) -> float:
        """Fallback rule-based threat scoring"""
        try:
            threat_score = 0.0
            
            msg_freq, avg_length, time_pattern, length_variance, response_time, \
            session_duration, unique_recipients, login_freq, geo_consistency, device_consistency = features
            
            # High message frequency
            if msg_freq > 20:
                threat_score += 30
            
            # Unusual time patterns (late night/early morning)
            if time_pattern < 5 or time_pattern > 22:
                threat_score += 20
            
            # Very short or very long messages
            if avg_length < 10 or avg_length > 500:
                threat_score += 15
            
            # High variance in message lengths
            if length_variance > 1000:
                threat_score += 10
            
            # Very fast response times (bot-like)
            if response_time < 1:
                threat_score += 25
            
            # Many unique recipients
            if unique_recipients > 10:
                threat_score += 20
            
            # Low geographic consistency
            if geo_consistency < 0.3:
                threat_score += 15
            
            # Low device consistency
            if device_consistency < 0.5:
                threat_score += 10
            
            return min(100, threat_score)
            
        except Exception as e:
            print(f"Error in rule-based threat scoring: {e}")
            return 0.0
    
    def _update_global_threat_level(self, threat_score: float):
        """Update global threat level"""
        try:
            self.threat_history.append(threat_score)
            
            # Calculate rolling average
            if len(self.threat_history) > 10:
                self.global_threat_level = np.mean(list(self.threat_history)[-10:])
            else:
                self.global_threat_level = np.mean(list(self.threat_history))
                
        except Exception as e:
            print(f"Error updating global threat level: {e}")
    
    def get_global_threat_level(self) -> float:
        """Get current global threat level"""
        return self.global_threat_level
    
    def get_user_threat_summary(self, user_id: str) -> Dict[str, Any]:
        """Get threat summary for a specific user"""
        try:
            behavior = self.user_behavior[user_id]
            
            return {
                'user_id': user_id,
                'message_count': len(behavior['message_frequency']),
                'avg_message_length': np.mean(behavior['message_lengths']) if behavior['message_lengths'] else 0,
                'suspicious_count': behavior['suspicious_count'],
                'last_activity': behavior['last_activity'].isoformat() if behavior['last_activity'] else None,
                'unique_ips': len(behavior['ip_addresses']),
                'threat_level': 'HIGH' if behavior['suspicious_count'] > 5 else 'MEDIUM' if behavior['suspicious_count'] > 2 else 'LOW'
            }
            
        except Exception as e:
            print(f"Error getting user threat summary: {e}")
            return {'user_id': user_id, 'threat_level': 'UNKNOWN'}
    
    def retrain_model(self, new_data: List[Dict]):
        """Retrain model with new data"""
        try:
            if not new_data:
                return False
            
            # Extract features from new data
            X_new = []
            for data_point in new_data:
                features = self._extract_features(
                    data_point['sender_id'],
                    data_point['recipient_id'],
                    data_point['message_length'],
                    data_point['timestamp']
                )
                X_new.append(features)
            
            X_new = np.array(X_new)
            
            # Combine with existing data
            if self.is_trained:
                # Load existing training data (simplified)
                X_existing = self._generate_normal_behavior_data(500)
                X_combined = np.vstack([X_existing, X_new])
            else:
                X_combined = X_new
            
            # Retrain model
            X_scaled = self.scaler.fit_transform(X_combined)
            X_pca = self.pca.fit_transform(X_scaled)
            
            self.model = IsolationForest(
                contamination=0.1,
                random_state=42,
                n_estimators=100
            )
            self.model.fit(X_pca)
            
            # Save updated model
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.scaler, self.scaler_path)
            joblib.dump(self.pca, self.pca_path)
            
            print("Model retrained successfully")
            return True
            
        except Exception as e:
            print(f"Error retraining model: {e}")
            return False
    
    def get_model_statistics(self) -> Dict[str, Any]:
        """Get model statistics and performance metrics"""
        try:
            return {
                'is_trained': self.is_trained,
                'model_type': 'Isolation Forest',
                'global_threat_level': self.global_threat_level,
                'total_threat_events': len(self.threat_history),
                'tracked_users': len(self.user_behavior),
                'model_accuracy': 'N/A (unsupervised)',
                'last_retrain': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"Error getting model statistics: {e}")
            return {'error': str(e)}
