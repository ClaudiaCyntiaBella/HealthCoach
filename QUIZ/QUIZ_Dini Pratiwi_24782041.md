# QUIZ - Interconnecting Between Digital Awareness And Application Design

**Mata Kuliah:** Internet Programming II  
**Program Studi:** Teknologi Rekayasa Internet  
**Nama Aplikasi:** HealthCoach  
**Nama:** Dini Pratiwi 
**NPM:** 24782041

## Bagian 1. Identitas dan Topik Proyek Aplikasi

**Nama Aplikasi:**  
HealthCoach

**Deskripsi Singkat dan Tujuan Utama:**  
HealthCoach adalah aplikasi berbasis AI yang membantu pengguna mengetahui informasi nutrisi makanan melalui foto. Pengguna cukup mengambil atau mengunggah foto makanan, kemudian sistem akan mengenali jenis makanan menggunakan Gemini Vision, mengambil data kalori, protein, lemak, dan karbohidrat dari database nutrisi, lalu memberikan rekomendasi berdasarkan hasil tersebut. Tujuan utama aplikasi ini adalah mempermudah pengguna dalam mengetahui kandungan nutrisi makanan tanpa harus mencari informasi secara manual satu per satu.

**Target Pengguna:**  
Target pengguna HealthCoach adalah masyarakat umum yang ingin mendapatkan informasi nutrisi makanan dengan cara yang lebih praktis melalui foto, terutama pengguna yang ingin lebih memperhatikan pola makan sehari-hari.

## Bagian 2. Resume Modul Digital Awareness

### Modul 1 - There's a Whole New World Out There!
Modul ini membahas bagaimana teknologi digital membuat banyak aktivitas menjadi lebih cepat dan praktis. Kegiatan yang dulu dilakukan secara manual sekarang bisa dilakukan melalui aplikasi dan internet, seperti komunikasi, transaksi, dan belajar. Teknologi memang membantu, tetapi tetap ada risiko seperti privasi, keamanan data, dan kesenjangan akses digital.

### Modul 2 - You'll Need Some Basic Tools
Modul ini membahas dasar penggunaan perangkat digital, sistem operasi, serta cara mengatur file dan folder agar mudah ditemukan. Selain itu, keamanan akun juga penting, terutama dengan menggunakan password yang kuat dan tidak mudah ditebak.

### Modul 3 - This Is How You Get Around and Find What You're Looking For
Modul ini membahas cara mencari informasi melalui browser maupun di dalam file. Pengguna juga perlu bisa menilai apakah informasi yang ditemukan relevan dan aman. Selain itu, dijelaskan juga tentang copyright, Creative Commons, public domain, dan penggunaan karya orang lain secara benar.

### Modul 4 - It Just Keeps Getting Better
Modul ini membahas perkembangan AI dan penggunaannya dalam kehidupan sehari-hari. AI bisa membantu banyak pekerjaan, tetapi hasilnya tetap dipengaruhi oleh data dan cara sistem dibuat. Modul ini juga membahas netiquette, yaitu etika saat menggunakan internet dan berkomunikasi dengan orang lain secara online.

### Modul 5 - Even Though It's Digital, It Is Real, With Real Consequences
Modul ini membahas bahwa aktivitas di internet tetap memiliki dampak nyata. Data pribadi seperti nama, email, alamat, dan nomor telepon perlu dijaga agar tidak disalahgunakan. Pengguna juga harus berhati-hati terhadap phishing, penipuan, cyberbullying, dan jejak digital yang bisa bertahan lama.

### Modul 6 - Learn About Anything and Everything
Modul ini membahas cara melakukan troubleshooting saat mengalami masalah teknis. Langkah awal bisa dilakukan dengan mengecek hal sederhana seperti daya perangkat, penyimpanan, aplikasi yang berjalan, atau melakukan restart. Selain itu, pengguna juga perlu terus meningkatkan keterampilan digital agar lebih mandiri dalam menggunakan teknologi.

## Bagian 3. Hubungan dan Implementasi pada Topik Proyek

