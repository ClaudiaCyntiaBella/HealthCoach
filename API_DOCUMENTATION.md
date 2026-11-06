Dokumentasi Backend & API HealthCoach
Dokumentasi ini menjelaskan endpoint Backend & API HealthCoach, analisis makanan melalui Gemini AI dan repository nutrisi, autentikasi JWT, pengelolaan profil pengguna, penyimpanan riwayat analisis, serta panduan integrasi frontend dengan Django REST Framework.

Pembaruan dokumentasi: 6 November 2026
Base URL pengembangan lokal: http://127.0.0.1:8000/api/v1/
Lingkup: Backend & API (Tiwi). Model, migrasi, dashboard Django, dan koneksi database dikelola Yuli; logika Gemini dan rekomendasi dikelola Aril; frontend dikelola Clau.

Contoh request dan respons di bawah bersifat ilustratif kecuali hasil pengujian yang dinyatakan secara khusus. Perilaku aktual mengikuti kode dan konfigurasi environment yang aktif. Jangan memasukkan password, API key, atau token asli ke dokumentasi.
1. Daftar Endpoint API
Semua path berikut berada di bawah prefix /api/v1/.
Method	Endpoint	Perlu access token?	Fungsi
GET	health/	Tidak	Memeriksa status backend
POST	analyze/	Opsional	Menganalisis foto; menyimpan riwayat jika login
POST	auth/register/	Tidak	Mendaftarkan akun pengguna
POST	auth/login/	Tidak	Mendapatkan pasangan token JWT
POST	auth/refresh/	Tidak; perlu refresh token	Mendapatkan access token baru
POST	auth/logout/	Tidak; wajib refresh token valid	Memasukkan refresh token ke blacklist
GET	auth/me/	Ya	Mengambil profil pengguna login
PATCH	auth/me/	Ya	Memperbarui profil pengguna login
GET	history/	Ya	Mengambil daftar riwayat sendiri
GET	history/{id}/	Ya	Mengambil detail riwayat sendiri
DELETE	history/{id}/	Ya	Menghapus riwayat sendiri


Endpoint riwayat belum menyediakan POST langsung, PUT, atau PATCH. Riwayat dibuat otomatis oleh endpoint analisis yang berhasil jika pengguna terautentikasi.
1.1 GET /api/v1/health/
Memeriksa apakah backend dapat diakses.

Contoh respons HTTP 200:
{
  "success": true,
  "status": "ok",
  "service": "HealthCoach API"
}
1.2 POST /api/v1/analyze/
Menerima foto makanan, menjalankan pipeline identifikasi Gemini Vision, mencari nutrisi melalui repository, mencoba estimasi AI bila diperlukan, dan menghasilkan rekomendasi.

Request: multipart/form-data, dengan field images (satu atau beberapa foto makanan/porsi yang sama). Field lama image masih didukung untuk kompatibilitas.

Ketentuan upload pada dokumentasi sebelumnya:
- Jumlah foto: 1–5.
- Format: JPG/JPEG, PNG, WEBP.
- Maksimal 5 MB per foto.
- Maksimal total 20 MB.
- Semua foto dalam satu request mewakili makanan/porsi yang sama.
Batas aktual mengikuti MAX_UPLOAD_IMAGES, MAX_IMAGE_SIZE_MB, dan MAX_TOTAL_UPLOAD_MB pada konfigurasi Django yang aktif.

Contoh perintah melalui Command Prompt (CMD):
curl -X POST http://127.0.0.1:8000/api/v1/analyze/ ^
  -F "images=@D:\foto\makanan-depan.jpg" ^
  -F "images=@D:\foto\makanan-samping.jpg"
Untuk menyimpan hasil ke riwayat akun, sertakan header Authorization: Bearer <ACCESS_TOKEN>. Tanpa token, analisis tetap dapat dilakukan tetapi hasil tidak disimpan ke riwayat pengguna.

