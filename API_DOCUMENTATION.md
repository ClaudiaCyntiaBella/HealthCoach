# Dokumentasi Backend & API HealthCoach

Dokumentasi ini menjelaskan endpoint Backend & API HealthCoach, analisis makanan melalui Gemini AI dan repository nutrisi, autentikasi JWT, profil akun dan profil kesehatan pengguna, penyimpanan riwayat analisis, serta panduan integrasi frontend dengan Django REST Framework.

**Pembaruan dokumentasi:** 7 November 2026
**Base URL pengembangan lokal:** `http://127.0.0.1:8000/api/v1/`

**Lingkup pekerjaan:** Backend & API (Tiwi). Model, migrasi, dashboard Django, dan koneksi database dikelola Yuli; logika Gemini dan rekomendasi dikelola Aril; frontend dikelola Clau.

Contoh request dan respons di bawah bersifat ilustratif kecuali hasil pengujian yang dinyatakan secara khusus. Perilaku aktual mengikuti kode dan konfigurasi environment yang aktif. Jangan memasukkan password, API key, atau token asli ke dokumentasi.

---

## 1. Daftar Endpoint API

Semua path berikut berada di bawah prefix `/api/v1/`.

| Method | Endpoint | Perlu access token? | Fungsi |
|---|---|---|---|
| GET | `health/` | Tidak | Memeriksa status backend |
| POST | `analyze/` | Opsional | Menganalisis foto; menyimpan riwayat jika login |
| POST | `auth/register/` | Tidak | Mendaftarkan akun pengguna |
| POST | `auth/login/` | Tidak | Mendapatkan pasangan token JWT |
| POST | `auth/refresh/` | Tidak; perlu refresh token | Mendapatkan access token baru |
| POST | `auth/logout/` | Tidak; wajib refresh token valid | Memasukkan refresh token ke blacklist |
| GET | `auth/me/` | Ya | Mengambil profil akun pengguna login |
| PATCH | `auth/me/` | Ya | Memperbarui profil akun pengguna login |
| GET | `health-profile/` | Ya | Mengambil profil kesehatan pengguna login |
| POST | `health-profile/` | Ya | Membuat profil kesehatan pertama kali |
| PATCH | `health-profile/` | Ya | Memperbarui sebagian profil kesehatan |
| GET | `history/` | Ya | Mengambil daftar riwayat sendiri |
| GET | `history/{id}/` | Ya | Mengambil detail riwayat sendiri |
| DELETE | `history/{id}/` | Ya | Menghapus riwayat sendiri |

Endpoint riwayat belum menyediakan POST langsung, PUT, atau PATCH. Riwayat dibuat otomatis oleh endpoint analisis yang berhasil jika pengguna terautentikasi.

### 1.1 GET /api/v1/health/

Memeriksa apakah backend dapat diakses.

Contoh respons HTTP 200:

```json
{
  "success": true,
  "status": "ok",
  "service": "HealthCoach API"
}
```

### 1.2 POST /api/v1/analyze/

Menerima foto makanan, menjalankan pipeline identifikasi Gemini Vision, mencari nutrisi melalui repository, mencoba estimasi AI bila diperlukan, dan menghasilkan rekomendasi.

Request menggunakan `multipart/form-data`, dengan field `images` untuk satu atau beberapa foto makanan/porsi yang sama. Field lama `image` masih didukung untuk kompatibilitas.

Ketentuan upload pada dokumentasi sebelumnya:

- Jumlah foto: 1–5.
- Format: JPG/JPEG, PNG, WEBP.
- Maksimal 5 MB per foto.
- Maksimal total 20 MB.
- Semua foto dalam satu request mewakili makanan atau porsi yang sama.

Batas aktual mengikuti `MAX_UPLOAD_IMAGES`, `MAX_IMAGE_SIZE_MB`, dan `MAX_TOTAL_UPLOAD_MB` pada konfigurasi Django yang aktif.

Contoh perintah melalui Command Prompt (CMD):

```cmd
curl -X POST http://127.0.0.1:8000/api/v1/analyze/ ^
  -F "images=@D:\foto\makanan-depan.jpg" ^
  -F "images=@D:\foto\makanan-samping.jpg"
```

Untuk menyimpan hasil ke riwayat akun, sertakan header:

```http
Authorization: Bearer <ACCESS_TOKEN>
```

Tanpa token, analisis tetap dapat dilakukan, tetapi hasil tidak disimpan ke riwayat pengguna.

Contoh respons HTTP 200 (sumber nutrisi dataset, pengguna login):

```json
{
  "success": true,
  "data": {
    "identification": {
      "food_name": "Nasi Goreng",
      "canonical_food_name": null,
      "identification_status": "IDENTIFIED",
      "confidence": "tinggi",
      "ingredients": [],
      "notes": ""
    },
    "matching": {
      "normalized_name": "nasi goreng",
      "status": "MATCHED",
      "duplicate_count": 1,
      "method": "EXACT",
      "reference_name": null
    },
    "nutrition": {
      "id": "773",
      "name": "Nasi Goreng",
      "calories": "276.0",
      "proteins": "3.2",
      "fat": "3.2",
      "carbohydrate": "30.2",
      "image": ""
    },
    "nutrition_source": "DATASET",
    "estimation_note": null,
    "recommendation": "Contoh rekomendasi yang dihasilkan sistem.",
    "recommendation_details": {},
    "note": "Contoh catatan analisis."
  },
  "meta": {
    "request_id": "contoh-uuid",
    "images_received": 2,
    "history_id": 12
  }
}
```

`history_id` bernilai ID riwayat bila analisis berhasil dan pengguna terautentikasi. Untuk analisis anonim, nilainya `null`. Nilai nutrisi serta ID di atas hanyalah contoh dokumentasi.

**Sumber nutrisi:**

| nutrition_source | Kondisi | Isi nutrition |
|---|---|---|
| DATASET | Repository menemukan makanan (MATCHED) | Nutrisi dari dataset |
| AI_ESTIMATED | Makanan teridentifikasi, tidak cocok di dataset, dan AI menyediakan estimasi | Estimasi nutrisi AI |
| UNAVAILABLE | Data nutrisi dan estimasi tidak tersedia | null |

`matching.status` menjelaskan kecocokan terhadap dataset, sedangkan `nutrition_source` menunjukkan asal nilai nutrisi.

