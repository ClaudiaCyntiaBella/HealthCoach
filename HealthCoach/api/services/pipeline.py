from api.services.gemini import identify_food
from api.services.nutrition import get_nutrition_repository
from api.services.recommendation import generate_recommendation


def analyze_food_images(images) -> dict:
    identification = identify_food(images)
    match = get_nutrition_repository().find_for_identification(
        identification.food_name,
        identification.canonical_food_name,
    )
    recommendation = generate_recommendation(match)

    note = recommendation["note"]
    if match.match_method == "CANONICAL" and match.reference_name:
        reference_note = (
            f"Data nutrisi menggunakan referensi {match.reference_name}. "
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
        "nutrition": match.nutrition,
        "recommendation": recommendation["recommendation"],
        "recommendation_details": recommendation["details"],
        "note": note,
    }