Contoh respons HTTP 200 (sumber nutrisi dataset, pengguna login):
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
history_id bernilai ID riwayat bila analisis berhasil dan pengguna terautentikasi. Untuk analisis anonim, nilainya null. Nilai nutrisi serta ID di atas hanyalah contoh dokumentasi.

Sumber nutrisi:
nutrition_source	Kondisi	Isi nutrition
DATASET	Repository menemukan makanan (MATCHED)	Nutrisi dari dataset
AI_ESTIMATED	Makanan teridentifikasi, tidak cocok di dataset, dan AI menyediakan estimasi	Estimasi nutrisi AI
UNAVAILABLE	Data nutrisi dan estimasi tidak tersedia	null


matching.status menjelaskan kecocokan terhadap dataset, sedangkan nutrition_source menunjukkan asal nilai nutrisi. Oleh karena itu, matching.status = "NOT_MATCHED" dapat terjadi bersama nutrition_source = "AI_ESTIMATED".

Untuk AI_ESTIMATED, estimation_note memuat penjelasan bahwa nilai nutrisi merupakan perkiraan AI berbasis informasi visual, bukan nilai resmi dataset. Pada UNAVAILABLE, estimation_note dapat berisi alasan data tidak tersedia atau null ketika objek tidak dikenali (UNKNOWN). Frontend tidak boleh menganggap contoh nilai sebagai hasil aktual.
1.3 POST /api/v1/auth/register/
Mendaftarkan akun menggunakan RegisterSerializer dan model User Django yang sudah ada. Field wajib: username, email, dan password. Serializer menerapkan validasi password Django serta menolak email yang telah digunakan.

Contoh request:
{
  "username": "contoh_pengguna",
  "email": "contoh@example.com",
  "password": "<PASSWORD_PENGGUNA>"
}
Contoh respons sukses HTTP 201:
{
  "success": true,
  "message": "Registrasi berhasil.",
  "data": {
    "id": 1,
    "username": "contoh_pengguna",
    "email": "contoh@example.com"
  }
}
Password tidak dikembalikan dalam respons. Registrasi melalui API telah berhasil diuji langsung pada database PostgreSQL yang terhubung pada 6 November 2026, menggunakan akun pengujian.
1.4 POST /api/v1/auth/login/
Login menggunakan TokenObtainPairView dari SimpleJWT.

Contoh request:
{
  "username": "contoh_pengguna",
  "password": "<PASSWORD_PENGGUNA>"
}
Contoh respons sukses HTTP 200:
{
  "refresh": "<REFRESH_TOKEN>",
  "access": "<ACCESS_TOKEN>"
}
Respons login standar SimpleJWT tidak menggunakan pembungkus success/`data` seperti beberapa endpoint HealthCoach lainnya. Token di atas hanya placeholder.
1.5 POST /api/v1/auth/refresh/
Mengirim refresh token yang masih berlaku dan belum di-blacklist untuk memperoleh access token baru. Endpoint tidak membutuhkan access token di header.

Contoh request:
{
  "refresh": "<REFRESH_TOKEN>"
}
Contoh respons sukses HTTP 200:
{
  "access": "<ACCESS_TOKEN_BARU>"
}
Format respons mengikuti SimpleJWT dan konfigurasi aktif. Pengujian langsung melalui PowerShell pada 6 November 2026 membuktikan access token hasil refresh dapat dipakai kembali untuk GET /api/v1/auth/me/.

Konfigurasi JWT yang diperiksa pada 6 November 2026:
Pengaturan	Nilai
ACCESS_TOKEN_LIFETIME	5 menit
REFRESH_TOKEN_LIFETIME	1 hari
ROTATE_REFRESH_TOKENS	False
BLACKLIST_AFTER_ROTATION	False


BLACKLIST_AFTER_ROTATION = False tidak menonaktifkan proses blacklist pada endpoint logout. Refresh token tetap dapat diblacklist secara eksplisit saat logout.

