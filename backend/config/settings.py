import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings:
    PROJECT_NAME: str = "MedicalRAG"
    
    # Storage
    UPLOAD_DIR: Path = BASE_DIR / "storage" / "records"
    DB_PATH: str = str(BASE_DIR / "storage" / "medicalrag.db")
    CHROMA_DB_DIR: str = str(BASE_DIR / "storage" / "chroma_db")
    
    # Gemini API
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    EMBEDDING_MODEL: str = "text-embedding-004"
    LLM_MODEL: str = "gemini-2.0-flash"
    
    # API Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8002
    
    # Security
    JWT_SECRET: str = os.getenv("JWT_SECRET", "super-secret-key-for-jwt-token-auth-99112")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  # HIPAA Session timeout constraint
    
    # AES PII Encryption Key (32 bytes)
    # Must be 16, 24, or 32 bytes long
    ENCRYPTION_KEY: bytes = os.getenv("PII_ENCRYPTION_KEY", "sixteenbytekey1234567890123456").encode()[:32]
    
    def __init__(self):
        # Create directories if they don't exist
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        Path(self.CHROMA_DB_DIR).mkdir(parents=True, exist_ok=True)

settings = Settings()
