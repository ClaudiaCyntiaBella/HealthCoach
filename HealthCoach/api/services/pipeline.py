from api.services.gemini import identify_food
from api.services.estimation import AI_ESTIMATION_DISCLAIMER, estimate_nutrition
from api.services.nutrition import get_nutrition_repository
from api.services.recommendation import generate_recommendation


NON_FOOD_MESSAGE = (
    "Maaf, foto yang Anda unggah bukan merupakan foto makanan atau minuman. "
    "Silakan unggah foto makanan atau minuman untuk melakukan analisis nutrisi."
)
UNCERTAIN_IMAGE_MESSAGE = (
    "Foto tidak dapat dikenali dengan jelas. Silakan ambil atau unggah foto "
    "makanan atau minuman yang lebih jelas."
)
TOO_BLURRY_MESSAGE = (
    "Foto terlalu buram dan makanan tidak dapat dikenali dengan jelas. "
    "Silakan unggah foto yang lebih jelas."
)
MODERATELY_BLURRY_WARNING = (
    "Foto agak buram. Hasil analisis mungkin kurang akurat; "
    "unggah foto yang lebih jelas untuk hasil yang lebih baik."
)


def _rejected_image_result(identification) -> dict:
    message = (
        TOO_BLURRY_MESSAGE
        if identification.image_quality == "TOO_BLURRY"
        else (
            NON_FOOD_MESSAGE
            if identification.image_category == "NON_FOOD"
            else UNCERTAIN_IMAGE_MESSAGE
        )
    )
    return {
        "identification": identification.to_dict(),
        "matching": {
            "normalized_name": None,
            "status": "NOT_MATCHED",
            "duplicate_count": 0,
            "method": "NONE",
            "reference_name": None,
        },
        "nutrition": None,
        "nutrition_source": "UNAVAILABLE",
        "estimation_note": None,
        "quality_warning": None,
        "recommendation": message,
        "recommendation_details": {
            "saran": message,
            "alasan": identification.notes or message,
            "pendamping_alternatif": "Tidak tersedia sebelum foto makanan atau minuman dapat dikenali.",
            "catatan_nutrisi": "Tidak ada informasi nutrisi untuk foto ini.",
        },
        "note": message,
    }


def analyze_food_images(images) -> dict:
    identification = identify_food(images)
    if not identification.is_analyzable:
        return _rejected_image_result(identification)

    match = get_nutrition_repository().find_for_identification(
        identification.food_name,
        identification.canonical_food_name,
    )
    nutrition = match.nutrition
    nutrition_source = "DATASET" if match.matching_status == "MATCHED" else "UNAVAILABLE"
    estimation_note = None
    quality_warning = (
        MODERATELY_BLURRY_WARNING
        if identification.image_quality == "MODERATELY_BLURRY"
        else None
    )

    if match.matching_status == "NOT_MATCHED" and identification.status == "IDENTIFIED":
        estimation = estimate_nutrition(identification)
        estimation_note = estimation.note
        if estimation.is_available:
            nutrition = estimation.nutrition
            nutrition_source = "AI_ESTIMATED"

    recommendation = generate_recommendation(
        match,
        nutrition=nutrition,
        nutrition_source=nutrition_source,
    )

    note = recommendation["note"]
    if match.match_method in {"CANONICAL", "ALIAS"} and match.reference_name:
        method_description = (
            "nama alternatif yang setara"
            if match.match_method == "ALIAS"
            else "nama dasar"
        )
        reference_note = (
            f"Data nutrisi menggunakan referensi {match.reference_name} "
            f"melalui {method_description}. "
            "Bahan tambahan pada foto dapat menyebabkan nilai sebenarnya berbeda."
        )
        note = f"{note} {reference_note}".strip()

    return {
        "identification": identification.to_dict(),
        "matching": {
            "normalized_name": match.normalized_name,
            "status": match.matching_status,
            "duplicate_count": match.duplicate_count,
            "method": match.match_method,
            "reference_name": match.reference_name,
        },
        "nutrition": nutrition,
        "nutrition_source": nutrition_source,
        "estimation_note": (
            f"{AI_ESTIMATION_DISCLAIMER} {estimation_note}".strip()
            if nutrition_source == "AI_ESTIMATED"
            else estimation_note
        ),
        "quality_warning": quality_warning,
        "recommendation": recommendation["recommendation"],
        "recommendation_details": recommendation["details"],
        "note": note,
    }

