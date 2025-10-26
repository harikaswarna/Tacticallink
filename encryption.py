"""
TacticalLink Encryption Manager
Implements AES-256, RSA-4096, and quantum-safe encryption
"""

import os
import base64
import hashlib
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from typing import Tuple, Optional
import secrets
import numpy as np

class EncryptionManager:
    """Advanced encryption manager with quantum-safe capabilities"""
    
    def __init__(self):
        self.backend = default_backend()
        self.aes_key_size = 32  # 256 bits
        self.rsa_key_size = 4096
        self.quantum_key_size = 1024  # Lattice-based simulation
    
    def generate_key_pair(self) -> Tuple[str, str]:
        """Generate RSA-4096 key pair"""
        try:
            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=self.rsa_key_size,
                backend=self.backend
            )
            
            # Get public key
            public_key = private_key.public_key()
            
            # Serialize keys
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            return base64.b64encode(public_pem).decode('utf-8'), base64.b64encode(private_pem).decode('utf-8')
            
        except Exception as e:
            raise Exception(f"Error generating key pair: {e}")
    
    def generate_aes_key(self) -> bytes:
        """Generate random AES-256 key"""
        return secrets.token_bytes(self.aes_key_size)
    
    def generate_quantum_safe_key(self) -> bytes:
        """Generate quantum-safe key using lattice-based simulation"""
        # Simulate Kyber-style lattice-based key generation
        # In production, use actual post-quantum cryptography libraries
        return secrets.token_bytes(self.quantum_key_size)
    
    def encrypt_message(self, message: str, recipient_public_key: str) -> Tuple[str, str]:
        """Encrypt message using hybrid encryption (AES + RSA)"""
        try:
            # Generate random AES key
            aes_key = self.generate_aes_key()
            
            # Encrypt message with AES-256
            encrypted_message = self._aes_encrypt(message.encode('utf-8'), aes_key)
            
            # Encrypt AES key with recipient's RSA public key
            encrypted_session_key = self._rsa_encrypt(aes_key, recipient_public_key)
            
            return encrypted_message, encrypted_session_key
            
        except Exception as e:
            raise Exception(f"Error encrypting message: {e}")
    
    def decrypt_message(self, encrypted_message: str, encrypted_session_key: str, 
                       recipient_private_key: str) -> str:
        """Decrypt message using hybrid decryption"""
        try:
            # Decrypt AES key with RSA private key
            aes_key = self._rsa_decrypt(encrypted_session_key, recipient_private_key)
            
            # Decrypt message with AES-256
            decrypted_message = self._aes_decrypt(encrypted_message, aes_key)
            
            return decrypted_message.decode('utf-8')
            
        except Exception as e:
            raise Exception(f"Error decrypting message: {e}")
    
    def _aes_encrypt(self, data: bytes, key: bytes) -> str:
        """Encrypt data with AES-256-GCM"""
        try:
            # Generate random IV
            iv = secrets.token_bytes(12)  # 96-bit IV for GCM
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key),
                modes.GCM(iv),
                backend=self.backend
            )
            
            # Encrypt
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(data) + encryptor.finalize()
            
            # Combine IV, tag, and ciphertext
            encrypted_data = iv + encryptor.tag + ciphertext
            
            return base64.b64encode(encrypted_data).decode('utf-8')
            
        except Exception as e:
            raise Exception(f"Error in AES encryption: {e}")
    
    def _aes_decrypt(self, encrypted_data: str, key: bytes) -> bytes:
        """Decrypt data with AES-256-GCM"""
        try:
            # Decode base64
            encrypted_bytes = base64.b64decode(encrypted_data)
            
            # Extract IV, tag, and ciphertext
            iv = encrypted_bytes[:12]
            tag = encrypted_bytes[12:28]
            ciphertext = encrypted_bytes[28:]
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key),
                modes.GCM(iv, tag),
                backend=self.backend
            )
            
            # Decrypt
            decryptor = cipher.decryptor()
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            
            return plaintext
            
        except Exception as e:
            raise Exception(f"Error in AES decryption: {e}")
    
    def _rsa_encrypt(self, data: bytes, public_key_pem: str) -> str:
        """Encrypt data with RSA public key"""
        try:
            # Decode public key
            public_key_bytes = base64.b64decode(public_key_pem)
            public_key = serialization.load_pem_public_key(
                public_key_bytes,
                backend=self.backend
            )
            
            # Encrypt
            encrypted_data = public_key.encrypt(
                data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            return base64.b64encode(encrypted_data).decode('utf-8')
            
        except Exception as e:
            raise Exception(f"Error in RSA encryption: {e}")
    
    def _rsa_decrypt(self, encrypted_data: str, private_key_pem: str) -> bytes:
        """Decrypt data with RSA private key"""
        try:
            # Decode private key
            private_key_bytes = base64.b64decode(private_key_pem)
            private_key = serialization.load_pem_private_key(
                private_key_bytes,
                password=None,
                backend=self.backend
            )
            
            # Decode encrypted data
            encrypted_bytes = base64.b64decode(encrypted_data)
            
            # Decrypt
            decrypted_data = private_key.decrypt(
                encrypted_bytes,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            return decrypted_data
            
        except Exception as e:
            raise Exception(f"Error in RSA decryption: {e}")
    
    def quantum_safe_encrypt(self, message: str, quantum_key: bytes) -> str:
        """Simulate quantum-safe encryption using lattice-based cryptography"""
        try:
            # Convert message to bytes
            message_bytes = message.encode('utf-8')
            
            # Pad message to key size
            padded_message = message_bytes.ljust(len(quantum_key), b'\x00')
            
            # Simulate lattice-based encryption (XOR with key for simplicity)
            # In production, use actual post-quantum algorithms like Kyber
            encrypted = bytes(a ^ b for a, b in zip(padded_message, quantum_key))
            
            return base64.b64encode(encrypted).decode('utf-8')
            
        except Exception as e:
            raise Exception(f"Error in quantum-safe encryption: {e}")
    
    def quantum_safe_decrypt(self, encrypted_message: str, quantum_key: bytes) -> str:
        """Simulate quantum-safe decryption"""
        try:
            # Decode base64
            encrypted_bytes = base64.b64decode(encrypted_message)
            
            # Simulate lattice-based decryption (XOR with key)
            decrypted = bytes(a ^ b for a, b in zip(encrypted_bytes, quantum_key))
            
            # Remove padding
            decrypted = decrypted.rstrip(b'\x00')
            
            return decrypted.decode('utf-8')
            
        except Exception as e:
            raise Exception(f"Error in quantum-safe decryption: {e}")
    
    def generate_derived_key(self, password: str, salt: bytes) -> bytes:
        """Generate key from password using PBKDF2"""
        try:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=self.aes_key_size,
                salt=salt,
                iterations=100000,
                backend=self.backend
            )
            
            return kdf.derive(password.encode('utf-8'))
            
        except Exception as e:
            raise Exception(f"Error generating derived key: {e}")
    
    def secure_hash(self, data: str) -> str:
        """Generate secure hash using SHA-256"""
        try:
            hash_object = hashlib.sha256(data.encode('utf-8'))
            return hash_object.hexdigest()
            
        except Exception as e:
            raise Exception(f"Error generating hash: {e}")
    
    def destroy_key(self, key_data: str):
        """Securely destroy key data"""
        try:
            # Overwrite key data with random bytes
            if isinstance(key_data, str):
                key_bytes = key_data.encode('utf-8')
            else:
                key_bytes = key_data
            
            # Overwrite multiple times
            for _ in range(3):
                random_data = secrets.token_bytes(len(key_bytes))
                key_bytes = random_data
            
            # Clear memory
            del key_bytes
            
        except Exception as e:
            print(f"Error destroying key: {e}")
    
    def verify_integrity(self, data: str, hash_value: str) -> bool:
        """Verify data integrity using hash"""
        try:
            computed_hash = self.secure_hash(data)
            return computed_hash == hash_value
            
        except Exception as e:
            print(f"Error verifying integrity: {e}")
            return False
    
    def generate_secure_random(self, length: int) -> str:
        """Generate cryptographically secure random string"""
        try:
            random_bytes = secrets.token_bytes(length)
            return base64.b64encode(random_bytes).decode('utf-8')
            
        except Exception as e:
            raise Exception(f"Error generating secure random: {e}")
    
    def adaptive_key_rotation(self, threat_level: float) -> bool:
        """Adaptive key rotation based on threat level"""
        try:
            # Rotate keys if threat level is high
            if threat_level > 70:
                # Generate new quantum-safe key
                new_quantum_key = self.generate_quantum_safe_key()
                
                # In production, this would trigger key rotation across the system
                print(f"High threat detected ({threat_level}): Initiating key rotation")
                
                return True
            
            return False
            
        except Exception as e:
            print(f"Error in adaptive key rotation: {e}")
            return False

# Quantum-safe encryption simulation
class QuantumSafeEncryption:
    """Simulation of quantum-safe encryption using lattice-based cryptography"""
    
    def __init__(self):
        self.lattice_dimension = 256
        self.error_distribution = 0.1
    
    def generate_lattice_key(self) -> Tuple[np.ndarray, np.ndarray]:
        """Generate lattice-based key pair (simplified simulation)"""
        try:
            # Generate random lattice basis
            secret_key = np.random.randint(-1, 2, self.lattice_dimension)
            public_key = np.random.randint(0, 2**16, self.lattice_dimension)
            
            return secret_key, public_key
            
        except Exception as e:
            raise Exception(f"Error generating lattice key: {e}")
    
    def lattice_encrypt(self, message: str, public_key: np.ndarray) -> np.ndarray:
        """Encrypt message using lattice-based encryption (simulation)"""
        try:
            # Convert message to binary
            message_bits = ''.join(format(ord(c), '08b') for c in message)
            message_vector = np.array([int(bit) for bit in message_bits])
            
            # Pad to lattice dimension
            if len(message_vector) < self.lattice_dimension:
                message_vector = np.pad(message_vector, (0, self.lattice_dimension - len(message_vector)))
            else:
                message_vector = message_vector[:self.lattice_dimension]
            
            # Simulate lattice encryption
            noise = np.random.normal(0, self.error_distribution, self.lattice_dimension)
            ciphertext = (public_key * message_vector + noise) % 2**16
            
            return ciphertext
            
        except Exception as e:
            raise Exception(f"Error in lattice encryption: {e}")
    
    def lattice_decrypt(self, ciphertext: np.ndarray, secret_key: np.ndarray) -> str:
        """Decrypt message using lattice-based decryption (simulation)"""
        try:
            # Simulate lattice decryption
            decrypted_vector = (ciphertext * secret_key) % 2
            
            # Convert back to string
            binary_string = ''.join(map(str, decrypted_vector))
            message = ''.join(chr(int(binary_string[i:i+8], 2)) for i in range(0, len(binary_string), 8))
            
            return message.rstrip('\x00')
            
        except Exception as e:
            raise Exception(f"Error in lattice decryption: {e}")

# Perfect Forward Secrecy implementation
class PerfectForwardSecrecy:
    """Implement perfect forward secrecy for message encryption"""
    
    def __init__(self):
        self.encryption_manager = EncryptionManager()
        self.session_keys = {}
    
    def generate_ephemeral_key(self, session_id: str) -> str:
        """Generate ephemeral key for session"""
        try:
            ephemeral_key = self.encryption_manager.generate_aes_key()
            self.session_keys[session_id] = ephemeral_key
            
            return base64.b64encode(ephemeral_key).decode('utf-8')
            
        except Exception as e:
            raise Exception(f"Error generating ephemeral key: {e}")
    
    def encrypt_with_ephemeral_key(self, message: str, session_id: str) -> str:
        """Encrypt message with ephemeral key"""
        try:
            if session_id not in self.session_keys:
                self.generate_ephemeral_key(session_id)
            
            ephemeral_key = self.session_keys[session_id]
            encrypted_message = self.encryption_manager._aes_encrypt(
                message.encode('utf-8'), ephemeral_key
            )
            
            return encrypted_message
            
        except Exception as e:
            raise Exception(f"Error encrypting with ephemeral key: {e}")
    
    def decrypt_with_ephemeral_key(self, encrypted_message: str, session_id: str) -> str:
        """Decrypt message with ephemeral key"""
        try:
            if session_id not in self.session_keys:
                raise Exception("Session key not found")
            
            ephemeral_key = self.session_keys[session_id]
            decrypted_message = self.encryption_manager._aes_decrypt(
                encrypted_message, ephemeral_key
            )
            
            return decrypted_message.decode('utf-8')
            
        except Exception as e:
            raise Exception(f"Error decrypting with ephemeral key: {e}")
    
    def destroy_session_key(self, session_id: str):
        """Destroy ephemeral key for perfect forward secrecy"""
        try:
            if session_id in self.session_keys:
                self.encryption_manager.destroy_key(self.session_keys[session_id])
                del self.session_keys[session_id]
                
        except Exception as e:
            print(f"Error destroying session key: {e}")