Apabila access token kedaluwarsa, frontend sebaiknya mencoba endpoint refresh dengan refresh token yang masih berlaku, lalu mengulangi request dengan access token baru. Bila refresh token juga tidak valid, sudah kedaluwarsa, atau telah di-blacklist, pengguna perlu login kembali. Refresh otomatis di aplikasi mobile menjadi tanggung jawab Clau.
1.6 POST /api/v1/auth/logout/
Mengakhiri sesi dengan memasukkan refresh token valid ke blacklist SimpleJWT. Endpoint logout yang telah diperbarui menggunakan authentication_classes = [] dan permission_classes = [AllowAny], sehingga tidak memerlukan access token. Access token kedaluwarsa atau tidak valid dalam header tidak menghalangi logout.

Contoh request:
{
  "refresh": "<REFRESH_TOKEN>"
}
Contoh respons sukses HTTP 200:
{
  "success": true,
  "message": "Logout berhasil."
}
Ketentuan logout:
- Body wajib berisi refresh token yang valid.
- Refresh token kosong, tidak valid, atau kedaluwarsa ditolak.
- Setelah logout berhasil, refresh token di-blacklist dan tidak bisa dipakai lagi untuk meminta access token baru.
- Backend tidak lagi memeriksa kepemilikan refresh token terhadap request.user di endpoint ini karena access token tidak diwajibkan. Refresh token adalah kredensial bearer yang harus dijaga kerahasiaannya.
- Frontend menghapus access token dan refresh token dari penyimpanan lokal setelah logout berhasil.
- Access token yang pernah diterbitkan tidak otomatis dicabut oleh blacklist refresh token; access token tersebut mungkin masih dapat dipakai hingga kedaluwarsa.
Hasil uji langsung 6 November 2026: logout berhasil saat header mengandung access token tidak valid. Setelah logout, permintaan refresh dengan token yang sama menghasilkan HTTP 401, menandakan refresh token tidak lagi diterima.
1.7 GET /api/v1/auth/me/
Mengambil profil pengguna yang sedang login, berdasarkan access token JWT yang valid.

Header: Authorization: Bearer <ACCESS_TOKEN>

Contoh respons HTTP 200:
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
1.8 PATCH /api/v1/auth/me/
Memperbarui sebagian data profil pengguna yang sedang login, menggunakan model User Django yang tersedia. Endpoint ini tidak memerlukan model atau migrasi baru.

Autentikasi: access token JWT wajib.

Header:
Authorization: Bearer <ACCESS_TOKEN>
Content-Type: application/json
Field yang boleh diperbarui: username, email, first_name, last_name. Satu atau beberapa field dapat dikirim dalam satu request.

Contoh request:
{
  "first_name": "Dini",
  "last_name": "Pratiwi"
}
Contoh respons HTTP 200:
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
Validasi dan keamanan:
- Pengguna hanya dapat memperbarui data miliknya sendiri melalui request.user.
- Username dan email yang telah digunakan pengguna lain ditolak; pemeriksaan duplikasi tidak membedakan huruf besar/kecil.
- Email dinormalisasi menjadi huruf kecil.
- Field id bersifat read-only dan bukan input yang diizinkan untuk PATCH.
- Field sensitif seperti password, is_staff, dan is_superuser tidak diizinkan.
- Request kosong atau field di luar daftar yang diizinkan ditolak dengan HTTP 400.
- Request tanpa access token valid ditolak dengan HTTP 401 pada konfigurasi autentikasi yang diuji.
Pengujian langsung melalui PowerShell telah membuktikan PATCH nama depan/belakang berhasil, lalu nilai yang sama terbaca kembali menggunakan GET dengan access token hasil refresh pada koneksi PostgreSQL Supabase yang aktif.