Oleh karena itu, `matching.status = "NOT_MATCHED"` dapat terjadi bersama `nutrition_source = "AI_ESTIMATED"`.

Untuk `AI_ESTIMATED`, `estimation_note` memuat penjelasan bahwa nilai nutrisi merupakan perkiraan AI berbasis informasi visual, bukan nilai resmi dataset.

Pada `UNAVAILABLE`, `estimation_note` dapat berisi alasan data tidak tersedia atau `null` ketika objek tidak dikenali (`UNKNOWN`). Frontend tidak boleh menganggap contoh nilai sebagai hasil aktual.

### 1.3 POST /api/v1/auth/register/

Mendaftarkan akun menggunakan `RegisterSerializer` dan model User Django yang sudah ada.

Field wajib:

- `username`
- `email`
- `password`

Serializer menerapkan validasi password Django serta menolak email yang telah digunakan.

Contoh request:

```json
{
  "username": "contoh_pengguna",
  "email": "contoh@example.com",
  "password": "<PASSWORD_PENGGUNA>"
}
```

Contoh respons sukses HTTP 201:

```json
{
  "success": true,
  "message": "Registrasi berhasil.",
  "data": {
    "id": 1,
    "username": "contoh_pengguna",
    "email": "contoh@example.com"
  }
}
```

Password tidak dikembalikan dalam respons.

Registrasi melalui API telah berhasil diuji langsung pada database PostgreSQL yang terhubung pada 6 November 2026 menggunakan akun pengujian.

### 1.4 POST /api/v1/auth/login/

Login menggunakan `TokenObtainPairView` dari SimpleJWT.

Contoh request:

```json
{
  "username": "contoh_pengguna",
  "password": "<PASSWORD_PENGGUNA>"
}
```

Contoh respons sukses HTTP 200:

```json
{
  "refresh": "<REFRESH_TOKEN>",
  "access": "<ACCESS_TOKEN>"
}
```

Respons login standar SimpleJWT tidak menggunakan pembungkus `success` atau `data` seperti beberapa endpoint HealthCoach lainnya.

Token pada contoh tersebut hanya placeholder.

### 1.5 POST /api/v1/auth/refresh/

Mengirim refresh token yang masih berlaku dan belum di-blacklist untuk memperoleh access token baru.

Endpoint ini tidak membutuhkan access token pada header.

Contoh request:

```json
{
  "refresh": "<REFRESH_TOKEN>"
}
```

Contoh respons sukses HTTP 200:

```json
{
  "access": "<ACCESS_TOKEN_BARU>"
}
```

Format respons mengikuti SimpleJWT dan konfigurasi aktif.

Pengujian langsung melalui PowerShell pada 6 November 2026 membuktikan access token hasil refresh dapat dipakai kembali untuk GET `/api/v1/auth/me/`.

Konfigurasi JWT yang diperiksa pada 6 November 2026:

| Pengaturan | Nilai |
|---|---|
| ACCESS_TOKEN_LIFETIME | 5 menit |
| REFRESH_TOKEN_LIFETIME | 1 hari |
| ROTATE_REFRESH_TOKENS | False |
| BLACKLIST_AFTER_ROTATION | False |

`BLACKLIST_AFTER_ROTATION = False` tidak menonaktifkan proses blacklist pada endpoint logout.

Refresh token tetap dapat diblacklist secara eksplisit saat logout.

Apabila access token kedaluwarsa, frontend sebaiknya mencoba endpoint refresh dengan refresh token yang masih berlaku, lalu mengulangi request dengan access token baru.

Bila refresh token tidak valid, sudah kedaluwarsa, atau telah di-blacklist, pengguna perlu login kembali.

Refresh otomatis di aplikasi mobile menjadi tanggung jawab Clau.

### 1.6 POST /api/v1/auth/logout/

Mengakhiri sesi dengan memasukkan refresh token valid ke blacklist SimpleJWT.

Endpoint logout yang telah diperbarui menggunakan:

```python
authentication_classes = []
permission_classes = [AllowAny]
```

Dengan konfigurasi tersebut, endpoint logout tidak memerlukan access token.

Access token kedaluwarsa atau tidak valid dalam header tidak menghalangi logout.

Contoh request:

```json
{
  "refresh": "<REFRESH_TOKEN>"
}
```

Contoh respons sukses HTTP 200:

```json
{
  "success": true,
  "message": "Logout berhasil."
}
```

Ketentuan logout:

- Body wajib berisi refresh token yang valid.
- Refresh token kosong, tidak valid, atau kedaluwarsa ditolak.
- Setelah logout berhasil, refresh token di-blacklist dan tidak bisa dipakai lagi untuk meminta access token baru.
- Backend tidak lagi memeriksa kepemilikan refresh token terhadap `request.user` di endpoint ini karena access token tidak diwajibkan.
- Refresh token adalah kredensial bearer yang harus dijaga kerahasiaannya.
- Frontend menghapus access token dan refresh token dari penyimpanan lokal setelah logout berhasil.
- Access token yang pernah diterbitkan tidak otomatis dicabut oleh blacklist refresh token; access token tersebut mungkin masih dapat dipakai hingga kedaluwarsa.

Hasil uji langsung 6 November 2026 menunjukkan logout berhasil saat header mengandung access token tidak valid.

Setelah logout, permintaan refresh dengan token yang sama menghasilkan HTTP 401.

### 1.7 GET /api/v1/auth/me/

Mengambil profil pengguna yang sedang login berdasarkan access token JWT yang valid.

Header:

```http
Authorization: Bearer <ACCESS_TOKEN>
```

Contoh respons HTTP 200:

```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "contoh_pengguna",
    "email": "contoh@example.com",
    "first_name": "Dini",
    "last_name": "Pratiwi"
  }
}
```

### 1.8 PATCH /api/v1/auth/me/

Memperbarui sebagian data profil pengguna yang sedang login menggunakan model User Django yang tersedia.

Endpoint ini tidak memerlukan model atau migrasi baru.

Autentikasi: access token JWT wajib.

Header:

```http
Authorization: Bearer <ACCESS_TOKEN>
Content-Type: application/json
```

Field yang boleh diperbarui:

- `username`
- `email`
- `first_name`
- `last_name`

Satu atau beberapa field dapat dikirim dalam satu request.

Contoh request:

