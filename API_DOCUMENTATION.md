Dokumentasi Backend & API HealthCoach
Dokumentasi ini menjelaskan endpoint Backend & API HealthCoach, analisis makanan melalui Gemini AI dan repository nutrisi, autentikasi JWT, penyimpanan riwayat analisis, serta panduan integrasi frontend React/Vite dengan backend Django REST Framework.

Pembaruan dokumentasi: 5 November 2026
Base URL pengembangan lokal: http://127.0.0.1:8000/api/v1/
Lingkup: Backend & API (Tiwi). Implementasi model dan koneksi database tetap dikelola bagian database; logika Gemini tetap dikelola bagian AI.
Contoh request dan respons di dokumen ini bersifat ilustratif, bukan keluaran layanan Gemini atau Supabase secara langsung. Perilaku API mengikuti kode dan konfigurasi environment yang aktif.

1. Daftar endpoint API
Semua path berikut berada di bawah prefix /api/v1/.
Method	Endpoint	Perlu login	Fungsi
GET	health/	Tidak	Memeriksa status backend
POST	analyze/	Opsional	Analisis foto; riwayat disimpan bila pengguna login
POST	auth/register/	Tidak	Mendaftarkan pengguna
POST	auth/login/	Tidak	Mendapatkan token JWT
POST	auth/refresh/	Tidak	Memperbarui access token
POST	auth/logout/	Ya	Menonaktifkan refresh token
GET	auth/me/	Ya	Mengambil profil akun login
GET	history/	Ya	Daftar riwayat milik pengguna login
GET	history/{id}/	Ya	Detail riwayat milik pengguna login
DELETE	history/{id}/	Ya	Menghapus riwayat milik pengguna login


Endpoint riwayat belum menyediakan POST langsung, PUT, atau PATCH. Pembuatan riwayat dilakukan oleh endpoint analisis yang berhasil untuk pengguna login.
1.1 GET /api/v1/health/
Memeriksa apakah backend dapat diakses.

Contoh respons HTTP 200:
{
  "success": true,
  "status": "ok",
  "service": "HealthCoach API"
}
1.2 POST /api/v1/analyze/
Menerima foto makanan, memanggil pipeline identifikasi Gemini Vision, mencari nutrisi melalui repository, mencoba estimasi AI apabila diperlukan, dan menghasilkan rekomendasi.

Request: multipart/form-data dengan field images (satu atau beberapa file foto dari satu makanan/porsi). Field lama image masih didukung untuk kompatibilitas.

Ketentuan upload yang dicatat dalam dokumentasi sebelumnya:
- Jumlah foto: 1–5.
- Format: JPG/JPEG, PNG, WEBP.
- Ukuran maksimal: 5 MB per foto.
- Total maksimal: 20 MB.
- Semua foto dalam satu request mewakili makanan/porsi yang sama.
Batas aktual berasal dari konfigurasi MAX_UPLOAD_IMAGES, MAX_IMAGE_SIZE_MB, dan MAX_TOTAL_UPLOAD_MB pada environment Django, sehingga perlu disesuaikan bila konfigurasinya berubah.

Contoh curl melalui Command Prompt Windows (CMD):
curl -X POST http://127.0.0.1:8000/api/v1/analyze/ ^
  -F "images=@D:\foto\makanan-depan.jpg" ^
  -F "images=@D:\foto\makanan-samping.jpg"
Untuk menyimpan riwayat analisis ke akun, sertakan access token JWT pada header Authorization: Bearer <ACCESS_TOKEN>. Tanpa token, analisis tetap dapat dilakukan, tetapi riwayat tidak disimpan ke akun.

Contoh respons sukses HTTP 200 (data nutrisi dari dataset, pengguna login):
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
history_id hanya bernilai ID riwayat jika analisis berhasil dan request terautentikasi. Untuk analisis anonim nilainya null. Contoh ID di atas bukan ID database aktual.

Sumber nutrisi:
nutrition_source	Kondisi	Isi nutrition
DATASET	Repository menemukan makanan (MATCHED)	Nutrisi dari dataset
AI_ESTIMATED	Tidak cocok di dataset, makanan teridentifikasi, dan AI menyediakan estimasi	Nilai estimasi AI
UNAVAILABLE	Nutrisi dataset atau estimasi tidak tersedia	null


Penting: matching.status menjelaskan kecocokan terhadap dataset, sedangkan nutrition_source menunjukkan asal nilai nutrisi. Karena itu matching.status = "NOT_MATCHED" dapat terjadi bersamaan dengan nutrition_source = "AI_ESTIMATED".