Batas cakupan profil: field kesehatan tambahan seperti usia, tinggi badan, berat badan, atau target kesehatan belum termasuk endpoint ini. Jika diperlukan, koordinasikan kebutuhan struktur data dengan Yuli dan kebutuhan frontend dengan Clau sebelum menambah field/model.
2. API Riwayat Analisis
Model FoodAnalysisHistory disediakan oleh bagian database dengan field user, result (JSON), dan created_at. Endpoint di bawah menggunakan model itu tanpa mengubah struktur atau migrasinya.

Semua endpoint riwayat memerlukan autentikasi. Data dibatasi berdasarkan request.user; klien tidak dapat memilih pemilik riwayat melalui ID pengguna.
2.1 GET /api/v1/history/
Mengembalikan daftar riwayat pengguna yang sedang login, diurutkan dari data terbaru.

Contoh respons HTTP 200:
{
  "success": true,
  "data": [
    {
      "id": 12,
      "result": {
        "identification": {"food_name": "Nasi Goreng"},
        "nutrition_source": "DATASET"
      },
      "created_at": "2026-11-05T10:00:00+07:00"
    }
  ]
}
Field result sebenarnya menyimpan seluruh keluaran pipeline; contoh di atas disingkat. Jika belum ada riwayat, data berupa array kosong [].
2.2 GET /api/v1/history/{id}/
Mengambil satu riwayat milik pengguna yang login. Struktur data sama dengan satu item pada respons daftar riwayat. Jika ID tidak ditemukan atau milik pengguna lain, endpoint mengembalikan HTTP 404.
2.3 DELETE /api/v1/history/{id}/
Menghapus satu riwayat milik pengguna yang login.

Contoh respons HTTP 200:
{
  "success": true,
  "message": "Riwayat analisis berhasil dihapus."
}
ID milik pengguna lain tidak dapat dihapus dan menghasilkan HTTP 404.
2.4 Penyimpanan riwayat pada POST /api/v1/analyze/
Setelah pipeline berhasil:
1. Jika request.user.is_authenticated, backend menyimpan hasil pipeline dalam FoodAnalysisHistory dengan pemilik request.user.
2. ID catatan dikembalikan melalui meta.history_id.
3. Jika pengguna anonim, analisis tetap berjalan tanpa menyimpan riwayat dan history_id = null.
4. Jika pipeline gagal sebelum menghasilkan hasil, riwayat baru tidak dibuat.
Penyimpanan riwayat telah diuji menggunakan database pengujian Django dan mock pada pipeline. Pembacaan tabel riwayat di koneksi PostgreSQL Supabase juga telah berhasil, tetapi pengujian manual di percakapan Tiwi ini tidak membuktikan seluruh alur foto → Gemini asli → riwayat tersimpan secara end-to-end.
3. Penanganan Error dan Keamanan API
Backend menggunakan error handler yang membentuk JSON terstruktur untuk error yang ditangani.

Contoh error validasi HTTP 400:
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
Beberapa kode error analisis yang terdokumentasi:
- VALIDATION_ERROR: request tidak memenuhi validasi.
- GEMINI_NOT_CONFIGURED: konfigurasi Gemini belum tersedia.
- GEMINI_TIMEOUT: pemanggilan Gemini melewati batas waktu.
- GEMINI_QUOTA_EXCEEDED: kuota Gemini habis.
- GEMINI_ACCESS_DENIED: masalah akses layanan Gemini.
- GEMINI_INVALID_RESPONSE: respons Gemini tidak valid.
- GEMINI_UNAVAILABLE: layanan Gemini tidak tersedia.
- NUTRITION_DATA_UNAVAILABLE: sumber nutrisi bermasalah.
- TOKEN_NOT_VALID: token JWT tidak valid, kedaluwarsa, atau ditolak dalam konteks yang sesuai.
Endpoint yang membutuhkan login menolak request tanpa access token valid (umumnya HTTP 401 pada konfigurasi yang diuji). Riwayat milik pengguna lain dikembalikan sebagai 404. Validasi PATCH profil menolak field tidak dikenal, kosong, atau duplikasi dengan HTTP 400.

