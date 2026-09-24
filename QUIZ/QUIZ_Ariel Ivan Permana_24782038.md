# QUIZ — INTERCONNECTING BETWEEN DIGITAL AWARENESS AND APPLICATION DESIGN

**Mata Kuliah:** Internet Programming II  
**Program Studi:** Teknologi Rekayasa Internet  
**Nama Aplikasi:** HealthCoach  
**Nama:** Ariel Ivan Permana  
**NPM:** 24782038

---

# BAGIAN 1. IDENTITAS DAN TOPIK PROYEK APLIKASI

## 1. Nama Aplikasi

HealthCoach

## 2. Deskripsi Singkat dan Tujuan Utama Aplikasi

HealthCoach merupakan aplikasi yang membantu pengguna memperoleh informasi mengenai makanan dan kandungan nutrisinya dengan memanfaatkan foto makanan. Masalah yang ingin diselesaikan adalah proses mengetahui informasi makanan yang biasanya masih dilakukan secara manual. Pengguna harus mencari nama makanan terlebih dahulu, kemudian mencari informasi seperti kalori, protein, lemak, dan karbohidrat dari sumber yang berbeda.

Pada HealthCoach, proses tersebut dibuat lebih sederhana. Pengguna memberikan foto makanan melalui aplikasi. Foto tersebut diproses menggunakan Gemini Vision untuk mengenali jenis makanan. Nama makanan hasil identifikasi kemudian digunakan oleh backend untuk mencari data nutrisi dari Indonesian Food and Drink Nutrition Dataset. Setelah data nutrisi ditemukan, Gemini digunakan kembali untuk memberikan rekomendasi berdasarkan informasi tersebut.

Dengan demikian, tujuan HealthCoach bukan hanya mengenali makanan dari gambar, tetapi menggabungkan identifikasi gambar, pencarian data nutrisi, dan pemberian rekomendasi dalam satu alur aplikasi.

## 3. Target Pengguna Utama

Target pengguna utama HealthCoach adalah orang yang membutuhkan informasi mengenai makanan dan kandungan nutrisinya secara praktis tanpa harus melakukan pencarian secara manual.Aplikasi ini ditujukan untuk pengguna yang ingin mengetahui informasi makanan hanya dengan memberikan foto makanan sebagai input. Pengguna dapat memperoleh hasil identifikasi makanan, informasi kandungan nutrisi seperti kalori, protein, lemak, dan karbohidrat, serta rekomendasi berdasarkan data nutrisi tersebut.

Contoh pengguna yang dapat memanfaatkan HealthCoach adalah mahasiswa, masyarakat umum, atau orang yang ingin mengetahui kandungan nutrisi dari makanan yang sedang mereka konsumsi. HealthCoach dirancang agar pengguna tidak perlu mencari informasi makanan dari berbagai sumber secara terpisah. Pengguna cukup memberikan foto makanan, kemudian sistem memproses foto tersebut dan menampilkan informasi yang tersedia melalui aplikasi.

# BAGIAN 2. RESUME MODUL DIGITAL AWARENESS

## Modul 1 — There's a Whole New World Out There!
Modul ini membahas perkembangan teknologi yang mengubah berbagai aktivitas dari cara analog menjadi digital. Teknologi membantu manusia dalam melakukan pekerjaan, belajar, berkomunikasi, mencari informasi, dan menjalankan aktivitas sehari-hari dengan lebih mudah.

## Modul 2 — You'll Need Some Basic Tools
Modul ini membahas dasar penggunaan perangkat digital, sistem operasi, serta pengelolaan file dan folder. Selain itu, dijelaskan pentingnya menggunakan password yang kuat untuk menjaga keamanan akun dan data pengguna.

## Modul 3 — This Is How You Get Around and Find What You're Looking For
Modul ini membahas penggunaan browser dan teknik pencarian informasi melalui internet maupun file. Selain itu, pengguna perlu memahami copyright dan public domain agar tidak sembarangan menggunakan karya atau informasi dari internet.

## Modul 4 — It Just Keeps Getting Better
Modul ini membahas perkembangan teknologi, khususnya AI, serta bagaimana teknologi tersebut dapat membantu aktivitas manusia. Modul ini juga menjelaskan pentingnya netiquette dan tanggung jawab dalam berkomunikasi serta menggunakan teknologi digital.

## Modul 5 — Even Though It's Digital, It Is Real, With Real Consequences
Modul ini membahas pentingnya menjaga data pribadi atau PII dan memahami digital footprint. Pengguna juga perlu berhati-hati terhadap komunikasi negatif, fraud atau penipuan, serta piracy atau pembajakan yang dapat menimbulkan dampak nyata.

## Modul 6 — Learn About Anything and Everything
Modul ini membahas dasar troubleshooting ketika mengalami masalah teknis dalam menggunakan teknologi. Selain itu, pengguna perlu terus meningkatkan keterampilan digital karena perkembangan teknologi dapat menimbulkan kesenjangan kemampuan.


