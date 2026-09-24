# NAMA : Yulia Roslina
# NPM  : 24782065

# INTERCONNECTING BETWEEN DIGITAL AWARENESS AND APPLICATION DESIGN

## Bagian 1. Identitas dan Topik Proyek Aplikasi

### Nama Aplikasi
HealthCoach

### Deskripsi Singkat dan Tujuan Utama Aplikasi
HealthCoach adalah aplikasi AI Nutrition Coach yang membantu pengguna memperoleh informasi dan rekomendasi nutrisi berdasarkan foto makanan. Pengguna yang ingin mengetahui kandungan nutrisi suatu makanan biasanya perlu mengenali nama makanan, mencari informasi nutrisi dari sumber tertentu, kemudian memahami informasi tersebut secara terpisah. HealthCoach menyederhanakan proses tersebut dengan menggunakan Gemini Vision untuk mengidentifikasi makanan, mencocokkan hasil identifikasi dengan database nutrisi, kemudian menggunakan data tersebut sebagai dasar untuk menghasilkan rekomendasi melalui Gemini.

Tujuan utama HealthCoach adalah membuat proses memperoleh dan memahami informasi nutrisi makanan menjadi lebih praktis melalui satu alur aplikasi berbasis foto.

### Target Pengguna Utama
HealthCoach ditujukan bagi individu yang sedang menjalani diet atau berusaha menerapkan pola hidup sehat, terutama mereka yang membutuhkan informasi dan rekomendasi nutrisi makanan secara praktis.

# Bagian 2. Resume Modul Digital Awareness

## 1. Modul 1: There's a Whole New World Out There!

Modul ini membahas bagaimana teknologi digital membuat berbagai aktivitas menjadi lebih mudah dan cepat, tetapi tetap memiliki risiko seperti masalah privasi, keamanan data, dan penggunaan yang berlebihan. Dalam HealthCoach, konsep tersebut kami terapkan dengan memanfaatkan AI untuk menyederhanakan proses mencari informasi makanan yang sebelumnya harus dilakukan secara manual. Pengguna cukup mengunggah foto makanan, lalu Gemini Vision mengenali makanan, sistem mengambil informasi nutrisinya dari database, dan Gemini menggunakan data tersebut untuk memberikan rekomendasi nutrisi. Dengan begitu, teknologi yang digunakan dalam HealthCoach benar-benar diarahkan untuk membantu pengguna mendapatkan dan memahami informasi nutrisi dengan cara yang lebih praktis.

## 2. Modul 2: You'll Need Some Basic Tools

Dalam HealthCoach, konsep modul ini diterapkan pada pengelolaan file, struktur aplikasi, dan keamanan akun pengguna. Foto makanan yang diunggah pengguna perlu dikelola dengan baik agar dapat diproses oleh sistem, sementara struktur folder dan file pada project dibuat terorganisir agar pengembangan aplikasi lebih mudah dilakukan. Untuk keamanan akun, password pengguna tidak disimpan dalam bentuk asli, tetapi diproses menggunakan hashing sehingga sistem tidak menyimpan password asli pengguna secara langsung.

## 3. Modul 3: This is How You Get Around and Find What You're Looking For

Dalam HealthCoach, konsep modul ini diterapkan pada cara sistem menemukan informasi makanan yang sesuai dari data yang tersedia. Setelah Gemini Vision mengenali makanan dari foto, hasil tersebut digunakan untuk mencari makanan yang cocok di database nutrisi. Data yang ditemukan kemudian digunakan untuk menampilkan informasi seperti kalori, protein, lemak, dan karbohidrat, lalu menjadi dasar bagi Gemini untuk memberikan rekomendasi nutrisi. Dengan begitu, pengguna tidak perlu mencari informasi makanan secara manual karena proses pencarian dan pengolahan datanya dilakukan oleh sistem.

## 4. Modul 4: It Just Keeps Getting Better

Dalam HealthCoach, konsep modul ini diterapkan terutama pada penggunaan AI secara bertanggung jawab. HealthCoach menggunakan Gemini untuk mengenali makanan dari foto dan memberikan rekomendasi nutrisi, tetapi hasil AI tidak selalu dianggap benar karena masih memiliki kemungkinan kesalahan. Karena itu, informasi dari AI perlu disampaikan secara jelas kepada pengguna dan tetap menggunakan database nutrisi sebagai sumber data, sehingga Gemini tidak bebas memberikan angka nutrisi berdasarkan perkiraannya sendiri. Selain itu, penggunaan AI dalam HealthCoach harus tetap memperhatikan tanggung jawab terhadap pengguna dan tidak memberikan kesan bahwa hasil rekomendasi merupakan diagnosis atau keputusan medis.

## 5. Modul 5: Even Though It's Digital, It Is Real, With Real Consequences