```json
{
  "first_name": "Dini",
  "last_name": "Pratiwi"
}
```

Contoh respons HTTP 200:

```json
{
  "success": true,
  "message": "Profil berhasil diperbarui.",
  "data": {
    "id": 1,
    "username": "contoh_pengguna",
    "email": "contoh@example.com",
    "first_name": "Dini",
    "last_name": "Pratiwi"
  }
}
```

Validasi dan keamanan:

- Pengguna hanya dapat memperbarui data miliknya sendiri melalui `request.user`.
- Username dan email yang telah digunakan pengguna lain ditolak; pemeriksaan duplikasi tidak membedakan huruf besar/kecil.
- Email dinormalisasi menjadi huruf kecil.
- Field `id` bersifat read-only dan bukan input yang diizinkan untuk PATCH.
- Field sensitif seperti `password`, `is_staff`, dan `is_superuser` tidak diizinkan.
- Request kosong atau field di luar daftar yang diizinkan ditolak dengan HTTP 400.
- Request tanpa access token valid ditolak dengan HTTP 401 pada konfigurasi autentikasi yang diuji.

Pengujian langsung melalui PowerShell telah membuktikan PATCH nama depan/belakang berhasil, lalu nilai yang sama terbaca kembali menggunakan GET dengan access token hasil refresh pada koneksi PostgreSQL Supabase yang aktif.

**Batas cakupan:** `/api/v1/auth/me/` khusus profil akun. Data kesehatan disediakan melalui endpoint terpisah `/api/v1/health-profile/`, dijelaskan lengkap pada bagian 11.

---

## 2. API Riwayat Analisis

Model `FoodAnalysisHistory` disediakan oleh bagian database dengan field:

- `user`
- `result` (JSON)
- `created_at`

Endpoint riwayat menggunakan model tersebut tanpa mengubah struktur atau migrasinya.

Semua endpoint riwayat memerlukan autentikasi. Data dibatasi berdasarkan `request.user`; klien tidak dapat memilih pemilik riwayat melalui ID pengguna.

### 2.1 GET /api/v1/history/

Mengembalikan daftar riwayat pengguna yang sedang login, diurutkan dari data terbaru.

Contoh respons HTTP 200:

```json
{
  "success": true,
  "data": [
    {
      "id": 12,
      "result": {
        "identification": {
          "food_name": "Nasi Goreng"
        },
        "nutrition_source": "DATASET"
      },
      "created_at": "2026-11-05T10:00:00+07:00"
    }
  ]
}
```

Field `result` sebenarnya menyimpan seluruh keluaran pipeline; contoh di atas disingkat.

Jika belum ada riwayat, `data` berupa array kosong `[]`.

### 2.2 GET /api/v1/history/{id}/

Mengambil satu riwayat milik pengguna yang sedang login.

Struktur data sama dengan satu item pada respons daftar riwayat.

Jika ID tidak ditemukan atau milik pengguna lain, endpoint mengembalikan HTTP 404.

### 2.3 DELETE /api/v1/history/{id}/

Menghapus satu riwayat milik pengguna yang sedang login.

Contoh respons HTTP 200:

```json
{
  "success": true,
  "message": "Riwayat analisis berhasil dihapus."
}
```

ID milik pengguna lain tidak dapat dihapus dan menghasilkan HTTP 404.

### 2.4 Penyimpanan Riwayat pada POST /api/v1/analyze/

Setelah pipeline berhasil:

1. Jika `request.user.is_authenticated`, backend menyimpan hasil pipeline dalam `FoodAnalysisHistory` dengan pemilik `request.user`.
2. ID catatan dikembalikan melalui `meta.history_id`.
3. Jika pengguna anonim, analisis tetap berjalan tanpa menyimpan riwayat dan `history_id = null`.
4. Jika pipeline gagal sebelum menghasilkan hasil, riwayat baru tidak dibuat.

Penyimpanan riwayat telah diuji menggunakan database pengujian Django dan mock pada pipeline.

Pembacaan tabel riwayat di koneksi PostgreSQL Supabase juga telah berhasil.

Namun, pengujian manual dalam pekerjaan ini belum membuktikan seluruh alur foto → Gemini asli → riwayat tersimpan secara end-to-end.

---

## 3. Penanganan Error dan Keamanan API

Backend menggunakan error handler yang membentuk JSON terstruktur untuk error yang ditangani.

Contoh error validasi HTTP 400:

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

Beberapa kode error analisis yang terdokumentasi:

- `VALIDATION_ERROR`: request tidak memenuhi validasi.
- `GEMINI_NOT_CONFIGURED`: konfigurasi Gemini belum tersedia.
- `GEMINI_TIMEOUT`: pemanggilan Gemini melewati batas waktu.
- `GEMINI_QUOTA_EXCEEDED`: kuota Gemini habis.
- `GEMINI_ACCESS_DENIED`: masalah akses layanan Gemini.
- `GEMINI_INVALID_RESPONSE`: respons Gemini tidak valid.
- `GEMINI_UNAVAILABLE`: layanan Gemini tidak tersedia.
- `NUTRITION_DATA_UNAVAILABLE`: sumber nutrisi bermasalah.
- `TOKEN_NOT_VALID`: token JWT tidak valid, kedaluwarsa, atau ditolak dalam konteks yang sesuai.

Endpoint yang membutuhkan login menolak request tanpa access token valid, umumnya HTTP 401 pada konfigurasi yang diuji.

Riwayat milik pengguna lain dikembalikan sebagai HTTP 404.

Validasi PATCH profil menolak field tidak dikenal, request kosong, atau duplikasi dengan HTTP 400.

Ketentuan keamanan:

- Simpan API key, password database, dan Django secret key di environment atau secret manager, bukan dalam kode atau dokumentasi GitHub.
- Jangan mengunggah `.env` yang mengandung rahasia.
- Jangan mencantumkan password dan JWT asli pada dokumentasi, screenshot, atau log yang dibagikan.
- Jika kredensial pernah terpublikasi, cabut atau rotasi kredensial terdampak dan koordinasikan penanganan riwayat Git dengan pemilik repository.
- Pengguna tidak dapat mengirim field `user` untuk mengambil atau menghapus riwayat orang lain.
- Refresh token harus diperlakukan sebagai rahasia karena pemegang token valid dapat menggunakannya untuk refresh atau pencabutan saat logout.

---

