# Dokumentasi Backend & API HealthCoach

## Endpoint

### `GET /api/v1/health/`

Memeriksa apakah backend aktif.

Respons `200`:

```json
{
  "success": true,
  "status": "ok",
  "service": "HealthCoach API"
}
```

### `POST /api/v1/analyze/`

Menerima satu sampai lima foto dari beberapa sudut untuk satu makanan yang sama.

- Content-Type: `multipart/form-data`
- Field: `images` (boleh diulang)
- Format: JPG, JPEG, PNG, atau WEBP
- Batas bawaan: 5 MB per foto dan 20 MB total
- Field lama `image` tetap diterima sementara untuk kompatibilitas frontend.

Contoh Command Prompt Windows:

```bat
curl -X POST http://127.0.0.1:8000/api/v1/analyze/ ^
  -F "images=@D:\foto\makanan-depan.jpg" ^
  -F "images=@D:\foto\makanan-samping.jpg"
```

Respons berhasil `200`:

```json
{
  "success": true,
  "data": {
    "identification": {
      "food_name": "Nasi Goreng",
      "identification_status": "IDENTIFIED",
      "confidence": "tinggi",
      "ingredients": [],
      "notes": ""
    },
    "matching": {
      "normalized_name": "nasi goreng",
      "status": "MATCHED",
      "duplicate_count": 1
    },
    "nutrition": {
      "id": "773",
      "name": "Nasi Goreng",
      "calories": "276.0",
      "proteins": "3.2",
      "fat": "3.2",
      "carbohydrate": "30.2",
      "image": "..."
    },
    "recommendation": "Berdasarkan data nutrisi dataset HealthCoach, ...",
    "note": "..."
  },
  "meta": {
    "request_id": "uuid",
    "images_received": 2
  }
}
```

Respons error selalu konsisten:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Input tidak valid.",
    "details": {
      "images": ["Daftar ini tidak boleh kosong."]
    }
  }
}
```

Kode penting: `VALIDATION_ERROR`, `GEMINI_NOT_CONFIGURED`, `GEMINI_TIMEOUT`,
`GEMINI_INVALID_RESPONSE`, `GEMINI_UNAVAILABLE`, dan
`NUTRITION_DATA_UNAVAILABLE`.

## Alur proses

1. API memvalidasi jumlah, ukuran, ekstensi, MIME, dan isi foto.
2. Seluruh foto dikirim dalam satu permintaan Gemini Vision sebagai beberapa
   sudut dari makanan yang sama.
3. Nama hasil identifikasi dinormalisasi dan dicocokkan persis dengan dataset.
4. Angka nutrisi hanya diambil dari dataset, tidak dibuat oleh Gemini.
5. Jika cocok, data nutrisi dikirim ke Gemini Recommendation dan responsnya
   divalidasi agar angka dataset tidak berubah.
6. Hasil akhir dikirim sebagai JSON yang stabil untuk frontend.

## Catatan integrasi PostgreSQL

Versi ini menggunakan `CsvNutritionRepository` agar endpoint sudah dapat diuji
sebelum tabel PostgreSQL milik bagian Backend & Database selesai. Adapter
`DjangoNutritionRepository` juga sudah tersedia. Setelah Yuli menyediakan model
(misalnya `nutrition.Nutrition`) dengan field `name`, `name_normalized`,
`calories`, `proteins`, `fat`, `carbohydrate`, dan opsional `image`, ubah `.env`:

```env
NUTRITION_SOURCE=database
NUTRITION_MODEL=nutrition.Nutrition
```

Kontrak endpoint dan kode frontend tidak perlu berubah.

