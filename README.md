# MedicalRAG - Secure Clinical Assistant

[English](README.md) | [Türkçe](README_TR.md)

MedicalRAG is a secure, HIPAA-conscious health records parser and question-answering assistant.

## Legal Disclaimer

> [!WARNING]
> MedicalRAG is designed as an administrative and analytical aid for healthcare professionals. It does NOT provide diagnostic services or generate clinical treatment plans. Always consult a licensed clinical practitioner for patient diagnostics and treatment.

## Setup Instructions

1. **Navigate to Project Directory**:
   ```bash
   cd medicalrag
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Configure API Key**:
   ```bash
   export GEMINI_API_KEY="your-gemini-api-key"
   ```
   *Note: If no API key is provided, the application automatically runs in Mock Mode.*

4. **Start the FastAPI Backend**:
   ```bash
   uvicorn backend.main:app --port 8002 --reload
   ```

5. **Start the Streamlit Frontend**:
   ```bash
   streamlit run frontend/app.py --server.port 8502
   ```

## Default Seeding Accounts
Use the following credentials on the login screen (`00_login`):
- **Doctor**: Username: `doctor` | Password: `doctor123`
- **Nurse**: Username: `nurse` | Password: `nurse123`
- **Patient**: Username: `patient` | Password: `patient123`
- **Admin**: Username: `admin` | Password: `admin123`

## Compliance & Security
- **Data Encryption**: Patient demographic fields name, DOB, and SSN are AES-256 encrypted at rest in the SQLite database.
- **Audit Trails**: Console queries and actions are saved with PII redaction. Visible under the admin console.
- **Access Limits**: API endpoints enforce in-memory rate limiting (max 10 requests per minute per user).
