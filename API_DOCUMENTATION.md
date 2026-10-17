# Dokumentasi Backend & API HealthCoach

Dokumentasi ini menjelaskan endpoint Backend & API HealthCoach, proses analisis makanan, integrasi Gemini AI, database nutrisi, serta panduan komunikasi antara frontend React/Vite dan backend Django REST Framework.

## 1. Endpoint API

### 1.1 GET /api/v1/health/

Endpoint untuk memeriksa apakah backend HealthCoach aktif dan dapat diakses.

**Method:** `GET`

**URL:**

`http://127.0.0.1:8000/api/v1/health/`

**Contoh respons berhasil (HTTP 200):**

```json
{
  "success": true,
  "status": "ok",
  "service": "HealthCoach API"
}
```

### 1.2 POST /api/v1/analyze/

Endpoint untuk menerima foto makanan, melakukan identifikasi menggunakan Gemini Vision, mencari data nutrisi, dan menghasilkan rekomendasi melalui Gemini AI.

**Method:** `POST`

**URL:**

`http://127.0.0.1:8000/api/v1/analyze/`

**Format permintaan:**

- Content-Type: `multipart/form-data`
- Nama field: `images`
- Jumlah foto: 1–5 foto
- Format foto: JPG, JPEG, PNG, atau WEBP
- Ukuran maksimal: 5 MB per foto
- Total maksimal: 20 MB
- Seluruh foto dalam satu permintaan harus menggambarkan makanan yang sama.
- Field lama `image` masih diterima sementara untuk kompatibilitas.

Batas tersebut merupakan pengaturan bawaan backend dan dapat disesuaikan melalui konfigurasi lingkungan.

**Contoh pengiriman menggunakan Command Prompt Windows:**

```bat
curl -X POST http://127.0.0.1:8000/api/v1/analyze/ ^
  -F "images=@D:\foto\makanan-depan.jpg" ^
  -F "images=@D:\foto\makanan-samping.jpg"
```

**Contoh respons berhasil (HTTP 200):**

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
    "recommendation": "Berdasarkan data nutrisi HealthCoach, ...",
    "note": "..."
  },
  "meta": {
    "request_id": "uuid",
    "images_received": 2
  }
}
```

**Catatan:** Data di atas merupakan contoh struktur respons. Nama makanan, nilai nutrisi, status identifikasi, dan rekomendasi aktual mengikuti hasil analisis serta data yang tersedia di sumber nutrisi.

Jika makanan tidak ditemukan pada database, status pencocokan dapat berupa `NOT_MATCHED` dan nilai `nutrition` dapat berupa `null`. Frontend harus menangani kondisi tersebut tanpa menampilkan angka nutrisi contoh.

## 2. Penanganan Error API

Backend HealthCoach menggunakan format respons error yang konsisten.

**Contoh respons error validasi (HTTP 400):**

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Input tidak valid.",
    "details": {
      "images": [
        "Daftar ini tidak boleh kosong."
      ]
    }
  }
}
```

Beberapa kode error yang perlu dikenali frontend:

- `VALIDATION_ERROR`: Data yang dikirim tidak sesuai ketentuan.
- `GEMINI_NOT_CONFIGURED`: Konfigurasi Gemini belum tersedia.
- `GEMINI_TIMEOUT`: Proses Gemini melebihi batas waktu.
- `GEMINI_INVALID_RESPONSE`: Respons Gemini tidak sesuai format yang diharapkan.
- `GEMINI_UNAVAILABLE`: Layanan Gemini tidak dapat digunakan.
- `NUTRITION_DATA_UNAVAILABLE`: Sumber data nutrisi mengalami masalah.

Frontend perlu menampilkan pesan error yang mudah dipahami pengguna dan menyediakan pilihan untuk mencoba kembali apabila diperlukan.

## 3. Alur Proses Analisis Makanan

Proses analisis makanan pada HealthCoach berjalan sebagai berikut:

1. Pengguna memilih satu atau beberapa foto makanan melalui frontend.
2. Frontend mengirim foto ke endpoint Django `/api/v1/analyze/`.
3. Backend melakukan validasi jumlah, ukuran, format, dan kelayakan file foto.
4. Foto dikirim ke Gemini Vision untuk mengidentifikasi nama makanan.
5. Nama makanan dinormalisasi dan dicocokkan dengan sumber data nutrisi.
6. Jika ditemukan kecocokan, data nutrisi diambil dari database atau sumber nutrisi yang dikonfigurasi.
7. Data nutrisi dikirim ke Gemini Recommendation untuk menghasilkan rekomendasi.
8. Backend menggabungkan identifikasi, hasil pencocokan, nutrisi, dan rekomendasi ke dalam respons JSON.
9. Frontend menerima JSON dan menampilkan hasil analisis kepada pengguna.

Angka nutrisi bersumber dari dataset atau database nutrisi HealthCoach, bukan dibuat secara bebas oleh Gemini.

## 4. Integrasi Database PostgreSQL

Backend HealthCoach mendukung dua sumber data nutrisi, yaitu CSV dan database PostgreSQL.

Pada pengembangan yang telah diuji bersama Yuli, backend berhasil menggunakan PostgreSQL melalui model Django:

`api.Nutrition`

Untuk menggunakan PostgreSQL sebagai sumber data nutrisi, konfigurasi pada file `HealthCoach/.env` adalah:

```env
DB_ENGINE=postgresql
NUTRITION_SOURCE=database
NUTRITION_MODEL=api.Nutrition
```

Informasi koneksi PostgreSQL, seperti nama database, host, username, port, dan password, juga dikonfigurasi melalui `.env`.

**Keamanan database:**

- Jangan menyimpan password database secara langsung pada `settings.py`.
- Jangan memasukkan file `.env` ke GitHub.
- Frontend tidak perlu terhubung langsung ke PostgreSQL.
- Semua akses data nutrisi dilakukan melalui backend Django.

Integrasi PostgreSQL telah berhasil diuji pada pengembangan backend. Pengujian akhir bersama frontend tetap diperlukan.

Migrasi database bersama harus dikoordinasikan dengan penanggung jawab database sebelum dijalankan.

## 5. Panduan Integrasi Frontend React/Vite

Frontend HealthCoach menggunakan React dengan Vite, sedangkan backend menggunakan Django REST Framework.

Pada lingkungan pengembangan lokal, alamat backend adalah:

`http://127.0.0.1:8000`

Endpoint analisis makanan:

`http://127.0.0.1:8000/api/v1/analyze/`

### 5.1 Mengirim Foto Menggunakan FormData

Frontend dapat mengirim foto menggunakan `FormData` dan fungsi `fetch()`.

Contoh fungsi integrasi:

```javascript
async function analyzeFood(files) {
  const formData = new FormData();

  files.forEach((file) => {
    formData.append("images", file);
  });

  const response = await fetch(
    "http://127.0.0.1:8000/api/v1/analyze/",
    {
      method: "POST",
      body: formData,
    }
  );

  const result = await response.json();

  if (!response.ok || !result.success) {
    throw new Error(
      result.error?.message ||
      "Analisis makanan gagal. Silakan coba lagi."
    );
  }

  return result.data;
}
```

**Catatan penting:**

- Nama field harus `images`, sesuai kontrak API Django.
- Setiap foto ditambahkan melalui `formData.append("images", file)`.
- Jangan mengatur header `Content-Type` secara manual ketika menggunakan `FormData`, karena browser akan menambahkan batas multipart secara otomatis.
- Frontend harus menangani kemungkinan gagal terhubung ke backend.

### 5.2 Membaca Hasil JSON

Frontend dapat mengambil informasi hasil analisis dari:

```javascript
const foodName = result.identification?.food_name;
const matchingStatus = result.matching?.status;
const nutrition = result.nutrition;
const recommendation = result.recommendation;
const note = result.note;
```

Contoh penggunaan data nutrisi:

```javascript
const calories = nutrition?.calories;
const proteins = nutrition?.proteins;
const carbohydrate = nutrition?.carbohydrate;
const fat = nutrition?.fat;
```

Apabila `nutrition` bernilai `null`, frontend sebaiknya menampilkan keterangan bahwa data nutrisi belum tersedia, bukan menggunakan nilai contoh.

### 5.3 Penyesuaian Validasi Upload

Berdasarkan pemeriksaan kode frontend `Analysis.jsx`, terdapat perbedaan aturan upload:

| Pengaturan | Frontend saat diperiksa | Backend |
|---|---|---|
| Jumlah maksimal foto | 3 foto | 5 foto |
| Ukuran maksimal per foto | 10 MB | 5 MB |
| Format | JPG, PNG, WEBP | JPG, PNG, WEBP |