Untuk AI_ESTIMATED, estimation_note berisi penjelasan/peringatan bahwa nilai adalah estimasi AI berdasarkan konteks visual, bukan angka nutrisi resmi dataset. Untuk UNAVAILABLE, estimation_note dapat berupa alasan estimasi tidak tersedia atau null pada kondisi UNKNOWN. Frontend tidak boleh menampilkan angka contoh sebagai data aktual.
1.3 POST /api/v1/auth/register/
Mendaftarkan pengguna melalui serializer registrasi yang sudah tersedia.

Contoh request (field wajib mengikuti RegisterSerializer pada kode aktif):
{
  "username": "contoh_pengguna",
  "email": "contoh@example.com",
  "password": "<PASSWORD_PENGGUNA>"
}
Struktur respons sukses HTTP 201:
{
  "success": true,
  "message": "Registrasi berhasil.",
  "data": {
    "id": 1,
    "username": "contoh_pengguna",
    "email": "contoh@example.com"
  }
}
Contoh request di atas tidak menggantikan aturan validasi atau kemungkinan field tambahan pada RegisterSerializer.
1.4 POST /api/v1/auth/login/
Login menggunakan SimpleJWT TokenObtainPairView.

Request:
{
  "username": "contoh_pengguna",
  "password": "<PASSWORD_PENGGUNA>"
}
Contoh respons sukses:
{
  "refresh": "<REFRESH_TOKEN>",
  "access": "<ACCESS_TOKEN>"
}
Respons default login SimpleJWT tidak menggunakan pembungkus success/`data` seperti beberapa endpoint HealthCoach lainnya. Token contoh bukan token sungguhan.
1.5 POST /api/v1/auth/refresh/
Mengirim refresh token untuk memperoleh access token baru.
{
  "refresh": "<REFRESH_TOKEN>"
}
Format respons mengikuti konfigurasi SimpleJWT yang aktif.
1.6 POST /api/v1/auth/logout/
Memerlukan access token di header Authorization dan refresh token di body. Backend memeriksa kepemilikan refresh token kemudian memasukkannya ke blacklist.

Request:
{
  "refresh": "<REFRESH_TOKEN>"
}
Respons sukses HTTP 200:
{
  "success": true,
  "message": "Logout berhasil."
}
1.7 GET /api/v1/auth/me/
Mengambil profil pengguna yang sudah login.

Contoh respons HTTP 200:
{
  "success": true,
  "data": {
    "id": 1,
    "username": "contoh_pengguna",
    "email": "contoh@example.com"
  }
}
2. API Riwayat Analisis
Model FoodAnalysisHistory sudah disediakan oleh bagian database, dengan field user, result (JSON), dan created_at. Endpoint API di bawah menggunakan model tersebut tanpa mengubah struktur model atau migrasi.

Semua endpoint riwayat memerlukan autentikasi. Data selalu difilter berdasarkan request.user; klien tidak dapat menentukan pemilik riwayat melalui ID pengguna dalam request.
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
result sebenarnya menyimpan seluruh hasil pipeline, bukan hanya dua field yang dipotong dalam contoh di atas. Jika belum ada riwayat, data berupa array kosong [].
2.2 GET /api/v1/history/{id}/
Menampilkan detail satu riwayat milik pengguna yang login. Struktur data sama dengan satu item pada daftar riwayat.

Jika ID tidak ditemukan atau merupakan milik pengguna lain, endpoint mengembalikan HTTP 404 agar riwayat pengguna lain tidak terbuka.
2.3 DELETE /api/v1/history/{id}/
Menghapus satu riwayat milik pengguna yang login.

Respons sukses HTTP 200:
{
  "success": true,
  "message": "Riwayat analisis berhasil dihapus."
}
ID yang bukan milik pengguna login tidak dapat dihapus dan menghasilkan HTTP 404.
2.4 Penyimpanan riwayat pada POST /api/v1/analyze/
Setelah pipeline sukses:
1. Jika request.user.is_authenticated benar, backend menyimpan hasil pipeline dalam FoodAnalysisHistory dengan pemilik request.user.
2. ID catatan dikembalikan melalui meta.history_id.
3. Jika pengguna anonim, analisis tetap berjalan tanpa pembuatan riwayat dan history_id bernilai null.
4. Jika pipeline gagal sebelum menghasilkan data, riwayat baru tidak dibuat.
Implementasi ini tidak mengubah model milik bagian database. Keberhasilan penyimpanan telah diuji menggunakan database pengujian Django dan pipeline yang di-mock, bukan pengujian koneksi langsung ke Supabase produksi.
3. Penanganan Error dan Keamanan API
Backend menggunakan error handler yang membentuk respons JSON terstruktur untuk error yang ditangani.

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
Beberapa kode error pada layanan analisis:
- VALIDATION_ERROR: request tidak memenuhi validasi.
- GEMINI_NOT_CONFIGURED: konfigurasi Gemini belum tersedia.
- GEMINI_TIMEOUT: proses Gemini melebihi batas waktu.
- GEMINI_QUOTA_EXCEEDED: kuota Gemini habis.
- GEMINI_ACCESS_DENIED: autentikasi/otorisasi layanan Gemini bermasalah.
- GEMINI_INVALID_RESPONSE: respons Gemini tidak valid.
- GEMINI_UNAVAILABLE: layanan Gemini tidak tersedia.
- NUTRITION_DATA_UNAVAILABLE: sumber nutrisi bermasalah.
Endpoint yang membutuhkan login menolak akses anonim (status dapat 401 atau 403 bergantung konfigurasi autentikasi). Detail riwayat yang bukan milik pengguna dikembalikan sebagai 404.