## 4. Alur Analisis Makanan

1. Pengguna memilih foto makanan melalui frontend.
2. Frontend mengirim `POST /api/v1/analyze/` menggunakan `multipart/form-data`.
3. Backend memvalidasi jenis, jumlah, dan ukuran gambar.
4. Gemini Vision mengidentifikasi makanan dari satu atau beberapa sudut foto.
5. Repository nutrisi mencari kecocokan EXACT atau CANONICAL terhadap dataset.
6. Jika MATCHED, nutrisi dari dataset digunakan (`DATASET`).
7. Jika NOT_MATCHED dan makanan teridentifikasi, AI dapat mencoba estimasi nutrisi (`AI_ESTIMATED`); jika tidak tersedia menjadi `UNAVAILABLE`.
8. Pipeline menyusun rekomendasi, sumber nutrisi, dan catatan analisis.
9. Jika pengguna login, backend API menyimpan hasil ke riwayat.
10. Backend mengembalikan respons JSON ke frontend.

Nilai `AI_ESTIMATED` adalah perkiraan berbasis informasi visual, bukan pengukuran resmi.

Jika objek tidak dikenali (`UNKNOWN`), pipeline tidak menjalankan estimasi nutrisi berdasarkan kode yang sebelumnya diperiksa.

---

## 5. Integrasi Database PostgreSQL (Antarmuka Backend)

Database dan repository nutrisi merupakan bagian Yuli.

Backend mengaksesnya melalui model/repository yang tersedia; frontend tidak seharusnya mengakses database secara langsung.

Backend sebelumnya mendukung sumber CSV dan PostgreSQL.

Konfigurasi yang terverifikasi aktif pada 6 November 2026:

```dotenv
DB_ENGINE=postgresql
NUTRITION_SOURCE=database
NUTRITION_MODEL=api.Nutrition
```

Pemeriksaan Django menunjukkan:

- Engine PostgreSQL aktif.
- Host database terisi.
- `connection.ensure_connection()` berhasil.
- `migrate --check` selesai tanpa error.
- Pembacaan data melalui ORM berhasil.

Saat pemeriksaan sebelumnya, database memiliki 9 pengguna, 1.346 data nutrisi, dan 1 riwayat sebelum akun uji didaftarkan.

Angka tersebut merupakan snapshot pengujian, bukan jumlah data permanen.

Parameter koneksi dan password tetap disimpan secara privat pada environment.

Perubahan konfigurasi, model, atau migrasi harus dikoordinasikan dengan Yuli.

Model `FoodAnalysisHistory` serta migrasinya berasal dari commit `2775d48` milik bagian database.

Dokumentasi detail database tetap berada dalam `DATABASE_DOCUMENTATION.md`.

### 5.1 Integrasi Model UserHealthProfile

Model `UserHealthProfile` disediakan Yuli.

Informasi model:

| Komponen | Keterangan |
|---|---|
| Model | `UserHealthProfile` |
| Tabel PostgreSQL | `user_health_profiles` |
| Relasi | OneToOne dengan User Django |
| Migrasi | `0003_userhealthprofile.py` |
| Pemilik model | Yuli |
| Pengguna model melalui API | Tiwi |

Migrasi `0003_userhealthprofile` telah berhasil diterapkan dan dikonfirmasi menggunakan `showmigrations` pada 7 November 2026.

Hasilnya menunjukkan:

```text
[X] 0001_initial
[X] 0002_foodanalysishistory
[X] 0003_userhealthprofile
```

Pembacaan tabel `UserHealthProfile` melalui ORM juga telah berhasil pada PostgreSQL Supabase.

Pada pemeriksaan awal, tabel belum memiliki data profil kesehatan.

Selanjutnya, Tiwi berhasil membuat profil kesehatan pertama melalui endpoint POST menggunakan akun khusus pengujian.

**Batas tanggung jawab:** Tiwi menggunakan model dan tabel yang tersedia tanpa membuat ulang atau mengubah model serta migrasi milik Yuli.

---

## 6. Panduan Integrasi Frontend React/Vite dan Mobile

Frontend HealthCoach berkomunikasi dengan Django REST Framework melalui HTTP JSON dan FormData.

Integrasi otomatis refresh token untuk aplikasi mobile menjadi tanggung jawab Clau.

### 6.1 Mengirim Foto dengan FormData

```javascript
async function analyzeFood(files, accessToken = null) {
  const formData = new FormData();

  files.forEach((file) => {
    formData.append("images", file);
  });

  const headers = {};

  if (accessToken) {
    headers.Authorization = `Bearer ${accessToken}`;
  }

  const response = await fetch(
    "http://127.0.0.1:8000/api/v1/analyze/",
    {
      method: "POST",
      headers,
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

  return result;
}
```

Gunakan `formData.append("images", file)` untuk setiap foto.

Jangan menetapkan `Content-Type` manual pada FormData karena browser akan membuat boundary multipart.

### 6.2 Membaca Hasil JSON

```javascript
const payload = await analyzeFood(files, accessToken);
const result = payload.data;

const foodName = result.identification?.food_name;
const matchingStatus = result.matching?.status;
const nutrition = result.nutrition;
const nutritionSource = result.nutrition_source;
const estimationNote = result.estimation_note;
const recommendation = result.recommendation;
const note = result.note;
const historyId = payload.meta?.history_id;

const calories = nutrition?.calories;
const proteins = nutrition?.proteins;
const carbohydrate = nutrition?.carbohydrate;
const fat = nutrition?.fat;
```

Jika `nutrition_source = AI_ESTIMATED`, tampilkan keterangan bahwa angka merupakan estimasi serta `estimation_note`.

Jika `nutrition = null`, tampilkan bahwa nutrisi belum tersedia, bukan angka contoh.

### 6.3 Validasi Upload Frontend dan Backend

Pada pemeriksaan lama terhadap `Analysis.jsx`, pernah ditemukan perbedaan:

| Pengaturan | Frontend saat pemeriksaan lama | Backend saat dokumentasi lama |
|---|---|---|
| Maksimal foto | 3 | 5 |
| Maksimal per foto | 10 MB | 5 MB |
| Format | JPG, PNG, WEBP | JPG, PNG, WEBP |

Angka frontend tersebut merupakan catatan pemeriksaan sebelumnya, bukan verifikasi kondisi frontend terkini.

