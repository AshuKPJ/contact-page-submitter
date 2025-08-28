# app/core/encryption.py

from cryptography.fernet import Fernet
from app.core.config import settings
import base64


class EncryptionService:
    def __init__(self):
        # Use the key from settings or generate one
        key = settings.CAPTCHA_ENCRYPTION_KEY
        if len(key) < 32:
            # Pad the key to 32 bytes if it's too short
            key = key.ljust(32, "0")
        # Convert to bytes and create base64 encoded key for Fernet
        key_bytes = key[:32].encode()
        self.cipher = Fernet(base64.urlsafe_b64encode(key_bytes))

    def encrypt(self, data: str) -> str:
        """Encrypt a string"""
        return self.cipher.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt a string"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()


# Create a singleton instance
encryption_service = EncryptionService()
