import os
import json
import mimetypes
from pathlib import Path

from dotenv import load_dotenv
from google import genai


# ============================================================
# 1. LOAD ENVIRONMENT VARIABLE
# ============================================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY belum ditemukan.\n"
        "Pastikan API Key sudah dimasukkan ke file .env."
    )


# ============================================================
# 2. CONNECT TO GEMINI
# ============================================================

client = genai.Client(api_key=api_key)

print("=" * 60)
print("GEMINI BERHASIL TERHUBUNG")
print("=" * 60)


# ============================================================
# 3. MENENTUKAN FOLDER GAMBAR
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
IMAGE_DIR = BASE_DIR / "images"

if not IMAGE_DIR.exists():
    raise FileNotFoundError(
        f"Folder gambar tidak ditemukan:\n{IMAGE_DIR}"
    )


# ============================================================
# 4. MENCARI SEMUA FILE GAMBAR
# ============================================================

supported_extensions = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp"
}

image_files = sorted(
    [
        file
        for file in IMAGE_DIR.iterdir()
        if file.is_file()
        and file.suffix.lower() in supported_extensions
    ]
)


if not image_files:
    print("\nTidak ada gambar yang ditemukan di folder:")
    print(IMAGE_DIR)
    exit()


print(f"\nFolder gambar:")
print(IMAGE_DIR)

print(f"\nJumlah gambar ditemukan: {len(image_files)}")

for index, image_file in enumerate(image_files, start=1):
    print(f"{index}. {image_file.name}")


# ============================================================
# 5. MEMBACA SEMUA GAMBAR
# ============================================================

contents = []

prompt = """
Anda adalah sistem analisis makanan untuk aplikasi HealthCoach.

Saya memberikan beberapa gambar makanan sekaligus.

Untuk setiap gambar, lakukan analisis berikut:

1. Identifikasi nama makanan utama.
2. Identifikasi bahan atau komponen makanan yang terlihat pada gambar.
3. Identifikasi bahan yang kemungkinan digunakan berdasarkan tampilan makanan.
4. Bedakan antara bahan yang benar-benar terlihat dan bahan yang hanya diperkirakan.
5. Berikan tingkat keyakinan:
   - tinggi
   - sedang
   - rendah
6. Jangan mengklaim bahan yang tidak dapat diketahui dari gambar
   sebagai fakta.
7. Jangan memberikan informasi nutrisi.
8. Jangan memberikan diagnosis kesehatan.
9. Jangan memberikan rekomendasi diet.

Gunakan format JSON berikut:

{
    "foods": [
        {
            "image": "nama_file_gambar",
            "food_name": "nama makanan",
            "ingredients": [
                {
                    "name": "nama bahan",
                    "visible": true,
                    "confidence": "tinggi"
                }
            ]
        }
    ]
}

Keterangan:
- visible = true jika bahan/komponen terlihat jelas pada gambar.
- visible = false jika bahan hanya diperkirakan berdasarkan karakteristik makanan.
- confidence menunjukkan tingkat keyakinan Gemini terhadap identifikasi bahan.

Pastikan setiap gambar memiliki hasil sendiri.
"""

contents.append(prompt)


for image_file in image_files:

    print(f"\nMembaca gambar: {image_file.name}")

    mime_type, _ = mimetypes.guess_type(image_file)

    if mime_type is None:
        mime_type = "image/jpeg"

    with open(image_file, "rb") as f:
        image_bytes = f.read()

    # Tambahkan nama file agar Gemini mengetahui
    # gambar mana yang sedang dianalisis
    contents.append(
        f"\nNama file gambar: {image_file.name}"
    )

    contents.append(
        {
            "inline_data": {
                "mime_type": mime_type,
                "data": image_bytes
            }
        }
    )


# ============================================================
# 6. KIRIM SEMUA GAMBAR KE GEMINI
# ============================================================

print("\n" + "=" * 60)
print("MENGIRIM SEMUA GAMBAR KE GEMINI...")
print("=" * 60)


try:

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=contents
    )

except Exception as e:

    print("\nTerjadi error saat menghubungi Gemini:")
    print(e)

    exit()


# ============================================================
# 7. MENAMPILKAN RESPONSE MENTAH
# ============================================================

print("\n" + "=" * 60)
print("RESPONSE DARI GEMINI")
print("=" * 60)

print(response.text)


# ============================================================
# 8. MENCOBA MEMBACA RESPONSE SEBAGAI JSON
# ============================================================

print("\n" + "=" * 60)
print("HASIL IDENTIFIKASI")
print("=" * 60)


result_text = response.text.strip()

# Menghapus markdown ```json jika Gemini menggunakannya
if result_text.startswith("```json"):
    result_text = result_text[7:]

if result_text.startswith("```"):
    result_text = result_text[3:]

if result_text.endswith("```"):
    result_text = result_text[:-3]

result_text = result_text.strip()


try:

    result_json = json.loads(result_text)

    foods = result_json.get("foods", [])

    if not foods:
        print("Tidak ada hasil identifikasi.")
    else:

        for index, food in enumerate(foods, start=1):

            image_name = food.get(
                "image",
                "Tidak diketahui"
            )

            food_name = food.get(
                "food_name",
                "Tidak teridentifikasi"
            )

            print(f"\n{index}. Gambar")
            print(f"   File       : {image_name}")
            print(f"   Makanan    : {food_name}")

except json.JSONDecodeError:

    print(
        "\nResponse Gemini bukan JSON yang valid."
    )

    print(
        "Gunakan bagian 'RESPONSE DARI GEMINI' "
        "untuk melihat hasil mentah."
    )


# ============================================================
# 9. SELESAI
# ============================================================

print("\n" + "=" * 60)
print("TEST GEMINI SELESAI")
print("=" * 60)