Aturan UI dan API perlu diselaraskan dengan batas backend yang sedang aktif bersama Clau.

### 6.4 Loading, Error, Riwayat, dan Refresh JWT

- Tampilkan loading selama analisis berlangsung dan hentikan setelah request selesai, baik berhasil maupun gagal.
- Tampilkan data nutrisi sesuai `nutrition_source` serta pesan error API atau fallback yang aman.
- Sertakan access token pada GET/DELETE riwayat, GET/PATCH profil akun, dan GET/POST/PATCH profil kesehatan.
- Jika request terproteksi mendapat HTTP 401 akibat access token kedaluwarsa, frontend dapat mencoba `POST /auth/refresh/` satu kali menggunakan refresh token yang valid.
- Setelah menerima access token baru, ulangi request sebelumnya.
- Jika refresh gagal, hapus token lokal dan arahkan pengguna untuk login kembali.
- Untuk logout, kirim refresh token ke `POST /auth/logout/`; access token tidak diwajibkan.
- Setelah logout berhasil, hapus access token dan refresh token dari penyimpanan lokal.
- Hindari pengulangan refresh tanpa batas jika request terus menghasilkan HTTP 401.

Untuk antarmuka profil kesehatan, gunakan `GET`, `POST`, dan `PATCH /api/v1/health-profile/` sebagaimana didokumentasikan pada bagian 11.

Ketiga endpoint tersebut wajib menggunakan access token JWT.

Pada pemeriksaan frontend sebelumnya, `Analysis.jsx` pernah menggunakan data contoh dan `setTimeout`.

Kondisi frontend terbaru belum diverifikasi ulang dalam pekerjaan ini. Perubahan frontend/mobile tetap menjadi bagian Clau.

---

## 7. CORS

Dokumentasi terdahulu mencatat origin pengembangan lokal seperti:

```text
http://localhost:3000
http://127.0.0.1:3000
http://localhost:5173
http://127.0.0.1:5173
```

Daftar tersebut berasal dari dokumentasi sebelumnya, bukan pemeriksaan ulang konfigurasi terkini.

Jika origin frontend berbeda, periksa konfigurasi dan koordinasikan perubahan `config/settings.py` dengan Yuli.

---

## 8. Pengujian Backend & API

Pengujian otomatis menggunakan Django Test Framework, DRF APIClient, database pengujian, dan mock terhadap dependency eksternal pada skenario tertentu.

### 8.1 Perintah Pengujian

```powershell
python HealthCoach\manage.py check

python HealthCoach\manage.py test api.tests.test_auth

python HealthCoach\manage.py test api.tests.test_health_profile_api

python HealthCoach\manage.py test api.tests
```

### 8.2 Hasil Pengujian Terbaru

Pengujian terakhir pada 7 November 2026:

| Pemeriksaan | Hasil |
|---|---|
| Django system check | Tidak ada masalah |
| Pengujian autentikasi | 22/22 lulus |
| Pengujian API profil kesehatan | 13/13 lulus |
| Seluruh pengujian Backend & API | **92/92 lulus** |

### 8.3 Cakupan Pengujian Otomatis

Pengujian mencakup:

- Validasi input foto, struktur respons, dan penanganan error.
- Endpoint dan pipeline untuk DATASET, AI_ESTIMATED, UNAVAILABLE, dan UNKNOWN menggunakan mock layanan eksternal.
- Autentikasi JWT, registrasi, login, refresh, dan logout.
- GET/PATCH profil akun, validasi username/email, penolakan field sensitif, dan pembatasan akses.
- Logout tanpa access token, logout dengan access token kedaluwarsa, serta penolakan refresh token setelah logout.
- Endpoint riwayat hanya menerima pengguna login dan mengakses data miliknya.
- Detail dan penghapusan riwayat milik pengguna lain mengembalikan HTTP 404.
- Hasil analisis pengguna login tersimpan, hasil anonim tidak tersimpan, dan pipeline gagal tidak menambah riwayat.
- GET profil kesehatan ketika profil belum tersedia.
- POST pembuatan profil kesehatan pertama kali.
- GET profil kesehatan yang sudah tersimpan.
- PATCH sebagian data kesehatan.
- PATCH ketika profil belum tersedia.
- Pencegahan pembuatan profil kesehatan ganda.
- Validasi berat badan dan tinggi badan.
- Validasi gender, tingkat aktivitas, dan tujuan nutrisi.
- Validasi tanggal lahir di masa depan.
- Penolakan field yang tidak diizinkan.
- Pembatasan akses profil kesehatan antar-pengguna.
- Penolakan request tanpa autentikasi.
- Penolakan request kosong.

### 8.4 Pengujian Manual API Akun dan JWT

Pengujian menggunakan PowerShell terhadap server Django dan PostgreSQL Supabase pada 6 November 2026:

- Registrasi akun pengujian berhasil dengan HTTP 201.
- Login JWT berhasil menghasilkan access token dan refresh token.
- GET profil akun berhasil.
- PATCH nama depan dan nama belakang berhasil.
- GET profil menggunakan access token hasil refresh menampilkan perubahan.
- Refresh token menghasilkan access token baru.
- Logout berhasil walaupun header Authorization berisi access token tidak valid.
- Refresh token yang sudah digunakan untuk logout ditolak dengan HTTP 401.

### 8.5 Pengujian Manual API Profil Kesehatan

Pengujian dilakukan pada 7 November 2026 menggunakan akun khusus pengujian, melalui PowerShell dan server Django yang terhubung dengan Supabase.

Hasil pengujian:

| Skenario | Hasil |
|---|---|
| Login JWT | Berhasil |
| GET sebelum profil dibuat | Berhasil, `data: null` |
| POST profil kesehatan pertama | Berhasil, HTTP 201 |
| GET membaca profil tersimpan | Berhasil |
| PATCH mengubah berat dan tujuan nutrisi | Berhasil, HTTP 200 |
| GET ulang setelah PATCH | Berhasil, perubahan tersimpan |
| POST kedua pada akun yang sama | Ditolak, HTTP 409 |

Data yang digunakan dalam pengujian merupakan data contoh.

Pada POST pertama, profil dibuat menggunakan berat badan 65,50 kg dan tinggi badan 170 cm.

PATCH kemudian memperbarui berat menjadi 68,50 kg dan tujuan nutrisi dari `maintain_weight` menjadi `healthy_eating`.

