# Laporan Kuis: Interconnecting between Digital Awareness and Application Design

* **Mata Kuliah**: Internet Programming II (PIE 1516)
* **Program Studi**: Teknologi Rekayasa Internet (IET POLINELA)
* **Nama**: Claudia Cyntia Bella
* **NPM**: 24782040

---

## Bagian 1. Identitas dan Topik Proyek Aplikasi

* **Nama Aplikasi**: HealthCoach
* **Deskripsi Singkat & Tujuan Utama Aplikasi**: 
  HealthCoach adalah platform aplikasi berbasis *client-server* yang dirancang untuk mengotomatiskan proses pencatatan dan analisis nutrisi harian pengguna melalui pendekatan visual. Masalah utama yang ingin kami selesaikan adalah kerumitan dan inefisiensi dalam pencatatan kalori manual. Melalui aplikasi ini, foto makanan yang diunggah akan diproses oleh *backend* Django, diidentifikasi menggunakan model kecerdasan buatan Gemini Vision, dan dicocokkan dengan *database* PostgreSQL. Setelah data nutrisi faktual ditarik, Gemini LLM akan memformulasikan rekomendasi gizi yang personal. Tujuan akhirnya adalah menciptakan ekosistem pemantauan kesehatan yang praktis dan cerdas dalam satu alur kerja.
* **Target Pengguna Utama**: 
  Individu yang memiliki kepedulian terhadap pola makan dan gaya hidup sehat, pegiat kebugaran (*fitness enthusiast*), serta masyarakat umum (termasuk pekerja dengan mobilitas tinggi) yang membutuhkan instrumen cepat untuk mengecek asupan kalori dan makronutrisi harian tanpa harus melakukan riset data secara manual.

---

## Bagian 2. Resume Modul Digital Awareness

### 1. Modul 1: There's a whole new world out there!
Modul ini menyoroti pergeseran peradaban manusia dari era analog menuju ekosistem digital yang serba terhubung. Pemanfaatan teknologi komputasi dan otomatisasi tidak sekadar mempercepat penyelesaian tugas-tugas rutin, melainkan mendefinisikan ulang cara manusia bekerja, berinteraksi, dan mengelola informasi menjadi jauh lebih efisien, terukur, dan terintegrasi.

### 2. Modul 2: You'll Need Some Basic Tools
Untuk dapat berpartisipasi secara aktif dan aman di dunia digital, pengguna wajib memahami arsitektur dasar perangkat keras (*hardware*), sistem operasi (*operating system*), serta manajemen penyimpanan data (*file/folder management*). Modul ini juga sangat menekankan urgensi keamanan siber tingkat dasar, terutama krusialnya merancang kata sandi (*password*) yang kompleks dan unik guna memitigasi risiko peretasan akun.

### 3. Modul 3: This is how you get around and find what you're looking for
Fokus modul ini adalah literasi informasi dalam menavigasi *World Wide Web* menggunakan *browser* dan *search engine*. Selain menguasai teknik pencarian data secara spesifik, pengguna dan pengembang dituntut memiliki kesadaran hukum terkait kekayaan intelektual digital. Hal ini mencakup kemampuan membedakan materi yang dilindungi hak cipta eksklusif (*copyright*) dengan aset digital yang berlisensi terbuka (*open-source* atau *public domain*).

### 4. Modul 4: It just keeps getting better
Perkembangan teknologi *Artificial Intelligence* (AI) dan *Machine Learning* membawa transformasi masif yang mempermudah otomatisasi tugas kompleks. Namun, kemajuan ini harus senantiasa diimbangi oleh penerapan etika berinternet (*netiquette*) yang santun serta tanggung jawab moral dari pengembang agar *output* dari algoritma AI tidak menyesatkan, diskriminatif, atau merugikan pihak lain.

### 5. Modul 5: Even Though It's Digital, It is Real, With Real Consequences
Aktivitas di dunia maya, sekecil apa pun, akan meninggalkan jejak digital (*digital footprint*) yang bersifat abadi dan berdampak langsung pada kehidupan nyata. Modul ini mengajarkan prinsip krusial dalam melindungi Data Pribadi Sensitif (*Personally Identifiable Information* / PII), menolak segala bentuk *cyberbullying*, serta membekali diri dengan tingkat kewaspadaan tinggi terhadap ancaman rekayasa sosial (*social engineering*), *phishing*, dan *fraud*.

### 6. Modul 6: Learn About Anything and Everything
Modul ini membekali pola pikir penyelesaian masalah (*troubleshooting mindset*) tingkat dasar ketika perangkat, jaringan, atau aplikasi mengalami malfungsi teknis (*error*). Selain itu, ditekankan pula pentingnya mentalitas pembelajaran berkelanjutan (*continuous learning*) untuk menjembatani kesenjangan keterampilan (*skills gaps*) di tengah industri teknologi yang terus berevolusi dengan sangat cepat.

---

## Bagian 3. Hubungan dan Implementasi pada Topik Proyek

### 1. Transformasi Digital dan Efisiensi Pengguna
* **Proses Konvensional (Analog)**: Sebelumnya, untuk melacak nutrisi, pengguna harus melalui proses berulang yang tidak efisien: menimbang porsi makanan secara fisik, mencari bahan di buku atau mesin pencari satu per satu, dan mengkalkulasi total makronutrisi (protein, lemak, karbohidrat) secara manual menggunakan kalkulator.
* **Simplifikasi Digital pada HealthCoach**: Rantai proses panjang tersebut disederhanakan menjadi satu aksi unggah (*upload*) foto melalui antarmuka *frontend*. Data akan diteruskan melalui REST API menuju sistem kami untuk dianalisis. Namun, kami menerapkan batasan teknis (*limitation*) yang jujur: sistem tidak dapat mengukur metrik fisik seperti gramasi atau berat pasti secara visual. Oleh karena itu, edukasi selalu diberikan di layar bahwa angka yang tertera merupakan "Estimasi Berdasarkan Porsi Standar", sehingga pengguna tetap memiliki ekspektasi yang rasional terhadap kemampuan teknologi.

