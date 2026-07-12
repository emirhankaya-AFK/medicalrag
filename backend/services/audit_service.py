import sqlite3
import re
from datetime import datetime
from typing import List, Dict, Any
from ..config.settings import settings

class AuditService:
    def __init__(self):
        self.db_path = settings.DB_PATH
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                user_role TEXT NOT NULL,
                action TEXT NOT NULL,
                accessed_resource TEXT,
                timestamp TEXT NOT NULL,
                details TEXT
            );
            """)
            conn.commit()

    def log_action(self, username: str, user_role: str, action: str, resource: str, details: str = ""):
        """
        Logs a user action with PII redaction on details.
        """
        redacted_details = self._redact_pii(details)
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO audit_logs (username, user_role, action, accessed_resource, timestamp, details) VALUES (?, ?, ?, ?, ?, ?);",
                (username, user_role, action, resource, timestamp, redacted_details)
            )
            conn.commit()

    def _redact_pii(self, text: str) -> str:
        if not text:
            return ""
        # Redact SSN pattern
        text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[REDACTED SSN]', text)
        # Redact DOB patterns like MM/DD/YYYY or YYYY-MM-DD
        text = re.sub(r'\b\d{2}/\d{2}/\d{4}\b', '[REDACTED DATE]', text)
        text = re.sub(r'\b\d{4}-\d{2}-\d{2}\b', '[REDACTED DATE]', text)
        # Redact phone numbers
        text = re.sub(r'\b\d{3}-\d{3}-\d{4}\b', '[REDACTED PHONE]', text)
        text = re.sub(r'\b\(\d{3}\)\s*\d{3}-\d{4}\b', '[REDACTED PHONE]', text)
        # Redact email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[REDACTED EMAIL]', text)
        return text

    def get_logs(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT 100;")
            return [dict(row) for row in cursor.fetchall()]

audit_service = AuditService()