Ketentuan keamanan:
- Simpan API key, password database, dan Django secret key di environment atau secret manager, bukan dalam kode atau dokumentasi GitHub.
- Jangan mengunggah .env yang mengandung rahasia.
- Jangan mencantumkan password dan JWT asli pada dokumentasi, screenshot, atau log yang dibagikan.
- Jika kredensial pernah terpublikasi, cabut/rotasi kredensial terdampak dan koordinasikan penanganan riwayat Git dengan pemilik repository.
- Pengguna tidak dapat mengirim field user untuk mengambil atau menghapus riwayat orang lain.
- Refresh token harus diperlakukan sebagai rahasia karena pemegang token valid dapat menggunakannya untuk refresh atau pencabutan saat logout.
4. Alur Analisis Makanan
1. Pengguna memilih foto makanan melalui frontend.
2. Frontend mengirim POST /api/v1/analyze/ menggunakan multipart/form-data.
3. Backend memvalidasi jenis, jumlah, dan ukuran gambar.
4. Gemini Vision mengidentifikasi makanan dari satu atau beberapa sudut foto.
5. Repository nutrisi mencari kecocokan EXACT/`CANONICAL` terhadap dataset.
6. Jika MATCHED, nutrisi dari dataset digunakan (DATASET).
7. Jika NOT_MATCHED dan makanan teridentifikasi, AI dapat mencoba estimasi nutrisi (AI_ESTIMATED); jika tidak tersedia menjadi UNAVAILABLE.
8. Pipeline menyusun rekomendasi, sumber nutrisi, dan catatan analisis.
9. Jika pengguna login, backend API menyimpan hasil ke riwayat.
10. Backend mengembalikan respons JSON ke frontend.
Nilai AI_ESTIMATED adalah perkiraan berbasis informasi visual, bukan pengukuran resmi. Jika objek tidak dikenali (UNKNOWN), pipeline tidak menjalankan estimasi nutrisi berdasarkan kode yang sebelumnya diperiksa.
5. Integrasi Database PostgreSQL (Antarmuka Backend)
Database dan repository nutrisi merupakan bagian Yuli. Backend mengaksesnya melalui model/repository yang tersedia; frontend tidak seharusnya mengakses database secara langsung.

Backend sebelumnya mendukung sumber CSV dan PostgreSQL. Konfigurasi yang terverifikasi aktif pada 6 November 2026:
DB_ENGINE=postgresql
NUTRITION_SOURCE=database
NUTRITION_MODEL=api.Nutrition
Pemeriksaan Django menunjukkan engine PostgreSQL, host terisi, connection.ensure_connection() berhasil, dan migrate --check selesai tanpa error. Pembacaan data melalui ORM juga berhasil, dengan 9 pengguna, 1.346 data nutrisi, dan 1 riwayat saat pemeriksaan sebelum akun uji didaftarkan. Kemudian registrasi API menciptakan satu akun uji baru. Angka ini adalah snapshot pengujian, bukan total permanen.

Parameter koneksi dan password tetap disimpan secara privat pada environment. Perubahan konfigurasi, model, atau migrasi harus dikoordinasikan dengan Yuli.

Model FoodAnalysisHistory serta migrasinya berasal dari commit 2775d48 milik bagian database. Dokumentasi detail database tetap ada dalam DATABASE_DOCUMENTATION.md.
6. Panduan Integrasi Frontend React/Vite dan Mobile
Frontend HealthCoach berkomunikasi dengan Django REST Framework melalui HTTP JSON dan FormData. Integrasi otomatis refresh token untuk aplikasi mobile menjadi tanggung jawab Clau.
6.1 Mengirim foto dengan FormData
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
      result.error?.message || "Analisis makanan gagal. Silakan coba lagi."
    );
  }

  return result;
}
Gunakan formData.append("images", file) untuk tiap foto. Jangan menetapkan Content-Type manual pada FormData, karena browser akan membuat boundary multipart.
6.2 Membaca hasil JSON
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
Jika nutrition_source = AI_ESTIMATED, tampilkan keterangan bahwa angka merupakan estimasi serta estimation_note. Jika nutrition = null, tampilkan bahwa nutrisi belum tersedia, bukan angka contoh.
6.3 Validasi upload frontend dan backend
Pada pemeriksaan lama terhadap Analysis.jsx, pernah ditemukan perbedaan:
Pengaturan	Frontend saat pemeriksaan lama	Backend saat dokumentasi lama
Maksimal foto	3	5
Maksimal per foto	10 MB	5 MB
Format	JPG, PNG, WEBP	JPG, PNG, WEBP


