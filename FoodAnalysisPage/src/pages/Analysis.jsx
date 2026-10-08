import { useRef, useState } from 'react'
import {
  Camera,
  Plus,
  X,
  ScanLine,
  Leaf,
  ImagePlus,
  CircleCheck,
  Scale,
  Flame,
  Beef,
  Wheat,
  Droplets,
} from 'lucide-react'

import './Analysis.css'

function Analysis() {
  const fileInputRef = useRef(null)

  const [photos, setPhotos] = useState([])
  const [status, setStatus] = useState('upload')
  const [errorMessage, setErrorMessage] = useState('')

  const MAX_PHOTOS = 3
  const MAX_SIZE = 10 * 1024 * 1024

  const handleChooseFile = () => {
    fileInputRef.current?.click()
  }

  const handleFileChange = (event) => {
    const selectedFiles = Array.from(event.target.files || [])

    if (!selectedFiles.length) return

    const remainingSlots = MAX_PHOTOS - photos.length

    if (remainingSlots <= 0) {
      setErrorMessage('Maksimal 3 foto dapat diunggah.')
      return
    }

    const validPhotos = []
    let validationError = ''

    for (const file of selectedFiles.slice(0, remainingSlots)) {
      const allowedTypes = [
        'image/jpeg',
        'image/png',
        'image/webp',
      ]

      if (!allowedTypes.includes(file.type)) {
        validationError = 'Format foto harus JPG, PNG, atau WEBP.'
        continue
      }

      if (file.size > MAX_SIZE) {
        validationError = 'Ukuran setiap foto maksimal 10 MB.'
        continue
      }

      validPhotos.push({
        id: `${Date.now()}-${Math.random()}`,
        file,
        previewUrl: URL.createObjectURL(file),
      })
    }

    if (validPhotos.length) {
      setPhotos((current) => [...current, ...validPhotos])
      setErrorMessage('')
      setStatus('upload')
    } else if (validationError) {
      setErrorMessage(validationError)
    }

    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const removePhoto = (photoId) => {
    setPhotos((currentPhotos) => {
      const photo = currentPhotos.find((item) => item.id === photoId)

      if (photo) {
        URL.revokeObjectURL(photo.previewUrl)
      }

      return currentPhotos.filter((item) => item.id !== photoId)
    })

    setErrorMessage('')
  }

  const handleAnalyze = () => {
    if (!photos.length) {
      setErrorMessage('Tambahkan minimal satu foto makanan terlebih dahulu.')
      return
    }

    setErrorMessage('')
    setStatus('loading')

    setTimeout(() => {
      setStatus('result')
    }, 2200)
  }

  const resetAnalysis = () => {
    photos.forEach((photo) => {
      URL.revokeObjectURL(photo.previewUrl)
    })

    setPhotos([])
    setStatus('upload')
    setErrorMessage('')

    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  return (
    <main className="an-page">
      <section className="an-intro">
        <span className="an-eyebrow">ANALISIS MAKANAN</span>

        <h1>
          Lihat nutrisi dari
          <br />
          makananmu.
        </h1>

        <p>
          Tambahkan foto makanan dari beberapa sudut agar sistem
          memperoleh konteks visual yang lebih baik.
        </p>

        <div className="an-guide">
          <div>
            <Camera size={19} />
            <span>
              <strong>Foto utama</strong>
              Ambil seluruh porsi makanan.
            </span>
          </div>

          <div>
            <ScanLine size={19} />
            <span>
              <strong>Sudut tambahan</strong>
              Foto samping atau sudut 45° dapat membantu analisis.
            </span>
          </div>

          <div>
            <Leaf size={19} />
            <span>
              <strong>Pencahayaan cukup</strong>
              Pastikan makanan terlihat jelas dan tidak terlalu gelap.
            </span>
          </div>
        </div>

        <div className="an-info-note">
          Hasil identifikasi dan estimasi porsi tetap merupakan
          perkiraan berdasarkan foto.
        </div>
      </section>

      <section className="an-panel">
        {status === 'loading' ? (
          <div className="an-loading">
            <div className="an-loader">
              <ScanLine size={28} />
            </div>

            <span className="an-small-label">HEALTHCOACH</span>

            <h2>Sedang menganalisis makananmu...</h2>

            <p>
              Sistem sedang memproses foto, mengenali makanan,
              dan menyiapkan informasi nutrisi.
            </p>

            <div className="an-loading-photos">
              {photos.map((photo) => (
                <img
                  key={photo.id}
                  src={photo.previewUrl}
                  alt="Foto makanan"
                />
              ))}
            </div>
          </div>
        ) : status === 'result' ? (
          <div className="an-result">
            <div className="an-result-images">
              <div className="an-main-result-image">
                <img
                  src={photos[0]?.previewUrl}
                  alt="Makanan yang dianalisis"
                />
              </div>

              {photos.length > 1 && (
                <div className="an-result-thumbnails">
                  {photos.slice(1).map((photo) => (
                    <img
                      key={photo.id}
                      src={photo.previewUrl}
                      alt="Sudut tambahan makanan"
                    />
                  ))}
                </div>
              )}
            </div>

            <div className="an-result-heading">
              <div>
                <span className="an-success-badge">
                  <CircleCheck size={15} />
                  Makanan berhasil dikenali
                </span>

                <span className="an-demo-badge">
                  Data sementara
                </span>
              </div>

              <h2>Nasi Goreng</h2>

              <p>
                Contoh hasil tampilan sebelum terhubung dengan
                Gemini Vision dan database nutrisi.
              </p>
            </div>

            <div className="an-portion-card">
              <div className="an-portion-icon">
                <Scale size={20} />
              </div>

              <div>
                <span>Estimasi porsi</span>
                <strong>± 280 gram</strong>
                <small>
                  Estimasi berdasarkan informasi visual dari foto.
                </small>
              </div>
            </div>

            <div className="an-nutrition-grid">
              <div>
                <Flame size={19} />
                <span>Kalori</span>
                <strong>350</strong>
                <small>kcal</small>
              </div>

              <div>
                <Beef size={19} />
                <span>Protein</span>
                <strong>12</strong>
                <small>g</small>
              </div>

              <div>
                <Wheat size={19} />
                <span>Karbohidrat</span>
                <strong>48</strong>
                <small>g</small>
              </div>

              <div>
                <Droplets size={19} />
                <span>Lemak</span>
                <strong>12</strong>
                <small>g</small>
              </div>
            </div>

            <div className="an-recommendation">
              <div>
                <Leaf size={20} />
              </div>

              <div>
                <strong>Rekomendasi HealthCoach</strong>

                <p>
                  Tambahkan sayuran untuk membantu meningkatkan
                  asupan serat dan menjaga keseimbangan makanan.
                </p>
              </div>
            </div>

            <button
              className="an-primary-button an-full-button"
              onClick={resetAnalysis}
            >
              Analisis Makanan Lain
            </button>
          </div>
        ) : (
          <div className="an-upload">
            <div className="an-upload-heading">
              <div className="an-upload-heading-icon">
                <ImagePlus size={24} />
              </div>

              <div>
                <h2>Tambahkan Foto Makanan</h2>

                <p>
                  Upload 1–3 foto dari sudut yang berbeda.
                </p>
              </div>
            </div>

            {photos.length === 0 ? (
              <button
                className="an-empty-upload"
                onClick={handleChooseFile}
              >
                <div>
                  <Plus size={26} />
                </div>

                <strong>Pilih Foto Makanan</strong>

                <span>
                  JPG, PNG, atau WEBP • Maksimal 10 MB per foto
                </span>
              </button>
            ) : (
              <>
                <div className="an-photo-grid">
                  {photos.map((photo, index) => (
                    <div className="an-photo-item" key={photo.id}>
                      <img
                        src={photo.previewUrl}
                        alt={`Foto makanan ${index + 1}`}
                      />

                      <span className="an-photo-label">
                        {index === 0
                          ? 'Foto utama'
                          : `Sudut ${index + 1}`}
                      </span>

                      <button
                        className="an-remove-photo"
                        onClick={() => removePhoto(photo.id)}
                        aria-label="Hapus foto"
                      >
                        <X size={16} />
                      </button>
                    </div>
                  ))}

                  {photos.length < MAX_PHOTOS && (
                    <button
                      className="an-add-photo"
                      onClick={handleChooseFile}
                    >
                      <Plus size={24} />
                      <span>Tambah foto</span>
                    </button>
                  )}
                </div>

                <div className="an-photo-count">
                  <span>
                    {photos.length} dari {MAX_PHOTOS} foto
                  </span>

                  {photos.length === 1 && (
                    <small>
                      Kamu dapat menambahkan sudut lain untuk memberi
                      konteks tambahan.
                    </small>
                  )}

                  {photos.length > 1 && (
                    <small>
                      Foto tambahan siap digunakan untuk analisis.
                    </small>
                  )}
                </div>

                <button
                  className="an-primary-button an-full-button"
                  onClick={handleAnalyze}
                >
                  <ScanLine size={18} />
                  Analisis Makanan
                </button>
              </>
            )}

            {errorMessage && (
              <div className="an-error">
                {errorMessage}
              </div>
            )}

            <input
              ref={fileInputRef}
              type="file"
              accept=".jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp"
              multiple
              hidden
              onChange={handleFileChange}
            />
          </div>
        )}
      </section>
    </main>
  )
}

export default Analysis