### 1. Penerapan teknologi untuk mempermudah aktivitas pengguna
HealthCoach membantu pengguna mengetahui informasi nutrisi makanan dengan cara yang lebih praktis. Sebelumnya pengguna harus mencari nama makanan dan kandungan nutrisinya secara manual. Dengan HealthCoach, pengguna cukup mengambil atau mengunggah foto makanan, lalu Gemini Vision mengenali makanan tersebut dan sistem mengambil data nutrisi dari database untuk ditampilkan kepada pengguna.

### 2. Penyimpanan data dan keamanan password
HealthCoach tidak memiliki fitur penyimpanan file yang harus diatur sendiri oleh pengguna seperti folder pada komputer. Foto makanan yang diunggah akan diproses oleh sistem, sehingga pengguna tidak perlu mengatur lokasi penyimpanannya secara manual.
Jika nantinya HealthCoach menggunakan fitur pendaftaran akun, data setiap pengguna akan disimpan secara terpisah agar lebih teratur. Untuk keamanan akun, pengguna dapat diarahkan membuat password yang cukup panjang, tidak mudah ditebak, dan menggunakan kombinasi huruf, angka, atau simbol.

### 3. Fitur pencarian dan penggunaan aset eksternal
Jika fitur pencarian ditambahkan, pengguna dapat mencari makanan berdasarkan nama sehingga informasi nutrisi lebih mudah ditemukan. Selain pencarian manual, HealthCoach juga menggunakan Gemini Vision untuk membantu mengenali makanan dari foto.
Aset eksternal yang digunakan antara lain *Indonesian Food and Drink Nutrition Dataset* dari Kaggle sebagai sumber data nutrisi dan Gemini sebagai layanan AI. Penggunaan dataset dan aset lain tetap perlu memperhatikan lisensi serta mencantumkan sumber yang digunakan.

### 4. Penggunaan AI secara etis dan bertanggung jawab
HealthCoach tidak memiliki fitur interaksi sosial antar pengguna, sehingga tidak terdapat fitur komentar atau komunikasi antar pengguna di dalam aplikasi. HealthCoach menggunakan AI untuk mengenali makanan dan memberikan rekomendasi nutrisi. Agar penggunaannya tetap bertanggung jawab, hasil dari AI tidak boleh dianggap selalu benar. Informasi nutrisi tetap diambil dari database, sedangkan Gemini digunakan untuk membantu proses identifikasi dan memberikan rekomendasi. Selain itu, aplikasi perlu memberi tahu pengguna bahwa hasil dari foto memiliki keterbatasan karena kualitas gambar, pencahayaan, dan ukuran porsi dapat memengaruhi hasil analisis.

### 5. Perlindungan data pribadi dan pencegahan penipuan
Jika HealthCoach menggunakan fitur akun, data seperti nama, email, dan informasi akun termasuk data pribadi yang perlu dilindungi. Aplikasi sebaiknya hanya meminta data yang memang diperlukan dan tidak membagikannya kepada pihak lain tanpa izin pengguna.
Untuk mengurangi risiko penipuan, pengguna perlu diingatkan agar tidak memberikan password kepada orang lain dan berhati-hati terhadap pesan atau link mencurigakan yang mengatasnamakan HealthCoach.

### 6. Penanganan masalah teknis
Jika terjadi masalah seperti koneksi internet terputus atau data gagal dimuat, HealthCoach akan menampilkan pesan yang menjelaskan masalah dengan bahasa yang mudah dipahami dan memberikan langkah sederhana yang dapat dicoba pengguna.
Contohnya:
> Data belum berhasil dimuat. Periksa koneksi internet Anda, lalu coba kembali.
Jika masalah terjadi pada proses foto:
> Foto belum dapat dikenali. Coba gunakan foto yang lebih jelas, lalu unggah kembali.
Pesan tersebut tidak hanya memberi tahu bahwa terjadi kesalahan, tetapi juga memberikan langkah yang dapat dilakukan pengguna untuk mencoba menyelesaikan masalah sendiri.
