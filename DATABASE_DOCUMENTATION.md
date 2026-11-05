
# HealthCoach - Database Documentation

## 1. Gambaran Umum

HealthCoach menggunakan Django ORM dengan PostgreSQL melalui Supabase sebagai database utama.

Database digunakan untuk:
- Menyimpan data nutrisi makanan.
- Menyimpan riwayat analisis makanan berdasarkan akun pengguna.
- Mengelola relasi data pengguna dengan riwayat analisis.

Konfigurasi koneksi database disimpan dalam file `.env` dan tidak boleh dimasukkan ke repository publik.

## 2. Struktur Database

### 2.1 Tabel nutrition

Tabel `nutrition` menyimpan informasi nutrisi makanan.

| Kolom | Tipe Data | Keterangan |
|---|---|---|
| id | BigInteger | Primary key |
| name | Varchar(255) | Nama makanan |
| calories | Float | Kalori |
| proteins | Float | Protein |
| fat | Float | Lemak |
| carbohydrate | Float | Karbohidrat |
| image | Varchar | URL gambar makanan |
| name_normalized | Varchar(255) | Nama makanan yang telah dinormalisasi |

Ketentuan:
- Primary key menggunakan kolom `id`.
- `name_normalized` memiliki indeks untuk membantu pencarian.
- Seluruh kolom wajib diisi pada model database, kecuali `image` yang memiliki nilai default kosong.

### 2.2 Tabel food_analysis_history

Tabel `food_analysis_history` menyimpan hasil analisis makanan milik pengguna.

| Kolom | Tipe Data | Keterangan |
|---|---|---|
| id | BigAutoField | Primary key otomatis |
| user_id | ForeignKey | Relasi ke pengguna |
| result | JSONField | Hasil analisis makanan |
| created_at | DateTime | Waktu pembuatan riwayat |

Ketentuan:
- Setiap riwayat dimiliki oleh satu pengguna.
- Satu pengguna dapat memiliki banyak riwayat analisis.
- Relasi pengguna mengarah ke model bawaan Django `auth.User`.
- Jika akun pengguna dihapus, riwayat miliknya ikut terhapus (`CASCADE`).
- Riwayat diurutkan berdasarkan waktu terbaru.

### 2.3 Tabel auth_user

Tabel `auth_user` merupakan tabel pengguna bawaan Django.

Tabel ini digunakan sebagai identitas pemilik riwayat analisis.

Pengelolaan autentikasi dan API pengguna mengikuti implementasi bagian Backend & API.

## 3. Relasi Antar Tabel

Relasi utama:

- `auth_user` memiliki relasi one-to-many dengan `food_analysis_history`.
- `food_analysis_history.user_id` menjadi foreign key yang mengarah ke `auth_user.id`.
- Tabel `nutrition` menyimpan dataset nutrisi dan tidak memiliki foreign key langsung ke tabel riwayat.

## 4. Migrasi Database

Migrasi dikelola menggunakan Django migrations.

| Migrasi | Keterangan | Status |
|---|---|---|
| api.0001_initial | Membuat tabel Nutrition | Sudah diterapkan |
| api.0002_foodanalysishistory | Membuat tabel FoodAnalysisHistory | Sudah diterapkan |

Pemeriksaan status migrasi:

```cmd
python manage.py showmigrations api
```

Pembuatan migrasi:

```cmd
python manage.py makemigrations api
```

Penerapan migrasi:

```cmd
python manage.py migrate
```

Migrasi harus dikoordinasikan sebelum diterapkan ke database bersama.

## 5. Konfigurasi Database

Konfigurasi koneksi PostgreSQL dikelola melalui file `.env`.

Variabel konfigurasi yang digunakan:

```env
DB_ENGINE=postgresql
NUTRITION_SOURCE=database
NUTRITION_MODEL=api.Nutrition
POSTGRES_HOST=...
POSTGRES_PORT=5432
POSTGRES_USER=...
POSTGRES_PASSWORD=...
```

Catatan keamanan:
- Jangan menyimpan password database di dalam kode.
- Jangan mengunggah `.env` ke GitHub.
- Gunakan environment variable untuk menyimpan kredensial.
- Frontend tidak boleh terhubung langsung ke database.

## 6. Validasi dan Integritas Data

Pemeriksaan data nutrisi sebelumnya menunjukkan:
- Jumlah data nutrisi: 1.346 baris.
- Nama makanan kosong: 0.
- Nama normalisasi kosong: 0.
- Nilai nutrisi negatif: 0.
- Gambar kosong: 0.
- Terdapat 4 kelompok data dengan nama normalisasi duplikat.

Data duplikat telah diidentifikasi, tetapi belum dilakukan penghapusan atau perubahan data.

Pemilihan data dengan nama normalisasi yang sama saat ini menggunakan urutan primary key terkecil.

## 7. Riwayat Analisis Pengguna

Tabel `food_analysis_history` sudah dibuat dan migrasi telah diterapkan pada database Supabase.

Namun, penyimpanan hasil analisis secara otomatis belum terintegrasi ke alur API.

Integrasi penyimpanan dan pengambilan riwayat menjadi pekerjaan lanjutan bagian Backend & API.

## 8. Backup dan Pemulihan Database

Backup dan pengujian pemulihan database belum diverifikasi.

Sebelum melakukan backup atau restore:
- Pastikan kredensial database tersedia.
- Tentukan lokasi penyimpanan backup yang aman.
- Jangan menyimpan file backup yang berisi data pengguna di repository publik.
- Lakukan pengujian restore pada lingkungan terpisah sebelum pemulihan database utama.

## 9. Catatan Pengembangan

Perubahan struktur database harus dilakukan melalui Django migrations.

Setiap perubahan model perlu:
1. Diperiksa terlebih dahulu.
2. Dibuatkan file migrasi.
3. Ditinjau sebelum diterapkan.
4. Dikoordinasikan dengan anggota tim yang menggunakan database.

Dokumentasi ini mencatat kondisi database berdasarkan pemeriksaan pengembangan hingga 5 November 2026.