# BAGIAN 3. HUBUNGAN DAN IMPLEMENTASI PADA TOPIK PROYEK

## 1. Bagaimana rancangan aplikasi dapat mempermudah tugas sehari-hari pengguna? Apa proses “analog/tradisional” dari topik proyekmu yang berhasil disederhanakan menjadi digital.
HealthCoach menyederhanakan proses yang sebelumnya dilakukan secara manual. Sebelum menggunakan aplikasi, pengguna yang ingin mengetahui informasi suatu makanan dapat melakukan beberapa langkah: Melihat makanan → mencari nama makanan → membuka sumber informasi → mencari kandungan nutrisi → membaca dan membandingkan informasi → menentukan kesimpulan.

Pada HealthCoach, proses tersebut dirancang menjadi: Foto makanan → identifikasi AI → pencarian data nutrisi → rekomendasi → hasil ditampilkan. Pengguna cukup memberikan foto makanan. Gemini Vision digunakan untuk membantu menentukan nama makanan, kemudian backend mencari informasi kalori, protein, lemak, dan karbohidrat dari dataset nutrisi. 

Data tersebut selanjutnya digunakan sebagai dasar pembuatan rekomendasi. Laporan_HealthCoach_Rapi Dengan demikian, proses pencarian informasi yang sebelumnya membutuhkan beberapa langkah dapat dilakukan melalui satu alur aplikasi.
Namun, HealthCoach tidak menganggap AI sebagai sumber tunggal kebenaran. Nilai nutrisi tetap diambil dari dataset karena hasil AI dapat salah dan foto tidak dapat menentukan berat atau ukuran porsi secara pasti. Hal ini juga merupakan salah satu keterbatasan yang sudah dicantumkan dalam rancangan proyek.

## 2. Jika aplikasimu memiliki fitur penyimpanan file atau pendaftaran akun, bagaimana kamu merancang struktur penyimpanan file yang intuitif bagi pengguna awam? Bagaimana kamu membantu pengguna membuat kata sandi yang aman?
Dalam rancangan HealthCoach saat ini, proses utama aplikasi berfokus pada foto makanan sebagai input dan pengolahan hasil analisis. Fitur pendaftaran akun pengguna belum menjadi bagian yang ditetapkan dalam rancangan utama. Apabila pada pengembangan berikutnya ditambahkan sistem akun, data pengguna perlu dipisahkan dan dikelola secara terstruktur di dalam database. Informasi setiap pengguna tidak boleh tercampur dengan data pengguna lainnya.

Keamanan password juga perlu diperhatikan. Pengguna dapat diberikan aturan untuk membuat password yang tidak mudah ditebak, misalnya menggunakan password yang cukup panjang dan tidak menggunakan informasi pribadi sebagai password. Selain itu, credential yang digunakan oleh sistem, seperti API key Gemini dan akses database, sebaiknya tidak diletakkan pada kode frontend atau repository publik. Credential tersebut harus dikelola pada sisi backend agar tidak mudah terlihat oleh pengguna.

## 3. Bagaimana kamu mendesain fitur pencarian (search bar) di dalam aplikasi agar pengguna dapat mencari informasi dengan mudah? Selain itu, sebutkan asset eksternal yang digunakan dalam aplikasi (library, API, gambar, icon). Apakah asset-aset tersebut berlisensi open-source, public domain, atau memiliki hak cipta khusus yang wajib dicantumkan?

HealthCoach saat ini belum mempunyai search bar yang menjadi fitur utama bagi pengguna. Proses pencarian makanan dilakukan oleh sistem setelah Gemini Vision memberikan hasil identifikasi. Sebagai contoh, apabila hasil identifikasi menunjukkan suatu nama makanan, backend dapat menggunakan nama tersebut sebagai kata pencarian untuk menemukan data yang sesuai pada dataset nutrisi.

Jika fitur pencarian langsung untuk pengguna dikembangkan pada tahap berikutnya, pencarian dapat dibuat berdasarkan nama makanan. Sistem juga dapat memberikan informasi ketika makanan yang dicari tidak terdapat dalam dataset. Dalam pengembangan HealthCoach terdapat beberapa komponen dari pihak
eksternal, yaitu:

- **Django**: sebagai framework backend.
- **Django REST Framework**: untuk pengembangan REST API.
- **Gemini Vision**: untuk membantu proses identifikasi makanan dari gambar.
- **Gemini**: untuk membantu menghasilkan rekomendasi berdasarkan data
  makanan dan nutrisi.
- **Indonesian Food and Drink Nutrition Dataset**: sebagai sumber data
  nutrisi makanan.

Untuk dataset yang digunakan, sumber yang digunakan dalam proyek berasal dari Kaggle. Status lisensi perlu mengacu pada informasi lisensi yang ditetapkan pada sumber dataset tersebut dan tidak boleh diasumsikan hanya berdasarkan lisensi asset lain.Penggunaan komponen eksternal juga perlu memperhatikan ketentuan penggunaan, hak cip ta, dan lisensi masing-masing sumber.

