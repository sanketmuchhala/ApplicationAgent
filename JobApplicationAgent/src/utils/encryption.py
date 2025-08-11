import os
import json
import base64
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class EncryptionManager:
    """Manages encryption and decryption of sensitive data"""
    
    def __init__(self, password: Optional[str] = None):
        self.password = password or os.getenv('ENCRYPTION_KEY', self._generate_default_key())
        self._cipher_suite = None
    
    def _generate_default_key(self) -> str:
        """Generate a default encryption key"""
        # In production, this should be provided by user or generated securely
        return "default_job_agent_key_please_change_in_production"
    
    def _get_cipher_suite(self) -> Fernet:
        """Get or create cipher suite"""
        if self._cipher_suite is None:
            # Derive key from password
            password_bytes = self.password.encode()
            salt = b'job_agent_salt_2024'  # In production, use random salt per encryption
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            
            key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
            self._cipher_suite = Fernet(key)
        
        return self._cipher_suite
    
    def encrypt_data(self, data: Dict[str, Any]) -> str:
        """Encrypt dictionary data to base64 string"""
        try:
            # Convert data to JSON string
            json_string = json.dumps(data, default=str)
            json_bytes = json_string.encode()
            
            # Encrypt the data
            cipher_suite = self._get_cipher_suite()
            encrypted_data = cipher_suite.encrypt(json_bytes)
            
            # Return as base64 string for storage
            return base64.urlsafe_b64encode(encrypted_data).decode()
            
        except Exception as e:
            raise Exception(f"Encryption failed: {str(e)}")
    
    def decrypt_data(self, encrypted_string: str) -> Dict[str, Any]:
        """Decrypt base64 string to dictionary data"""
        try:
            # Decode from base64
            encrypted_data = base64.urlsafe_b64decode(encrypted_string.encode())
            
            # Decrypt the data
            cipher_suite = self._get_cipher_suite()
            decrypted_bytes = cipher_suite.decrypt(encrypted_data)
            
            # Convert back to dictionary
            json_string = decrypted_bytes.decode()
            return json.loads(json_string)
            
        except Exception as e:
            raise Exception(f"Decryption failed: {str(e)}")
    
    def encrypt_string(self, text: str) -> str:
        """Encrypt a string"""
        try:
            text_bytes = text.encode()
            cipher_suite = self._get_cipher_suite()
            encrypted_data = cipher_suite.encrypt(text_bytes)
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            raise Exception(f"String encryption failed: {str(e)}")
    
    def decrypt_string(self, encrypted_string: str) -> str:
        """Decrypt a string"""
        try:
            encrypted_data = base64.urlsafe_b64decode(encrypted_string.encode())
            cipher_suite = self._get_cipher_suite()
            decrypted_bytes = cipher_suite.decrypt(encrypted_data)
            return decrypted_bytes.decode()
        except Exception as e:
            raise Exception(f"String decryption failed: {str(e)}")
    
    def is_encrypted(self, data_string: str) -> bool:
        """Check if a string appears to be encrypted data"""
        try:
            # Try to decode as base64
            decoded = base64.urlsafe_b64decode(data_string.encode())
            
            # Check if it looks like Fernet encrypted data (starts with version bytes)
            return len(decoded) > 10 and decoded[0] in [0x80, 0x81, 0x82]
        except Exception:
            return False
    
    def encrypt_sensitive_fields(self, data: Dict[str, Any], sensitive_fields: list) -> Dict[str, Any]:
        """Encrypt only specified sensitive fields in a dictionary"""
        encrypted_data = data.copy()
        
        for field_path in sensitive_fields:
            # Handle nested field paths like 'contact.email'
            keys = field_path.split('.')
            current = encrypted_data
            
            # Navigate to parent of target field
            for key in keys[:-1]:
                if key in current and isinstance(current[key], dict):
                    current = current[key]
                else:
                    break
            else:
                # Encrypt the target field if it exists
                final_key = keys[-1]
                if final_key in current and current[final_key] is not None:
                    original_value = str(current[final_key])
                    encrypted_value = self.encrypt_string(original_value)
                    current[final_key] = f"ENCRYPTED:{encrypted_value}"
        
        return encrypted_data
    
    def decrypt_sensitive_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt fields that were encrypted with encrypt_sensitive_fields"""
        decrypted_data = data.copy()
        
        def decrypt_recursive(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if isinstance(value, str) and value.startswith("ENCRYPTED:"):
                        try:
                            encrypted_part = value[10:]  # Remove "ENCRYPTED:" prefix
                            decrypted_value = self.decrypt_string(encrypted_part)
                            obj[key] = decrypted_value
                        except Exception as e:
                            print(f"Warning: Could not decrypt field {key}: {str(e)}")
                    elif isinstance(value, (dict, list)):
                        decrypt_recursive(value)
            elif isinstance(obj, list):
                for item in obj:
                    decrypt_recursive(item)
        
        decrypt_recursive(decrypted_data)
        return decrypted_data
    
    @staticmethod
    def generate_new_key() -> str:
        """Generate a new encryption key"""
        return Fernet.generate_key().decode()
    
    def change_password(self, new_password: str):
        """Change encryption password"""
        self.password = new_password
        self._cipher_suite = None  # Force recreation with new password
    
    def verify_password(self, test_data: str = "test") -> bool:
        """Verify that the current password can encrypt/decrypt"""
        try:
            encrypted = self.encrypt_string(test_data)
            decrypted = self.decrypt_string(encrypted)
            return decrypted == test_data
        except Exception:
            return False