GET ulang mengembalikan nilai terbaru dengan hasil pemeriksaan:

```text
GETBerhasil     : True
BeratTersimpan  : 68.50
TujuanTersimpan : healthy_eating
DataSesuai      : True
```

Pengujian POST kedua menghasilkan:

```text
Status HTTP          : 409
Profil ganda ditolak : True
```

Pengujian manual tersebut hanya menggunakan akun khusus pengujian dan tidak mengubah profil pengguna lain.

Pengujian otomatis tidak dengan sendirinya membuktikan seluruh layanan eksternal bekerja end-to-end pada lingkungan produksi.

Integrasi mobile dan layanan Gemini asli masih perlu diverifikasi sesuai tanggung jawab tim.

---

## 9. Pembagian Tanggung Jawab dan Koordinasi

### Tiwi — Backend & API

Bertanggung jawab terhadap:

- Endpoint API.
- Autentikasi JWT.
- Profil akun pengguna.
- API profil kesehatan.
- Serializer dan validasi input.
- Pembatasan akses serta otorisasi pengguna.
- Kontrak request dan respons JSON.
- Penghubung API dengan pipeline.
- Penyimpanan hasil analisis melalui API.
- Pengujian otomatis dan pengujian langsung.
- Dokumentasi Backend & API.

Autentikasi sebelumnya terkait Issue #54 dan integrasi frontend–backend sebelumnya terkait Issue #55.

### Yuli — Database dan Dashboard Django

Bertanggung jawab terhadap:

- Model database.
- Migrasi database.
- Model `UserHealthProfile`.
- Koneksi PostgreSQL Supabase.
- Repository nutrisi.
- Dashboard Django.
- Dokumentasi database.

### Aril — Artificial Intelligence

Bertanggung jawab terhadap:

- Identifikasi makanan menggunakan Gemini Vision.
- Estimasi nutrisi berbasis AI.
- Logika rekomendasi makanan.
- Pemanfaatan data profil kesehatan dalam rekomendasi apabila telah disepakati.

### Clau — Frontend

Bertanggung jawab terhadap:

- Frontend React/Vite dan mobile.
- Formulir profil akun dan kesehatan.
- Tombol pilihan jenis kelamin.
- Slider tinggi dan berat badan.
- Pilihan tujuan nutrisi.
- Integrasi HTTP dengan backend.
- Penyimpanan token pada sisi klien.
- Refresh otomatis access token.
- Tampilan hasil analisis dan riwayat.

### Aturan Koordinasi

Tiwi tidak mengubah bagian berikut tanpa koordinasi:

```text
HealthCoach/api/models.py
HealthCoach/api/migrations/
HealthCoach/config/settings.py
HealthCoach/config/urls.py
HealthCoach/dashboard/
```

Pekerjaan Tiwi dilakukan pada branch:

```text
feature/backend-api-profil-tiwi
```

Sesuai permintaan Yuli untuk fitur profil kesehatan, perubahan perlu diajukan melalui Pull Request menuju `main`.

Pesan commit menggunakan bahasa Indonesia.

---

## 10. Catatan Perkembangan

- PR #68 dan #69 milik Tiwi telah di-merge. PR #69 menambahkan empat pengujian endpoint–pipeline untuk sumber nutrisi.
- Commit `2775d48` dari Yuli menambahkan `FoodAnalysisHistory`, migrasi, dashboard, dan dokumentasi database.
- PR #70 dari branch `feature/backend-api-history-tiwi` telah di-merge ke `main`, berisi daftar, detail, dan penghapusan riwayat serta penyimpanan hasil analisis melalui API.
- PR #71 telah di-merge ke `main` melalui commit `4968a15`, berisi API edit profil akun dan perbaikan logout JWT. Commit Tiwi untuk pekerjaan tersebut adalah `342f37e`.
- Model `UserHealthProfile` dan migrasi `0003_userhealthprofile.py` milik Yuli telah tersedia di `main` melalui commit `e72eee6`.
- Branch Tiwi telah diperbarui sampai commit `9d15214` sebelum membuat API kesehatan.
- Fitur PATCH profil akun dan logout JWT sudah selesai dan berada pada `main`.
- Fitur profil kesehatan menggunakan endpoint terpisah `/api/v1/health-profile/`.
- Tiwi telah membuat serializer, views GET/POST/PATCH, routing, dan 13 pengujian otomatis untuk profil kesehatan.
- Seluruh **92/92 pengujian Backend & API lulus** pada 7 November 2026.
- Pengujian manual Supabase untuk GET, POST, PATCH, GET ulang, dan penolakan POST kedua HTTP 409 telah berhasil.
- Saat pembaruan dokumentasi ini, implementasi API profil kesehatan masih berada sebagai perubahan lokal di branch `feature/backend-api-profil-tiwi` dan belum dinyatakan sudah di-commit, di-push, atau dibuatkan Pull Request.
- Refresh token otomatis dan integrasi tampilan frontend mobile tetap menjadi tanggung jawab Clau.

Dokumen ini berfokus pada kontrak API dan hasil pengujian yang telah diketahui.

Dokumen tidak memuat password, API key, token asli, maupun detail privat koneksi database.

---

## 11. API Profil Kesehatan Pengguna

**Status implementasi:** Dibuat dan diuji pada 7 November 2026. Belum dinyatakan sudah di-commit atau di-push pada saat pembaruan dokumentasi.

Fitur ini terpisah dari profil akun `GET/PATCH /api/v1/auth/me/`.

Model `UserHealthProfile` disediakan oleh Yuli dalam:

```text
HealthCoach/api/models.py
```

Migrasi:

```text
HealthCoach/api/migrations/0003_userhealthprofile.py
```

Model menggunakan tabel `user_health_profiles` dengan relasi OneToOne ke model User Django.

Dengan relasi ini, setiap akun hanya dapat memiliki satu profil kesehatan.

Tiwi tidak mengubah model atau migrasi tersebut.

### 11.1 Daftar Endpoint Profil Kesehatan

Semua endpoint berada pada base URL:

```text
http://127.0.0.1:8000/api/v1/
```

Seluruh endpoint wajib menggunakan access token JWT.

| Metode | Endpoint | Fungsi | Status sukses |
|---|---|---|---|
| GET | `health-profile/` | Mengambil profil kesehatan pengguna login | 200 |
| POST | `health-profile/` | Membuat profil kesehatan pertama kali | 201 |
| PATCH | `health-profile/` | Mengubah sebagian data profil | 200 |