Ketentuan keamanan:
- Simpan API key, password database, dan Django secret key di environment/secret manager yang sesuai, bukan di kode atau dokumentasi GitHub.
- Jangan mengunggah .env berisi rahasia ke repository.
- Jangan mencantumkan token asli pada dokumentasi atau screenshot.
- Jika kredensial pernah terpublikasi, cabut/rotasi kredensial terdampak dan koordinasikan penanganan riwayat Git dengan pemilik repository.
- Pengguna tidak dapat mengirim field user untuk mengambil atau menghapus riwayat orang lain.
4. Alur Analisis Makanan
1. Pengguna memilih foto makanan melalui frontend.
2. Frontend mengirim POST /api/v1/analyze/ dengan multipart/form-data.
3. Backend memvalidasi jenis, jumlah, dan ukuran gambar.
4. Gemini Vision mengidentifikasi makanan dari satu atau beberapa sudut foto.
5. Repository nutrisi mencari EXACT/CANONICAL matching terhadap dataset.
6. Jika MATCHED, data nutrisi diambil dari dataset (DATASET).
7. Jika NOT_MATCHED dan makanan teridentifikasi, sistem dapat mencoba estimasi nutrisi AI. Jika tersedia, sumbernya AI_ESTIMATED; jika tidak, UNAVAILABLE.
8. Pipeline menyusun rekomendasi, informasi sumber nutrisi, dan catatan hasil analisis.
9. Untuk pengguna login, hasil disimpan ke riwayat melalui backend API.
10. Backend mengembalikan JSON ke frontend untuk ditampilkan.
Nilai AI_ESTIMATED adalah perkiraan berbasis informasi visual, bukan hasil pengukuran resmi. Jika objek tidak dikenali (UNKNOWN), pipeline tidak menjalankan estimasi nutrisi berdasarkan kode yang telah diperiksa.
5. Integrasi Database PostgreSQL (Informasi Antarmuka Backend)
Bagian database dan repository nutrisi menjadi tanggung jawab Yuli. Backend mengakses data melalui repository yang tersedia; frontend tidak boleh mengakses database langsung.

Backend pernah mendukung sumber nutrisi CSV dan PostgreSQL. Konfigurasi yang terdokumentasi untuk penggunaan PostgreSQL adalah:
DB_ENGINE=postgresql
NUTRITION_SOURCE=database
NUTRITION_MODEL=api.Nutrition
Parameter koneksi dan password disimpan secara privat pada environment, bukan pada dokumentasi GitHub. Perubahan konfigurasi, model, atau migrasi harus dikoordinasikan dengan penanggung jawab database.

Model riwayat FoodAnalysisHistory dan migrasinya dibuat pada commit 2775d48 oleh bagian Backend & Database. Dokumentasi detail database tetap berada pada DATABASE_DOCUMENTATION.md.
6. Panduan Integrasi Frontend React/Vite
Frontend HealthCoach menggunakan React/Vite dan berkomunikasi dengan Django REST Framework menggunakan HTTP JSON dan FormData.
6.1 Mengirim foto menggunakan FormData
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
Gunakan formData.append("images", file) untuk setiap gambar. Jangan mengatur Content-Type secara manual ketika menggunakan FormData, karena browser harus menambahkan boundary multipart.
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
Jika nutrition_source bernilai AI_ESTIMATED, tampilkan penanda bahwa nilai merupakan estimasi beserta estimation_note. Jika nutrition bernilai null, tampilkan keterangan bahwa nutrisi belum tersedia, bukan angka contoh.
6.3 Validasi upload frontend dan backend
Pada pemeriksaan frontend Analysis.jsx yang terdokumentasi sebelumnya, terdapat perbedaan:
Pengaturan	Frontend saat pemeriksaan sebelumnya	Backend saat dokumentasi sebelumnya
Jumlah foto maksimal	3	5
Maksimal ukuran per foto	10 MB	5 MB
Format	JPG, PNG, WEBP	JPG, PNG, WEBP


