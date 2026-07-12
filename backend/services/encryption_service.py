from Crypto.Cipher import AES
import base64
from ..config.settings import settings

class EncryptionService:
    def __init__(self):
        # AES key must be 16, 24, or 32 bytes.
        self.key = settings.ENCRYPTION_KEY
        
    def encrypt(self, plain_text: str) -> str:
        """
        Encrypts plain text using AES CFB mode.
        Returns a base64 encoded string containing IV + encrypted payload.
        """
        if not plain_text:
            return ""
        cipher = AES.new(self.key, AES.MODE_CFB)
        iv = cipher.iv
        encrypted_bytes = cipher.encrypt(plain_text.encode('utf-8'))
        # Concat IV and ciphertext, encode to base64 string
        return base64.b64encode(iv + encrypted_bytes).decode('utf-8')

    def decrypt(self, encrypted_text: str) -> str:
        """
        Decrypts base64 encoded AES CFB payload.
        """
        if not encrypted_text:
            return ""
        try:
            raw_data = base64.b64decode(encrypted_text.encode('utf-8'))
            iv = raw_data[:16]
            ciphertext = raw_data[16:]
            cipher = AES.new(self.key, AES.MODE_CFB, iv=iv)
            decrypted_bytes = cipher.decrypt(ciphertext)
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            print(f"Decryption failed: {e}")
            return "[DECRYPTION_ERROR]"

encryption_service = EncryptionService()
