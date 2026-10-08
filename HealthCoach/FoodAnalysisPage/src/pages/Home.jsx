import { Link } from 'react-router-dom'
import {
  ArrowRight,
  Camera,
  ScanLine,
  Leaf,
  CheckCircle2,
} from 'lucide-react'

import './Home.css'

function Home() {
  return (
    <main className="hc-home">

      <section className="hc-hero">
        <div className="hc-hero-copy">
          <span className="hc-eyebrow">
            HEALTHCOACH
          </span>

          <h1>
            Kenali Nutrisi
            <br />
            Makananmu dengan Lebih
            <br />
            Mudah
          </h1>

          <p>
            Cukup unggah foto makanan. HealthCoach membantu mengenali
            makanan, menampilkan informasi nutrisi, dan memberikan
            rekomendasi yang mudah dipahami.
          </p>

          <div className="hc-hero-actions">
            <Link to="/analysis" className="hc-primary-btn">
              Mulai Analisis
              <ArrowRight size={18} />
            </Link>

            <a href="#cara-kerja" className="hc-text-link">
              Lihat cara kerja
            </a>
          </div>

          <div className="hc-trust">
            <span>
              <CheckCircle2 size={16} />
              Mudah digunakan
            </span>

            <span>
              <CheckCircle2 size={16} />
              Informasi ringkas
            </span>

            <span>
              <CheckCircle2 size={16} />
              Praktis
            </span>
          </div>
        </div>

        <div className="hc-hero-visual">
          <video
            className="hc-hero-video"
            src="/videos/healthcoach-hero.mp4"
            autoPlay
            loop
            muted
            playsInline
          />
        </div>
      </section>

      <section className="hc-how" id="cara-kerja">
        <div className="hc-section-heading">
          <span>CARA KERJA</span>

          <h2>
            Sederhana dari foto sampai rekomendasi.
          </h2>

          <p>
            Tiga langkah untuk memperoleh informasi nutrisi makananmu.
          </p>
        </div>

        <div className="hc-steps">
          <article>
            <div className="hc-step-top">
              <div className="hc-step-icon">
                <Camera size={24} />
              </div>

              <span>01</span>
            </div>

            <h3>Tambahkan Foto</h3>

            <p>
              Unggah hingga 3 foto makanan dari sudut yang berbeda.
            </p>
          </article>

          <article>
            <div className="hc-step-top">
              <div className="hc-step-icon">
                <ScanLine size={24} />
              </div>

              <span>02</span>
            </div>

            <h3>Analisis Makanan</h3>

            <p>
              Sistem mengenali makanan dan mengambil informasi nutrisinya.
            </p>
          </article>

          <article>
            <div className="hc-step-top">
              <div className="hc-step-icon">
                <Leaf size={24} />
              </div>

              <span>03</span>
            </div>

            <h3>Lihat Rekomendasi</h3>

            <p>
              Informasi nutrisi dan rekomendasi ditampilkan dengan jelas.
            </p>
          </article>
        </div>
      </section>

      <section className="hc-benefits">
        <div className="hc-benefit-heading">
          <span>KENAPA HEALTHCOACH?</span>

          <h2>
            Nutrisi tidak harus terasa rumit.
          </h2>
        </div>

        <div className="hc-benefit-items">
          <div>
            <CheckCircle2 size={20} />

            <p>
              <strong>Praktis</strong>
              Tidak perlu memasukkan makanan satu per satu.
            </p>
          </div>

          <div>
            <CheckCircle2 size={20} />

            <p>
              <strong>Mudah dibaca</strong>
              Informasi utama ditampilkan secara ringkas.
            </p>
          </div>

          <div>
            <CheckCircle2 size={20} />

            <p>
              <strong>Mudah digunakan</strong>
              Dirancang untuk penggunaan sehari-hari.
            </p>
          </div>
        </div>
      </section>

      <section className="hc-bottom-cta">
        <div>
          <span>SIAP MENCOBA?</span>

          <h2>
            Mulai dari foto makananmu.
          </h2>

          <p className="hc-bottom-description">
            Unggah hingga 3 foto dari sudut berbeda untuk membantu
            proses analisis.
          </p>
        </div>

        <Link to="/analysis" className="hc-primary-btn">
          Analisis Makanan
          <ArrowRight size={18} />
        </Link>
      </section>

    </main>
  )
}

export default Home