Angka frontend tersebut merupakan catatan pemeriksaan sebelumnya, bukan verifikasi kondisi frontend terkini. Aturan UI dan API perlu diselaraskan dengan batas backend yang sedang aktif bersama Clau.
6.4 Loading, error, riwayat, dan refresh JWT
- Tampilkan loading selama analisis berlangsung dan hentikan setelah request selesai, baik berhasil maupun gagal.
- Tampilkan data nutrisi sesuai nutrition_source, serta pesan error API atau fallback yang aman.
- Sertakan access token pada GET/DELETE riwayat serta GET/PATCH profil.
- Ketika request terproteksi mendapat HTTP 401 karena access token kedaluwarsa, frontend dapat mencoba POST /auth/refresh/ sekali menggunakan refresh token yang masih valid, lalu mengulangi request dengan access token baru.
- Jika refresh gagal (misalnya refresh token sudah kedaluwarsa atau di-blacklist), hapus token lokal dan arahkan pengguna ke login.
- Untuk logout, kirim refresh token ke POST /auth/logout/; access token tidak diwajibkan. Setelah berhasil, hapus kedua token dari penyimpanan lokal.
- Hindari pengulangan refresh tanpa batas jika request terus menghasilkan 401.
Pada pemeriksaan frontend sebelumnya, Analysis.jsx pernah menggunakan data contoh dan setTimeout. Kondisi frontend terbaru tidak diverifikasi ulang dalam pekerjaan ini. Perubahan frontend/mobile tetap menjadi bagian Clau.
7. CORS
Dokumentasi terdahulu mencatat origin pengembangan lokal seperti:
http://localhost:3000
http://127.0.0.1:3000
http://localhost:5173
http://127.0.0.1:5173
Daftar tersebut berasal dari dokumentasi sebelumnya, bukan pemeriksaan ulang konfigurasi terkini. Jika origin frontend berbeda, periksa konfigurasi dan koordinasikan perubahan config/settings.py dengan Yuli.
8. Pengujian Backend & API
Pengujian otomatis menggunakan Django Test Framework, DRF APIClient, database pengujian, dan mock terhadap dependency eksternal pada skenario tertentu.