PUT dan DELETE untuk profil kesehatan belum disediakan.

Pemilik profil selalu ditentukan dari `request.user`, bukan `user`, `user_id`, atau ID lain yang dikirim frontend.

### 11.2 Field dan Validasi

| Field | Tipe | Aturan |
|---|---|---|
| `id` | Integer | Hanya baca; dibuat database |
| `weight` | Decimal | 1–500 kg, maksimal dua angka desimal |
| `height` | Decimal | 30–300 cm, maksimal dua angka desimal |
| `gender` | String | male, female, prefer_not_to_say |
| `birth_date` | Tanggal | Format YYYY-MM-DD, tidak boleh masa depan |
| `activity_level` | String | sedentary, light, moderate, active, very_active |
| `nutrition_goal` | String | lose_weight, maintain_weight, gain_weight, healthy_eating |
| `created_at` | DateTime | Hanya baca, terisi otomatis |
| `updated_at` | DateTime | Hanya baca, diperbarui otomatis |

Semua field kesehatan pada model bersifat opsional sehingga pengisian dapat dilakukan secara bertahap.

Namun, serializer menolak POST atau PATCH yang kosong.

Serializer juga menolak field yang tidak dikenal, termasuk `user` dan `user_id`.

Nilai pilihan harus menggunakan kode pada tabel, bukan teks label yang terlihat pada tombol UI.

**Perhatian untuk frontend:**

Rancangan slider awal Clau menggunakan tinggi 100–220 cm dan berat 25–200 kg, sedangkan validasi model/API mendukung tinggi 30–300 cm dan berat 1–500 kg.

Rentang yang dipakai UI perlu disepakati bersama dan tidak boleh membiarkan nilai di luar aturan backend.

Rancangan UI awal juga belum menampilkan input `birth_date` atau `activity_level`. Kedua field tersebut dapat tetap kosong sesuai model sampai desain disepakati.

### 11.3 GET /api/v1/health-profile/

Digunakan untuk mengambil profil kesehatan milik pengguna yang sedang login.

Header:

```http
Authorization: Bearer <ACCESS_TOKEN>
```

**Saat profil belum tersedia, respons HTTP 200:**

```json
{
  "success": true,
  "data": null,
  "message": "Profil kesehatan belum diisi."
}
```

GET tidak membuat data profil baru secara otomatis.

Perilaku tersebut disebut **lazy creation**.

Profil kesehatan baru dibuat ketika pengguna mengirim POST pertama kali.

**Saat profil sudah tersedia, contoh respons HTTP 200:**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "weight": "65.50",
    "height": "170.00",
    "gender": "female",
    "birth_date": "2003-05-20",
    "activity_level": "moderate",
    "nutrition_goal": "maintain_weight",
    "created_at": "2026-11-07T12:00:15+07:00",
    "updated_at": "2026-11-07T12:00:15+07:00"
  }
}
```

ID dan timestamp pada contoh digunakan sebagai ilustrasi format.

### 11.4 POST /api/v1/health-profile/

Digunakan untuk membuat profil kesehatan pertama kali.

Pengguna hanya perlu mengirim field yang ingin diisi.

Header:

```http
Authorization: Bearer <ACCESS_TOKEN>
Content-Type: application/json
```

Contoh request:

```json
{
  "weight": "65.50",
  "height": "170.00",
  "gender": "female",
  "birth_date": "2003-05-20",
  "activity_level": "moderate",
  "nutrition_goal": "maintain_weight"
}
```

Contoh respons sukses HTTP 201:

```json
{
  "success": true,
  "message": "Profil kesehatan berhasil dibuat.",
  "data": {
    "id": 1,
    "weight": "65.50",
    "height": "170.00",
    "gender": "female",
    "birth_date": "2003-05-20",
    "activity_level": "moderate",
    "nutrition_goal": "maintain_weight",
    "created_at": "2026-11-07T12:00:15+07:00",
    "updated_at": "2026-11-07T12:00:15+07:00"
  }
}
```

Relasi `OneToOneField` mencegah lebih dari satu profil untuk pengguna yang sama.

Jika pengguna sudah memiliki profil kesehatan, POST berikutnya ditolak dengan HTTP 409 Conflict.

**Contoh respons HTTP 409:**

```json
{
  "success": false,
  "error": {
    "code": "PROFILE_ALREADY_EXISTS",
    "message": "Profil kesehatan sudah tersedia. Gunakan PATCH untuk memperbaruinya.",
    "details": null
  }
}
```

Dengan demikian, POST kedua tidak menimpa data profil yang sudah ada.

Frontend harus menggunakan PATCH untuk memperbarui profil.

### 11.5 PATCH /api/v1/health-profile/

Digunakan untuk memperbarui satu atau beberapa field profil kesehatan milik pengguna login.

Field yang tidak dikirim tetap mempertahankan nilai sebelumnya.

PATCH memerlukan profil yang sudah dibuat menggunakan POST.

Header:

```http
Authorization: Bearer <ACCESS_TOKEN>
Content-Type: application/json
```

Contoh request:

```json
{
  "weight": "68.50",
  "nutrition_goal": "healthy_eating"
}
```

Contoh respons sukses HTTP 200:

```json
{
  "success": true,
  "message": "Profil kesehatan berhasil diperbarui.",
  "data": {
    "id": 1,
    "weight": "68.50",
    "height": "170.00",
    "gender": "female",
    "birth_date": "2003-05-20",
    "activity_level": "moderate",
    "nutrition_goal": "healthy_eating",
    "created_at": "2026-11-07T12:00:15+07:00",
    "updated_at": "2026-11-07T12:06:51+07:00"
  }
}
```

Jika profil belum pernah dibuat, PATCH mengembalikan HTTP 404.

Frontend perlu menggunakan POST terlebih dahulu.

### 11.6 Error dan Keamanan

| HTTP | Kondisi |
|---|---|
| 200 | GET atau PATCH berhasil |
| 201 | POST profil pertama berhasil |
| 400 | Input kosong, nilai tidak valid, field asing, tanggal masa depan, atau pilihan tidak sesuai |
| 401 | Access token tidak ada, tidak valid, atau kedaluwarsa |
| 404 | PATCH pada profil yang belum tersedia |
| 409 | POST saat pengguna sudah memiliki profil |

Seluruh metode menggunakan permission:

```python
permission_classes = [IsAuthenticated]
```

Pengambilan, pembuatan, dan perubahan profil menggunakan `request.user`, bukan ID pengguna dari frontend.

Endpoint tidak mengembalikan field `user` atau data profil pengguna lain.

Serializer menolak field asing agar pemilik data tidak dapat diganti secara manual.

Contoh error validasi HTTP 400 (ilustratif):

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Input tidak valid.",
    "details": {
      "weight": [
        "Berat badan harus antara 1 sampai 500 kg."
      ]
    }
  }
}
```

