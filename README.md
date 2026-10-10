# MedicalRAG - Secure Clinical Assistant

[English](#english) | [Türkçe](#türkçe) | [Deutsch](#deutsch)

## English
### Purpose
MedicalRAG is a secure, HIPAA‑conscious health records parser and question‑answering assistant.

### Verified Features
- Parses uploaded medical records and enables natural‑language questioning.
- Encrypts patient demographic fields (name, DOB, SSN) with AES‑256 at rest in SQLite.
- Maintains audit trails with PII redaction, viewable in the admin console.
- Enforces in‑memory rate limiting (max 10 requests per minute per user).
- Runs in Mock Mode when no GEMINI API key is provided.

### Stack
- **Backend:** Python, FastAPI
- **Frontend:** Python, Streamlit
- **Database:** SQLite
- **Encryption:** AES‑256
- **LLM:** Google Gemini (optional, via API key)

### Setup & Usage
```bash
# 1. Clone repository and navigate
git clone <repository-url>
cd medicalrag

# 2. Install dependencies
pip install -r backend/requirements.txt

# 3. Set API key (optional)
export GEMINI_API_KEY="your-gemini-api-key"

# 4. Start backend
uvicorn backend.main:app --port 8002 --reload

# 5. Start frontend
streamlit run frontend/app.py --server.port 8502
```
Default seeding accounts for the login page (`00_login`):
- Doctor: `doctor` / `doctor123`
- Nurse: `nurse` / `nurse123`
- Patient: `patient` / `patient123`
- Admin: `admin` / `admin123`

### Testing
Unit tests are located in the `tests/` directory (e.g., `test_auth.py`, `test_extraction.py`, `test_qa.py`).

### Limitations
- Not a diagnostic tool; does not generate clinical treatment plans.
- Intended as an administrative/analytical aid; always consult a licensed practitioner.
- Full LLM functionality requires a valid GEMINI API key; otherwise the app runs in Mock Mode.
- Rate limiting is applied to prevent abuse.

## Türkçe
### Amaç
MedicalRAG, HIPAA'ya uygun güvenli bir sağlık kayıtları ayrıştırıcı ve soru‑cevap asistanıdır.

### Doğrulanmış Özellikler
- Yüklenen tıbbi kayıtları ayrıştırır ve doğal dil ile soru‑cevap sağlar.
- Hasta demografik bilgileri (ad, doğum tarihi, SSN) AES‑256 ile şifrelenerek SQLite'de saklanır.
- PII'nin çıkarıldığı denetim izleri tutulur ve yönetim konsolunda görüntülenebilir.
- Kullanıcı başına dakikada maksimum 10 istek sınırlamasıyla bellek içi oran sınırlaması uygulanır.
- GEMINI API anahtarı sağlanmadığında Mock Mod'da çalışır.

### Yığın
- **Arka uç:** Python, FastAPI
- **Ön uç:** Python, Streamlit
- **Veritabanı:** SQLite
- **Şifreleme:** AES‑256
- **LLM:** Google Gemini (isteğe bağlı, API anahtarı üzerinden)

### Kurulum & Kullanım
```bash
# 1. Depoyu klonlayın ve dizine geçin
git clone <repository-url>
cd medicalrag

# 2. Bağımlılıkları yükleyin
pip install -r backend/requirements.txt

# 3. API anahtarını ayarlayın (isteğe bağlı)
export GEMINI_API_KEY="your-gemini-api-key"

# 4. Arka ucu başlatın
uvicorn backend.main:app --port 8002 --reload

# 5. Ön ucu başlatın
streamlit run frontend/app.py --server.port 8502
```
Giriş ekranı (`00_login`) için varsayılan hesaplar:
- Doktor: `doctor` / `doctor123`
- Hemşire: `nurse` / `nurse123`
- Hasta: `patient` / `patient123`
- Yönetici: `admin` / `admin123`

### Test
`tests/` dizininde birim testleri bulunur (ör. `test_auth.py`, `test_extraction.py`, `test_qa.py`).

### Sınırlamalar
- Tanı aracı değildir; klinik tedavi planı üretmez.
- Yönetim/analitik yardımcı aracıdır; her zaman lisanslı bir hekimdan danışın.
- Tam LLM işlevselliği geçerli bir GEMINI API anahtarı gerektirir; aksi takdirde uygulama Mock Mod'da çalışır.
- Kötüye kullanımı önlemek için oran sınırlaması uygulanır.

## Deutsch
### Zweck
MedicalRAG ist ein sicherer, HIPAA‑konformer Parser für Gesundheitsdatensätze und ein Frage‑Antwort‑Assistent.

### Verifizierte Funktionen
- Parsen hochgeladener medizinischer Datensätze und Beantwortung von Fragen in natürlicher Sprache.
- Verschlüsselung von Patientendemografie (Name, Geburtsdatum, SSN) mit AES‑256 im SQLite‑Datenspeicher im Ruhezustand.
- Führung von Audit‑Trails mit PII‑Redaktion, einsehbar in der Admin‑Konsole.
- Durchsetzung von In‑Memory‑Rate‑Limiting (max. 10 Anfragen pro Minute pro Benutzer).
- Im Mock‑Modus läuft die Anwendung, wenn kein GEMINI API‑Key angegeben ist.

### Stack
- **Backend:** Python, FastAPI
- **Frontend:** Python, Streamlit
- **Datenbank:** SQLite
- **Verschlüsselung:** AES‑256
- **LLM:** Google Gemini (optional, über API‑Key)

### Einrichtung & Nutzung
```bash
# 1. Repository klonen und wechseln
git clone <repository-url>
cd medicalrag

# 2. Abhängigkeiten installieren
pip install -r backend/requirements.txt

# 3. API‑Key setzen (optional)
export GEMINI_API_KEY="your-gemini-api-key"

# 4. Backend starten
uvicorn backend.main:app --port 8002 --reload

# 5. Frontend starten
streamlit run frontend/app.py --server.port 8502
```
Standard‑Anmeldedaten für die Login‑Seite (`00_login`):
- Arzt: `doctor` / `doctor123`
- Krankenschwester: `nurse` / `nurse123`
- Patient: `patient` / `patient123`
- Admin: `admin` / `admin123`

### Tests
Einheitstests befinden sich im `tests/`‑Verzeichnis (z. B. `test_auth.py`, `test_extraction.py`, `test_qa.py`).

### Einschränkungen
- Kein Diagnosetool; erzeugt keine klinischen Behandlungspläne.
- Dienlich als Verwaltungs‑/Analyse‑Assistenz; immer einen zugelassenen Arzt konsultieren.
- Vollständige LLM‑Funktionalität setzt einen gültigen GEMINI API‑Key voraus; ohne Schlüssel läuft die App im Mock‑Modus.
- Rate Limiting dient dem Missbrauchsschutz.