Angka frontend pada tabel tersebut merupakan hasil pemeriksaan sebelumnya, bukan verifikasi kondisi frontend terkini. Aturan UI perlu diselaraskan dengan batas backend yang berlaku bersama Clau.
6.4 Loading, error, dan akses riwayat
- Tampilkan loading selama request analisis berlangsung.
- Tampilkan respons nutrisi sesuai nutrition_source.
- Tampilkan pesan error dari respons API atau pesan fallback yang aman.
- Hentikan loading ketika request selesai, termasuk saat terjadi kegagalan.
- Sertakan access token untuk mengakses GET /history/, GET /history/{id}/, dan DELETE /history/{id}/.
- Jika token tidak ada atau kedaluwarsa, arahkan pengguna ke alur autentikasi yang sesuai.
Pada pemeriksaan frontend sebelumnya, Analysis.jsx pernah menggunakan data contoh dan setTimeout. Kondisi frontend terkini belum diperiksa ulang dalam pekerjaan Backend & API ini; penyelesaiannya menjadi bagian frontend Clau.
7. CORS
Dalam dokumentasi sebelumnya, backend menyediakan CORS untuk pengembangan lokal dengan origin seperti:
http://localhost:3000
http://127.0.0.1:3000
http://localhost:5173
http://127.0.0.1:5173
Jika frontend menggunakan origin berbeda, konfigurasi harus diperiksa dan perubahan pada config/settings.py dikoordinasikan lebih dahulu. Daftar ini berasal dari dokumentasi sebelumnya, bukan pemeriksaan ulang konfigurasi terbaru.
8. Pengujian Backend & API
Pengujian menggunakan Django Test Framework, DRF APIClient, dan mock untuk dependency eksternal pada skenario tertentu.

Perintah:
python HealthCoach\manage.py check
python HealthCoach\manage.py test api.tests
Hasil terakhir yang dilaporkan pada 5 November 2026: 70/70 pengujian backend lulus, dan system check tidak menemukan masalah.

Cakupan pengujian yang telah dikembangkan:
- Validasi input foto, struktur respons, dan pemetaan error API.
- Integrasi endpoint–pipeline untuk DATASET, AI_ESTIMATED, UNAVAILABLE, dan UNKNOWN dengan mock layanan eksternal.
- Endpoint riwayat membutuhkan autentikasi dan hanya menampilkan data milik pengguna login.
- Detail dan penghapusan riwayat pengguna lain menghasilkan 404.
- Hasil analisis pengguna login disimpan; hasil anonim tidak disimpan; pipeline yang gagal tidak menghasilkan riwayat.
Tes di atas tidak otomatis membuktikan bahwa seluruh layanan eksternal berjalan end-to-end di lingkungan produksi. Pengujian frontend dan integrasi lintas tim dilakukan sesuai tugas masing-masing.
9. Pembagian Tanggung Jawab dan Koordinasi
Tiwi — Backend & API: endpoint, validasi, autentikasi dan otorisasi API, kontrak respons, integrasi endpoint, penyimpanan hasil lewat API, pengujian, dan dokumentasi. Pekerjaan autentikasi pernah dibahas sebagai Issue #54; integrasi frontend–backend pernah dibahas sebagai Issue #55.

Yuli — Database dan repository nutrisi: model, migrasi, koneksi Supabase, repository nutrisi, serta dashboard Django yang sudah dikerjakan.

Aril — AI: Gemini Vision, estimasi nutrisi, dan rekomendasi.

Clau — Frontend: UI React/Vite, pengiriman request, dan tampilan hasil serta riwayat.

Jangan mengubah api/models.py, migrasi, config/settings.py, config/urls.py, atau dashboard tanpa koordinasi dengan penanggung jawabnya. Jangan langsung push ke main; gunakan branch fitur dan Pull Request.
10. Catatan Perkembangan
- PR #68 dan #69 milik Tiwi sudah di-merge. PR #69 menambahkan empat pengujian endpoint–pipeline untuk sumber nutrisi.
- Commit 2775d48 dari Yuli menambahkan FoodAnalysisHistory, migrasi, dashboard, dan dokumentasi database.
- Pada branch feature/backend-api-history-tiwi, Tiwi menambahkan API daftar/detail/hapus riwayat dan penyimpanan hasil analisis melalui FoodAnalysisView.
- Pengujian terbaru mencapai 70/70 lulus. Pada saat dokumentasi disusun, pekerjaan API riwayat belum dinyatakan sudah di-commit/di-merge; status Git terakhir masih menunjukkan perubahan lokal.
- Integrasi frontend/backend end-to-end belum dikonfirmasi selesai dalam tahap ini. Dokumentasi integrasi Issue #55 tetap relevan untuk koordinasi dengan Clau.
Dokumentasi ini fokus pada kontrak API dan hasil pengujian yang telah tersedia; tidak menyertakan password, key, atau detail koneksi privat.