Dalam HealthCoach, konsep modul ini diterapkan pada perlindungan data dan privasi pengguna. Data seperti informasi akun dan foto makanan yang diunggah pengguna harus dikelola dengan aman dan hanya digunakan untuk kebutuhan aplikasi. Selain itu, HealthCoach perlu membatasi informasi yang dikumpulkan agar tidak menyimpan data pribadi yang sebenarnya tidak diperlukan, serta menjaga agar data pengguna tidak mudah diakses atau disalahgunakan oleh pihak lain. Hal ini penting karena meskipun data disimpan dan diproses secara digital, dampaknya tetap nyata bagi pengguna jika terjadi kebocoran atau penyalahgunaan data.

## 6. Modul 6: Learn About Anything and Everything

Dalam HealthCoach, konsep modul ini diterapkan pada troubleshooting ketika terjadi masalah pada aplikasi. Misalnya, ketika koneksi internet terputus, Gemini gagal merespons, atau data makanan tidak ditemukan di database, sistem perlu memberikan pesan error yang jelas agar pengguna mengetahui apa yang terjadi dan apa yang bisa dilakukan. Dari sisi pengembangan, kemampuan troubleshooting juga membantu kami mencari penyebab masalah dan memperbaikinya, sementara pemahaman terhadap skills gap membantu mengenali bagian teknis yang masih perlu dipelajari selama proses pengembangan HealthCoach.


# Bagian 3. Hubungan dan Implementasi pada Topik Proyek

## 1. Bagaimana rancangan aplikasi dapat mempermudah tugas sehari-hari pengguna?

HealthCoach dirancang untuk menyederhanakan proses yang biasanya mengharuskan pengguna mencari nama makanan, mencari informasi nutrisi, kemudian memahami informasi tersebut secara terpisah.

Proses tersebut diubah menjadi satu alur:

Foto makanan → Identifikasi makanan → Pencarian data nutrisi → Rekomendasi nutrisi

Pengguna cukup memberikan foto makanan sebagai input. Gemini Vision kemudian mengidentifikasi makanan tersebut, lalu hasilnya digunakan oleh backend untuk mencari data nutrisi pada database PostgreSQL. Data nutrisi yang diperoleh selanjutnya digunakan oleh Gemini untuk memberikan rekomendasi yang lebih mudah dipahami.

Dengan cara ini, HealthCoach membantu mengurangi langkah yang harus dilakukan pengguna saat mencari informasi makanan, tetapi tetap menggunakan database sebagai dasar informasi nutrisinya.

## 2. Bagaimana rancangan penyimpanan file dan keamanan kata sandi diterapkan?

HealthCoach dapat menyimpan foto makanan yang diunggah pengguna untuk proses analisis. Jika fitur riwayat analisis digunakan, foto tersebut dapat dikaitkan dengan data analisis milik pengguna sehingga hasil sebelumnya dapat dikelola dengan lebih teratur. Karena itu, file perlu disimpan dengan struktur yang jelas, misalnya berdasarkan identitas pengguna dan identitas analisis, agar foto dari satu pengguna tidak tercampur dengan pengguna lainnya dan lebih mudah dikelola oleh sistem.

Untuk keamanan akun, password tidak disimpan dalam bentuk teks biasa. Password yang dimasukkan pengguna akan diproses menggunakan mekanisme password hashing pada backend, sehingga yang disimpan di database bukan password asli pengguna. Dengan cara ini, apabila data database diakses tanpa izin, password asli pengguna tidak langsung dapat diketahui. Selain itu, pengguna juga perlu diarahkan untuk menggunakan password yang kuat dan tidak mudah ditebak.

## 3. Bagaimana fitur pencarian dan asset eksternal diterapkan?

Pada HealthCoach, pencarian informasi nutrisi tidak bergantung pada search bar sebagai fitur utama. Proses pencarian dilakukan secara otomatis setelah Gemini Vision mengenali makanan dari foto. Hasil identifikasi tersebut digunakan oleh backend untuk mencari data makanan yang sesuai pada database nutrisi. Dengan demikian, pengguna tidak perlu mengetik nama makanan dan mencari informasi nutrisinya secara manual.

Selain database internal, HealthCoach menggunakan beberapa layanan dan sumber eksternal, seperti Gemini API untuk pemrosesan AI, Django dan Django REST Framework untuk pengembangan backend, serta Indonesian Food and Drink Nutrition Dataset sebagai sumber data nutrisi. Library atau package yang digunakan untuk mendukung pengembangan aplikasi juga termasuk asset eksternal.

Setiap asset eksternal perlu diperiksa sumber dan ketentuan lisensinya sebelum digunakan. Untuk dataset, sumber dan lisensinya perlu dicantumkan dalam dokumentasi proyek. Begitu juga dengan library dan asset seperti gambar atau icon yang digunakan, penggunaannya harus mengikuti ketentuan lisensi yang berlaku.

