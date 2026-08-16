# MedicalRAG — Güvenli Klinik Asistan

[English](README.md) | [Türkçe](README_TR.md)

MedicalRAG, sağlık kayıtlarını ayrıştıran ve bu kayıtlar üzerinde soru-cevap yapılmasını sağlayan, güvenlik ve erişim kontrolüne odaklı bir yardımcı uygulamadır.

> [!WARNING]
> MedicalRAG yalnızca idari ve analitik destek amacıyla tasarlanmıştır. Tanı koymaz veya tedavi planı üretmez. Tanı ve tedavi için her zaman lisanslı bir sağlık uzmanına başvurun.

## Kurulum

```bash
pip install -r backend/requirements.txt
export GEMINI_API_KEY="gemini-api-anahtariniz"
uvicorn backend.main:app --port 8002 --reload
```

Başka bir terminalde:

```bash
streamlit run frontend/app.py --server.port 8502
```

API anahtarı yoksa uygulama örnek yanıt modunda çalışır.

## Güvenlik özellikleri

- Hasta kimlik alanlarında AES-256 ile depolama şifrelemesi
- Kişisel verileri maskeleyen denetim kayıtları
- Rol temelli erişim
- Kullanıcı başına dakikada 10 istek sınırı

Varsayılan geliştirme hesapları yalnızca yerel test içindir; gerçek dağıtım öncesinde tüm parolaları değiştirin.