### 2. Struktur Penyimpanan File & Keamanan Kata Sandi
Dalam fase *Proof of Concept* saat ini, arsitektur HealthCoach berfokus pada interaksi instan (*frictionless experience*). Pengguna tidak diwajibkan melewati birokrasi pendaftaran akun, dan *input* foto diproses langsung secara *real-time* di memori *backend* tanpa harus mewajibkan pengguna mengatur hierarki *folder* penyimpanan.
Apabila pada fase pengembangan selanjutnya fitur autentikasi pengguna (*user login*) diimplementasikan, kami akan menerapkan standar keamanan industri. Kata sandi tidak akan pernah disimpan dalam bentuk teks biasa (*plain text*), melainkan diproses menggunakan algoritma *hashing* pada *database*. Di sisi antarmuka, sistem akan memvalidasi *input* agar pengguna wajib merangkai kombinasi kata sandi yang panjang, mengandung karakter unik, alfanumerik, dan sulit ditebak.

### 3. Fitur Pencarian & Pengelolaan Lisensi Aset
Pencarian informasi makanan saat ini dieksekusi secara otomatis (*automated query*) di sisi server. *Backend* Django akan menggunakan teks *output* dari Gemini Vision sebagai parameter pencarian ke dalam tabel *database* PostgreSQL. 
Aplikasi kami dibangun dengan merangkai berbagai komponen eksternal yang dihormati lisensi penggunaannya:
* **Django (Backend & REST API)**: Lisensi bebas pakai berbasis *Open-Source* (BSD License).
* **PostgreSQL (Database Management)**: Lisensi *Open-Source*.
* **Gemini Vision & Gemini LLM**: API Layanan Komersial (*Commercial API*) yang kami gunakan dengan tunduk secara penuh pada aturan *Terms of Service* (ToS) dari Google Cloud.
* **Indonesian Food and Drink Nutrition Dataset**: Dataset terbuka (*Open Data* dari Kaggle) yang kami gunakan sebagai *knowledge base* awal yang terstruktur.

### 4. Etika Digital & AI yang Bertanggung Jawab
Kami sangat menyadari fenomena *AI Hallucination* (AI mengarang fakta). Untuk memastikan penggunaan kecerdasan buatan yang etis dan kredibel, kami menerapkan segregasi fungsi yang tegas: Gemini Vision **hanya** bertugas melakukan klasifikasi gambar (*image recognition*). Gemini dilarang keras menebak angka nutrisi dari nol. Semua nilai kalori dan makronutrisi ditarik murni dari tabel *database* internal kami yang berbasis data penelitian. 
Selain itu, kami mengakui bahwa kualitas foto (gelap, buram, atau makanan teraduk) akan menurunkan tingkat kepercayaan (*confidence score*) dari AI. Jika tingkat kemiripan rendah atau data tidak ada di *database*, sistem akan menolak memberikan kesimpulan palsu dan akan menginformasikan keterbatasan tersebut secara transparan kepada *end-user*.

### 5. Perlindungan Data Sensitif (PII) & Antisipasi Siber
Kami mengadopsi prinsip Minimasi Data (*Data Minimization*). Sistem saat ini hanya meminta izin untuk memproses foto *input*, tanpa mengumpulkan data rekam medis, NIK, atau instrumen finansial apa pun. Transmisi data dari *frontend* ke *backend* akan diamankan menggunakan protokol jaringan terenkripsi (HTTPS) agar tidak mudah di-*sniffing* oleh pihak ketiga. 
Dalam rangka melindungi pengguna dari ancaman *social engineering* atau *phishing* yang mengatasnamakan aplikasi kami, *platform* akan menyertakan imbauan berkala bahwa tim administrator HealthCoach tidak akan pernah meminta kredensial akun pengguna melalui saluran komunikasi apa pun.

### 6. Troubleshooting Mandiri & Pesan Error Ramah Pengguna
Mengingat arsitektur HealthCoach sangat bergantung pada ketersediaan *Application Programming Interface* (API) eksternal dan stabilitas jaringan (*client-server communication*), kami telah mengantisipasi terjadinya kegagalan sistem (*system failure*). Kami tidak akan memunculkan *stack trace* atau kode *error server* murni (seperti `500 Internal Server Error` atau `503 Service Unavailable`) yang akan membingungkan pengguna awam. Sebagai gantinya, *error handling* akan memunculkan panduan *troubleshooting* yang empati:

* **Skenario 1: API Server Sibuk (Koneksi Timeout)**
  >  **Layanan Analisis Sedang Padat**
  > Saat ini server kami sedang menangani antrean yang tinggi atau koneksi Anda terputus. Mohon periksa stabilitas jaringan internet Anda, tunggu beberapa saat, lalu ketuk tombol **[Coba Ulang]**.
* **Skenario 2: Resolusi atau Pencahayaan Foto Ekstrem**
  >  **Objek Sulit Diidentifikasi**
  > Kualitas gambar sangat memengaruhi akurasi AI. Makanan pada foto ini belum terlihat jelas karena buram atau kurang cahaya. Mohon pastikan pencahayaan cukup dan coba unggah kembali.
* **Skenario 3: Null Data (Tidak Ada di Database)**
  >  **Nutrisi Belum Tersedia**
  > AI berhasil mengidentifikasi jenis makanan Anda, namun rincian nutrisi absolutnya belum terekam di dalam basis data HealthCoach saat ini.