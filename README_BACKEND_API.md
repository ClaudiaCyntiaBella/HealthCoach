# HealthCoach — Backend & API (Bagian Tiwi)

Paket ini merupakan implementasi bagian Backend & API: upload multi-foto,
validasi input, integrasi Gemini Vision, exact matching dataset nutrisi,
Gemini Recommendation, respons JSON, timeout, error handling, CORS, dan
pengamanan API key.

## Menjalankan di Windows

Dari root repository `HealthCoach-GitHub`:

```bat
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy HealthCoach\.env.example HealthCoach\.env
notepad HealthCoach\.env
py HealthCoach\manage.py migrate
py HealthCoach\manage.py runserver
```

Isi `GEMINI_API_KEY` pada `HealthCoach\.env`. Jangan pernah memasukkan file
`.env` atau API key asli ke GitHub.

Tes backend:

```bat
py HealthCoach\manage.py test api
```

Dokumentasi kontrak frontend terdapat pada `API_DOCUMENTATION.md`.

## PostgreSQL

Untuk memakai PostgreSQL, ubah bagian berikut pada `.env`:

```env
DB_ENGINE=postgresql
POSTGRES_DB=healthcoach_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password-lokal
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

Jangan menulis password database secara langsung di `settings.py`.

## Memasang ke repository tim

Salin isi paket ini ke root repository terbaru. Struktur utamanya akan menjadi:

```text
HealthCoach-GitHub/
├── requirements.txt
├── API_DOCUMENTATION.md
└── HealthCoach/
    ├── manage.py
    ├── .env.example
    ├── api/
    ├── config/
    └── data/
```

Sebelum commit, jalankan `git status`, `py HealthCoach\manage.py test api`, lalu
pastikan `.env` tidak muncul dalam daftar file yang akan di-commit.