Perintah pengujian:
python HealthCoach\manage.py check
python HealthCoach\manage.py test api.tests.test_auth
python HealthCoach\manage.py test api.tests
Hasil terbaru pada 6 November 2026:
- python HealthCoach\manage.py check: tidak menemukan masalah.
- python HealthCoach\manage.py test api.tests.test_auth: 22/22 lulus.
- python HealthCoach\manage.py test api.tests: 79/79 lulus.
Cakupan otomatis:
- Validasi input foto, struktur respons, dan penanganan error.
- Endpoint dan pipeline untuk DATASET, AI_ESTIMATED, UNAVAILABLE, dan UNKNOWN menggunakan mock layanan eksternal.
- Autentikasi JWT, registrasi, login, refresh, dan logout.
- GET/PATCH profil, validasi username/email, penolakan field sensitif, dan pembatasan akses ke pengguna login.
- Logout tanpa access token, logout dengan access token kedaluwarsa, serta penolakan refresh token setelah logout.
- Endpoint riwayat hanya menerima pengguna login dan hanya mengakses data miliknya.
- Detail/penghapusan riwayat milik pengguna lain mengembalikan HTTP 404.
- Hasil analisis login tersimpan; hasil anonim tidak tersimpan; pipeline yang gagal tidak menambah riwayat.
Uji manual melalui PowerShell terhadap server Django dan koneksi PostgreSQL Supabase (6 November 2026):
- Registrasi akun uji berhasil (HTTP 201).
- Login JWT berhasil menghasilkan access token dan refresh token.
- GET profil akun uji berhasil.
- PATCH nama depan/belakang berhasil.
- GET profil menggunakan access token hasil refresh menampilkan kembali perubahan, memverifikasi pembacaan setelah penyimpanan.
- Refresh menghasilkan access token baru yang dapat mengakses profil.
- Logout berhasil walau header Authorization berisi access token tidak valid.
- Refresh token yang telah digunakan untuk logout kemudian ditolak oleh endpoint refresh (HTTP 401).
Pengujian manual di atas hanya menggunakan akun pengujian, bukan mengubah profil pengguna lain. Uji otomatis tidak dengan sendirinya membuktikan seluruh layanan eksternal berjalan end-to-end pada lingkungan produksi; integrasi mobile dan Gemini asli tetap harus diverifikasi sesuai tanggung jawab tim.
9. Pembagian Tanggung Jawab dan Koordinasi
Tiwi — Backend & API: endpoint, autentikasi, profil pengguna, validasi, otorisasi, kontrak respons, penghubung pipeline, penyimpanan hasil melalui API, pengujian, dan dokumentasi. Autentikasi terkait Issue #54; integrasi frontend–backend sebelumnya terkait Issue #55.

Yuli — Database dan dashboard Django: model, migrasi, koneksi Supabase, repository nutrisi, dashboard, dan dokumentasi database.

Aril — AI: identifikasi Gemini Vision, estimasi nutrisi, dan rekomendasi.

Clau — Frontend: React/Vite dan mobile, formulir profil, alur request, penyimpanan token sisi klien, refresh otomatis, dan tampilan analisis serta riwayat.

Jangan mengubah api/models.py, migrasi, config/settings.py, config/urls.py, atau folder dashboard/ tanpa koordinasi. Pekerjaan Tiwi dilakukan pada branch fitur. PR tidak wajib jika tim memang menyepakati alur tanpa PR; jangan melakukan push/merge langsung ke main tanpa kesepakatan tim. Pesan commit Tiwi selanjutnya menggunakan bahasa Indonesia.
10. Catatan Perkembangan
- PR #68 dan #69 milik Tiwi telah di-merge. PR #69 menambahkan empat pengujian endpoint–pipeline untuk sumber nutrisi.
- Commit 2775d48 dari Yuli menambahkan FoodAnalysisHistory, migrasi, dashboard, dan dokumentasi database.
- PR #70 dari branch feature/backend-api-history-tiwi telah di-merge ke main, berisi daftar/detail/hapus riwayat dan penyimpanan hasil analisis oleh API.
- Main lokal telah diperbarui sampai commit b3847b7 (perbaikan yuli) sebelum pengerjaan fitur profil.
- Pekerjaan fitur profil dan logout berlangsung pada branch feature/backend-api-profil-tiwi.
- Fitur terbaru: PATCH profil pengguna dengan validasi, dan logout berbasis refresh token meskipun access token tidak valid/kedaluwarsa.
- Seluruh 79/79 pengujian Backend & API lulus; pengujian manual registrasi, login, profil, refresh, dan logout pada koneksi Supabase juga berhasil.
- Pada saat dokumen ini disusun, perubahan profil/logout masih berada di branch lokal dan belum dinyatakan sudah di-commit atau di-push.
- Refresh token otomatis dan penyempurnaan integrasi pada frontend mobile merupakan kelanjutan pekerjaan Clau.
Dokumen ini berfokus pada kontrak API dan hasil pengujian yang telah diketahui. Tidak memuat password, API key, token nyata, atau detail privat koneksi database.