## 4. Jika aplikasimu memiliki fitur interaksi social, bagaimana kamu mencegah pelanggaran etika digital di dalamnya? Jika aplikasi menggunakan fitur pintar berbasis AI, bagaimana kamu memastikan AI tersebut bekerja secara etis dan bertanggung jawab bagi pengguna?

AI menjadi salah satu bagian penting dalam alur HealthCoach, tetapi hasil yang diberikan oleh AI tidak dijadikan satu-satunya sumber informasi. Gemini Vision digunakan untuk membantu menentukan makanan dari gambar. Setelah itu, sistem tidak langsung meminta AI membuat angka nutrisi sendiri. Backend terlebih dahulu menggunakan hasil identifikasi tersebut untuk mencari informasi nutrisi pada dataset. Informasi yang diperoleh dari dataset kemudian dapat digunakan sebagai konteks untuk proses rekomendasi oleh Gemini. Pendekatan tersebut digunakan untuk mengurangi kemungkinan munculnya informasi nutrisi yang tidak mempunyai sumber dari database yang digunakan.

HealthCoach juga perlu memberikan informasi kepada pengguna mengenai keterbatasan proses identifikasi. Hasil dapat dipengaruhi oleh kualitas foto, pencahayaan, sudut pengambilan gambar, kemiripan tampilan makanan, serta keterbatasan dataset. Apabila makanan tidak ditemukan pada dataset, sistem sebaiknya tidak mengarang nilai nutrisi. Pengguna perlu diberi tahu bahwa informasi untuk makanan tersebut belum tersedia.

## 5. Data pribadi sensitive (PII) apa saja yang dikumpulkan oleh aplikasimu? Bagaimana cara kamu melindungi data tersebut agar tidak bocor atau disalahgunakan? Bagaimana aplikasi meminimalkan Risiko pengguna menjadi korban penipuan siber di platform mu?

Data yang diberikan kepada HealthCoach perlu dibatasi sesuai kebutuhan aplikasi. Input utama yang digunakan dalam alur saat ini adalah foto makanan yang dikirim pengguna untuk dianalisis. Jika pada pengembangan berikutnya sistem menggunakan akun pengguna, data
seperti nama, email, dan informasi autentikasi harus mendapatkan perlindungan yang sesuai. Prinsip yang dapat diterapkan adalah mengumpulkan data yang memang diperlukan, membatasi akses terhadap data, serta tidak menyimpan atau membagikan informasi yang tidak diperlukan untuk fungsi aplikasi.

Selain perlindungan data, pengguna juga perlu diberikan pemahaman mengenai keamanan akun. HealthCoach tidak seharusnya meminta pengguna mengirimkan password melalui pesan atau memberikan credential kepada pihak lain. Jika suatu saat terdapat komunikasi yang mengatasnamakan HealthCoach, pengguna perlu berhati-hati terhadap permintaan data rahasia maupun link yang mencurigakan. Hal ini dapat membantu mengurangi risiko phishing atau penipuan yang memanfaatkan identitas aplikasi.

## 6. Ketika aplikasi mengalami masalah teknis (misalnya kehilangan koneksi internet atau kegagalan memuat data), bagaimana aplikasi mengomunikasikannya kepada pengguna? Tuliskan contoh rancangan pesan error ramah pengguna yang memandu pengguna melakukan troubleshooting mandiri secara mudah

HealthCoach bergantung pada beberapa komponen, sehingga masalah dapat terjadi pada koneksi pengguna, proses backend, database, maupun layanan AI. Pesan kesalahan sebaiknya tidak hanya menunjukkan bahwa sistem gagal, tetapi juga memberikan informasi mengenai tindakan yang dapat dilakukan
pengguna.

Beberapa contoh pesan yang dapat digunakan adalah:

### Koneksi Bermasalah
**Koneksi ke layanan belum tersedia. Periksa koneksi internet Anda dan**
**jalankan analisis kembali.**

### Gambar Tidak Berhasil Diproses
**Gambar belum dapat diproses. Gunakan foto dengan objek makanan yang**
**terlihat lebih jelas, kemudian coba kembali.**

### Data Nutrisi Tidak Ditemukan
**Makanan berhasil dikenali, tetapi informasi nutrisinya belum tersedia**
**pada dataset HealthCoach.**

### Layanan AI Tidak Merespons
**Analisis belum dapat dilakukan karena layanan AI tidak merespons.**
**Silakan coba kembali beberapa saat lagi.**
Dengan memberikan pesan seperti tersebut, pengguna dapat mengetahui kondisi yang sedang terjadi tanpa harus memahami pesan error teknis dari backend. Pengguna juga memperoleh langkah awal yang dapat dilakukan sendiri sebelum meminta bantuan pengelola aplikasi.