Ketentuan frontend perlu disesuaikan bersama Clau agar tidak mengizinkan file yang melebihi batas backend.

Frontend boleh membatasi jumlah foto menjadi tiga apabila memang disepakati sebagai keputusan antarmuka, tetapi batas ukuran per foto tidak boleh melebihi batas yang diterapkan backend.

### 5.4 Loading dan Penanganan Error

Saat proses analisis berjalan, frontend perlu menampilkan indikator loading.

Setelah respons diterima:

- Jika berhasil, tampilkan nama makanan, informasi nutrisi yang tersedia, dan rekomendasi.
- Jika validasi gagal, tampilkan pesan kesalahan dari backend.
- Jika layanan Gemini mengalami masalah, tampilkan pesan error yang sesuai.
- Jika terjadi gangguan jaringan, tampilkan informasi bahwa backend tidak dapat dihubungi.
- Sediakan mekanisme untuk mencoba analisis kembali.

Pada kode frontend `Analysis.jsx` yang diperiksa, hasil analisis masih berupa data contoh dan proses loading masih menggunakan `setTimeout`.

Fungsi tersebut perlu diganti dengan pemanggilan API asli oleh bagian frontend.

## 6. Konfigurasi CORS

Backend Django telah menyediakan konfigurasi CORS untuk pengembangan frontend React/Vite, termasuk alamat berikut:

```text
http://localhost:3000
http://127.0.0.1:3000
http://localhost:5173
http://127.0.0.1:5173
```

Konfigurasi ini memungkinkan frontend pada alamat tersebut mengirim permintaan ke backend, selama server berjalan dan aturan CORS sesuai.

Jika frontend menggunakan alamat atau port lain, konfigurasi CORS perlu diperiksa kembali.

## 7. Pengujian Integrasi Backend dan Frontend

Pengujian integrasi dilakukan untuk memastikan seluruh proses berjalan dari frontend hingga hasil analisis ditampilkan.

Skenario pengujian meliputi:

1. Memastikan backend Django aktif melalui `/api/v1/health/`.
2. Membuka halaman analisis makanan pada frontend.
3. Memilih foto yang memenuhi aturan upload.
4. Mengirim foto melalui `POST /api/v1/analyze/`.
5. Memastikan frontend menerima respons JSON.
6. Memastikan nama makanan dan informasi nutrisi ditampilkan sesuai respons backend.
7. Memastikan rekomendasi Gemini ditampilkan apabila tersedia.
8. Menguji pesan error ketika foto tidak valid atau backend gagal memproses permintaan.
9. Memastikan loading berhenti setelah permintaan selesai.
10. Menguji kembali alur setelah terjadi kegagalan.

Pengujian backend secara terpisah telah dilakukan sebelumnya. Pengujian integrasi frontend dan backend masih perlu dilaksanakan bersama Clau.

## 8. Pembagian Tanggung Jawab Issue #55

**Tiwi — Backend & API**

- Menyiapkan dan memperbarui dokumentasi API.
- Menjelaskan format request dan response kepada frontend.
- Memastikan endpoint dapat digunakan oleh frontend.
- Membantu mengatasi kendala komunikasi API, validasi, atau CORS.
- Melakukan pengujian integrasi bersama Clau.

**Clau — Frontend**

- Menghubungkan tombol analisis ke API Django.
- Mengirim foto menggunakan `FormData`.
- Mengganti data contoh dengan hasil JSON dari backend.
- Menampilkan loading, hasil analisis, dan pesan error.
- Menguji tampilan hasil analisis bersama Tiwi.

Bagian database nutrisi dan layanan Gemini AI tetap ditangani sesuai pembagian tugas anggota tim.

## 9. Catatan Pengembangan

Dokumentasi ini menggambarkan kontrak API analisis makanan yang telah dikembangkan pada backend HealthCoach.

Integrasi React/Vite dan Django untuk Issue #55 masih memerlukan pengujian bersama sebelum dinyatakan selesai.

Fitur JWT dari Issue #54 dikembangkan melalui PR terpisah, sehingga penggunaannya pada integrasi frontend mengikuti status review dan penggabungan PR tersebut.

Jangan menjalankan migrasi database PostgreSQL bersama tanpa koordinasi dengan penanggung jawab database.