Detail pesan error sebenarnya mengikuti serializer dan exception handler yang aktif.

### 11.7 Alur Integrasi Frontend Clau

1. Setelah login, frontend menyimpan access token dan refresh token secara aman sesuai platform.
2. Saat halaman profil kesehatan dibuka, frontend memanggil `GET /api/v1/health-profile/`.
3. Jika `data` bernilai `null`, tampilkan pilihan dan slider kosong. GET tidak otomatis membuat profil.
4. Ketika pengguna memilih opsi dan menekan tombol Simpan Profil untuk pertama kali, frontend mengirim POST.
5. Jika profil sudah tersedia, frontend menggunakan PATCH untuk memperbarui data.
6. Setelah berhasil, frontend memperbarui tampilan berdasarkan respons API.
7. Jika diperlukan, frontend dapat melakukan GET ulang untuk memastikan data terbaru.
8. Jika access token kedaluwarsa, lakukan refresh sesuai mekanisme pada bagian 1.5.
9. Tangani status 400, 401, 404, dan 409 dengan pesan serta alur UI yang sesuai.

Pembagian tugas pada proses tersebut:

- Clau menangani pilihan jenis kelamin, slider, tanggal lahir, tingkat aktivitas, dan tombol Simpan Profil pada frontend.
- Tiwi menangani endpoint, autentikasi, validasi, serta respons API.
- Yuli menangani model, migrasi, dan database.
- Aril menangani potensi penggunaan profil sebagai konteks rekomendasi AI jika telah disepakati.

Penggunaan data profil kesehatan sebagai konteks AI belum dinyatakan sudah terintegrasi dalam pekerjaan ini.

### 11.8 Bukti Pengujian API Profil Kesehatan

**Pengujian otomatis pada 7 November 2026:**

```powershell
python HealthCoach\manage.py test api.tests.test_health_profile_api
```

Hasil:

```text
Found 13 test(s).
Ran 13 tests
OK
```

Kemudian seluruh tes backend:

```powershell
python HealthCoach\manage.py test api.tests
```

Hasil:

```text
Found 92 test(s).
Ran 92 tests
OK
```

Ketiga belas tes profil kesehatan mencakup:

- GET ketika profil belum tersedia.
- Autentikasi GET, POST, dan PATCH.
- POST pembuatan profil pertama.
- Penolakan POST kedua.
- GET profil yang sudah tersedia.
- PATCH pembaruan sebagian.
- PATCH ketika profil belum tersedia.
- Validasi berat dan tinggi badan.
- Validasi pilihan gender, aktivitas, dan tujuan nutrisi.
- Validasi tanggal lahir di masa depan.
- Penolakan field pemilik profil dari frontend.
- Perlindungan data antar-pengguna.
- Penolakan request kosong.

Seluruh 92 pengujian backend lulus menggunakan database test Django.

Pengujian tersebut tidak berarti layanan Gemini asli telah diuji langsung secara end-to-end.

**Pengujian manual melalui PowerShell dan Supabase pada 7 November 2026:**

1. Koneksi PostgreSQL berhasil dan migrasi `0003_userhealthprofile` telah diterapkan.
2. Tabel `user_health_profiles` berhasil dibaca dan awalnya belum memiliki profil.
3. Login JWT menggunakan akun pengujian berhasil.
4. GET sebelum profil tersedia menghasilkan `success: true` dan `data: null`.
5. POST berhasil membuat profil kesehatan pertama.
6. GET ulang berhasil membaca data yang disimpan.
7. PATCH memperbarui berat dari 65,50 menjadi 68,50 kg.
8. PATCH memperbarui tujuan nutrisi dari `maintain_weight` menjadi `healthy_eating`.
9. GET ulang mengembalikan data terbaru sesuai perubahan.
10. POST kedua untuk akun yang sama ditolak HTTP 409.

Output verifikasi setelah PATCH:

```text
GETBerhasil     : True
BeratTersimpan  : 68.50
TujuanTersimpan : healthy_eating
DataSesuai      : True
```

Output pencegahan profil ganda:

```text
Memulai pengujian pencegahan profil ganda...
Status HTTP: 409
Profil ganda ditolak: True
```

Pengujian dilakukan dengan satu akun khusus pengujian.

Hasil tersebut memverifikasi jalur baca dan tulis inti profil kesehatan melalui Supabase.

Namun, pengujian ini belum membuktikan keseluruhan integrasi aplikasi mobile maupun layanan Gemini nyata.

### 11.9 Kepemilikan Kode dan Koordinasi

| Anggota | Tanggung jawab |
|---|---|
| Yuli | Model `UserHealthProfile`, migrasi 0003, tabel dan konfigurasi Supabase |
| Tiwi | `health_profile_serializers.py`, `health_profile_views.py`, routing `api/urls.py`, pengujian, dan dokumentasi |
| Clau | Antarmuka pilihan, slider, formulir kesehatan, dan integrasi API mobile |
| Aril | Potensi pemanfaatan profil kesehatan dalam rekomendasi AI apabila disepakati |

API kesehatan tidak mengubah model, migrasi, dashboard, atau logika AI milik anggota lain.

Setelah pemeriksaan keamanan Git, perubahan perlu di-commit menggunakan pesan bahasa Indonesia, di-push ke branch Tiwi, dan dibuatkan Pull Request ke `main` sesuai permintaan Yuli.

---

**Akhir Dokumentasi Backend & API HealthCoach**

Dokumentasi diperbarui berdasarkan hasil implementasi dan pengujian yang diketahui sampai 7 November 2026.

Tidak ada password database, API key, JWT asli, atau informasi privat koneksi Supabase yang dicantumkan dalam dokumen ini.