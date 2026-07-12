import sqlite3
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from ..config.settings import settings
from .encryption_service import encryption_service

class MedicalStorageService:
    def __init__(self):
        self.db_path = settings.DB_PATH
        # Ensure directories exist
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
            
            # Users Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL
            );
            """)

            # Patients Table (With PII encryption)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL, -- Encrypted
                dob TEXT,          -- Encrypted
                gender TEXT,
                ssn TEXT           -- Encrypted
            );
            """)

            # Medical Records Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS medical_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                upload_date TEXT NOT NULL,
                FOREIGN KEY (patient_id) REFERENCES patients (id) ON DELETE CASCADE
            );
            """)

            # Extractions Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS extractions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                record_id INTEGER NOT NULL,
                diagnoses TEXT, -- JSON
                medications TEXT, -- JSON
                lab_results TEXT, -- JSON
                vital_signs TEXT, -- JSON
                allergies TEXT, -- JSON
                insights TEXT, -- Clinical insights
                extraction_date TEXT NOT NULL,
                FOREIGN KEY (record_id) REFERENCES medical_records (id) ON DELETE CASCADE
            );
            """)
            conn.commit()
            
            # Seed an admin and doctor user if empty
            self._seed_users()

    def _seed_users(self):
        from .auth_service import auth_service
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users;")
            if cursor.fetchone()[0] == 0:
                # Seed default users
                doctor_hash = auth_service.hash_password("doctor123")
                nurse_hash = auth_service.hash_password("nurse123")
                patient_hash = auth_service.hash_password("patient123")
                admin_hash = auth_service.hash_password("admin123")
                
                cursor.executemany("""
                INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?);
                """, [
                    ("doctor", doctor_hash, "doctor"),
                    ("nurse", nurse_hash, "nurse"),
                    ("patient", patient_hash, "patient"),
                    ("admin", admin_hash, "admin")
                ])
                conn.commit()

    # --- User Operations ---
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?;", (username,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def add_user(self, username: str, password_hash: str, role: str) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?);",
                (username, password_hash, role)
            )
            user_id = cursor.lastrowid
            conn.commit()
            return user_id

    # --- Patient Operations (Encryption / Decryption wrapper) ---
    def add_patient(self, name: str, dob: str, gender: str, ssn: str) -> Dict[str, Any]:
        enc_name = encryption_service.encrypt(name)
        enc_dob = encryption_service.encrypt(dob)
        enc_ssn = encryption_service.encrypt(ssn)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO patients (name, dob, gender, ssn) VALUES (?, ?, ?, ?);",
                (enc_name, enc_dob, gender, enc_ssn)
            )
            patient_id = cursor.lastrowid
            conn.commit()
            return {"id": patient_id, "name": name, "dob": dob, "gender": gender, "ssn": ssn}

    def get_patient(self, patient_id: int) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM patients WHERE id = ?;", (patient_id,))
            row = cursor.fetchone()
            if not row:
                return None
            data = dict(row)
            # Decrypt sensitive fields
            data["name"] = encryption_service.decrypt(data["name"])
            data["dob"] = encryption_service.decrypt(data["dob"])
            data["ssn"] = encryption_service.decrypt(data["ssn"])
            return data

    def list_patients(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM patients;")
            results = []
            for row in cursor.fetchall():
                data = dict(row)
                data["name"] = encryption_service.decrypt(data["name"])
                data["dob"] = encryption_service.decrypt(data["dob"])
                data["ssn"] = encryption_service.decrypt(data["ssn"])
                results.append(data)
            return results

    # --- Medical Record Operations ---
    def save_file(self, file_content: bytes, filename: str) -> Path:
        target_path = settings.UPLOAD_DIR / filename
        if target_path.exists():
            stem = Path(filename).stem
            suffix = Path(filename).suffix
            filename = f"{stem}_{int(datetime.utcnow().timestamp())}{suffix}"
            target_path = settings.UPLOAD_DIR / filename

        with open(target_path, "wb") as f:
            f.write(file_content)
        return target_path

    def add_medical_record(self, patient_id: int, filename: str, file_path: str) -> Dict[str, Any]:
        upload_date = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO medical_records (patient_id, filename, file_path, upload_date) VALUES (?, ?, ?, ?);",
                (patient_id, filename, str(file_path), upload_date)
            )
            record_id = cursor.lastrowid
            conn.commit()
            return {"id": record_id, "patient_id": patient_id, "filename": filename, "file_path": str(file_path), "upload_date": upload_date}

    def get_medical_record(self, record_id: int) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM medical_records WHERE id = ?;", (record_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def list_medical_records(self, patient_id: Optional[int] = None) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if patient_id is not None:
                cursor.execute("SELECT * FROM medical_records WHERE patient_id = ? ORDER BY upload_date DESC;", (patient_id,))
            else:
                cursor.execute("SELECT * FROM medical_records ORDER BY upload_date DESC;")
            return [dict(row) for row in cursor.fetchall()]

    def delete_medical_record(self, record_id: int) -> bool:
        record = self.get_medical_record(record_id)
        if not record:
            return False
        
        file_path = Path(record["file_path"])
        if file_path.exists():
            file_path.unlink()

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM medical_records WHERE id = ?;", (record_id,))
            conn.commit()
            return True

    # --- Extraction Operations ---
    def add_extraction(self, record_id: int, diagnoses: str, medications: str, lab_results: str, vital_signs: str, allergies: str, insights: str) -> int:
        extraction_date = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM extractions WHERE record_id = ?;", (record_id,))
            cursor.execute("""
            INSERT INTO extractions (record_id, diagnoses, medications, lab_results, vital_signs, allergies, insights, extraction_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """, (record_id, diagnoses, medications, lab_results, vital_signs, allergies, insights, extraction_date))
            ext_id = cursor.lastrowid
            conn.commit()
            return ext_id

    def get_extraction(self, record_id: int) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM extractions WHERE record_id = ?;", (record_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

storage_service = MedicalStorageService()
