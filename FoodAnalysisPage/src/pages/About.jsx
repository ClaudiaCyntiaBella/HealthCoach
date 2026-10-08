function About() {
  return (
    <main className="about-page">
      <div className="about-card">
        <span className="eyebrow">TENTANG HEALTHCOACH</span>

        <h1>Teman sederhana untuk memahami makananmu.</h1>

        <p>
          HealthCoach adalah aplikasi AI Nutrition Coach yang membantu
          pengguna memperoleh informasi nutrisi melalui foto makanan.
        </p>

        <p>
          Sistem mengidentifikasi makanan, mencocokkan hasil dengan data
          nutrisi, kemudian memberikan rekomendasi yang mudah dipahami.
        </p>

        <div className="about-points">
          <div>📷 Analisis melalui foto</div>
          <div>🥗 Informasi nutrisi</div>
          <div>🌿 Rekomendasi yang mudah dipahami</div>
        </div>
      </div>
    </main>
  )
}

export default About
