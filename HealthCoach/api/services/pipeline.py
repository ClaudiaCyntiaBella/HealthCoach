from api.services.gemini import identify_food
from api.services.estimation import AI_ESTIMATION_DISCLAIMER, estimate_nutrition
from api.services.nutrition import get_nutrition_repository
from api.services.recommendation import generate_recommendation


def analyze_food_images(images) -> dict:
    identification = identify_food(images)
    match = get_nutrition_repository().find_for_identification(
        identification.food_name,
        identification.canonical_food_name,
    )
    nutrition = match.nutrition
    nutrition_source = "DATASET" if match.matching_status == "MATCHED" else "UNAVAILABLE"
    estimation_note = None

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
        "nutrition": nutrition,
        "nutrition_source": nutrition_source,
        "estimation_note": (
            f"{AI_ESTIMATION_DISCLAIMER} {estimation_note}".strip()
            if nutrition_source == "AI_ESTIMATED"
            else estimation_note
        ),
        "recommendation": recommendation["recommendation"],
        "recommendation_details": recommendation["details"],
        "note": note,
    }