Dengan cara tersebut, penggunaan asset eksternal pada HealthCoach tetap dapat ditelusuri dan digunakan sesuai dengan ketentuan yang berlaku.

## 4. Bagaimana memastikan penggunaan AI dalam HealthCoach tetap etis dan bertanggung jawab?

Penggunaan AI pada HealthCoach difokuskan pada fungsi yang memang dibutuhkan oleh aplikasi, yaitu mengenali makanan dari foto dan memberikan rekomendasi nutrisi. AI tidak digunakan untuk mendiagnosis kondisi kesehatan atau memberikan keputusan medis.

Alur penggunaan AI di HealthCoach dibuat sederhana:

Gemini Vision mengenali makanan dari foto yang diberikan pengguna.
Database PostgreSQL digunakan untuk mengambil informasi nutrisi berdasarkan makanan yang berhasil dikenali.
Gemini menggunakan informasi tersebut untuk memberikan rekomendasi yang lebih mudah dipahami pengguna.

Pembagian ini dilakukan agar AI tidak menjadi satu-satunya sumber untuk menentukan nilai nutrisi. Kalori, protein, lemak, dan karbohidrat berasal dari database, sedangkan AI digunakan untuk mengenali makanan dan membantu menyusun rekomendasi.

Hasil dari AI juga tetap memiliki kemungkinan salah, misalnya ketika foto kurang jelas, makanan tertutup sebagian, atau beberapa makanan memiliki bentuk yang mirip. Karena itu, hasil yang diberikan HealthCoach tetap perlu dipahami sebagai hasil identifikasi dan rekomendasi dari sistem yang memiliki keterbatasan, bukan sebagai hasil yang selalu benar atau diagnosis medis.

## 5. Data pribadi sensitif apa yang dikumpulkan dan bagaimana melindunginya?

Dalam HealthCoach, data yang digunakan untuk menjalankan aplikasi meliputi identitas akun, email, password, foto makanan, dan riwayat analisis makanan. Data tersebut hanya digunakan sesuai kebutuhan fitur aplikasi, sehingga HealthCoach tidak perlu mengumpulkan informasi pribadi yang tidak berhubungan dengan fungsi aplikasi.

Untuk menjaga keamanan akun, password tidak disimpan dalam bentuk aslinya, tetapi diproses menggunakan password hashing. Foto makanan dan riwayat analisis juga perlu dibatasi aksesnya agar hanya dapat dilihat oleh pengguna yang bersangkutan. HealthCoach juga tidak meminta data seperti PIN, OTP, password layanan lain, atau informasi perbankan karena data tersebut tidak diperlukan untuk menjalankan aplikasi.

Dengan begitu, HealthCoach hanya mengelola data yang memang dibutuhkan dan tetap menjaga agar data pengguna tidak mudah diakses atau disalahgunakan.

## 6. Bagaimana aplikasi menangani masalah teknis?

Kalau terjadi masalah saat menggunakan HealthCoach, aplikasi perlu memberikan pesan yang jelas dan mudah dipahami, bukan hanya menampilkan bahwa proses gagal. Pesan tersebut juga sebaiknya memberi tahu pengguna apa yang bisa dilakukan untuk mencoba kembali.

Contohnya:

Koneksi internet terputus: “Koneksi internet terputus. Periksa koneksi Wi-Fi atau data seluler, lalu coba lagi.”
Foto gagal diproses: “Foto belum dapat diproses. Pastikan makanan terlihat jelas, lalu coba unggah kembali.”
Makanan tidak teridentifikasi: “Makanan belum dapat dikenali. Coba gunakan foto yang lebih jelas.”
Data nutrisi tidak ditemukan: “Informasi nutrisi untuk makanan ini belum tersedia.”
Layanan Gemini tidak tersedia: “Layanan analisis sedang tidak tersedia. Coba lagi beberapa saat kemudian.”

Dengan cara ini, pengguna tetap bisa memahami apa yang sedang terjadi tanpa harus mengetahui masalah teknis di baliknya, seperti API, server, atau database. Bagi developer, pesan tersebut juga dapat membantu mengetahui bagian mana dari sistem yang sedang mengalami masalah.


# Kesimpulan

Penerapan Digital Awareness pada HealthCoach menunjukkan bahwa pengembangan aplikasi tidak hanya berfokus pada teknologi yang digunakan, tetapi juga pada bagaimana teknologi tersebut digunakan dengan tepat dan bertanggung jawab. Hal ini terlihat dari penyederhanaan pencarian informasi nutrisi, keamanan akun dan data pengguna, penggunaan aset digital yang sesuai, penggunaan AI dengan batasan yang jelas, serta penanganan masalah yang mudah dipahami pengguna. Dengan begitu, HealthCoach tidak hanya berfokus pada fitur yang dapat berjalan, tetapi juga pada keamanan, kemudahan penggunaan, dan manfaat yang diberikan kepada pengguna.
