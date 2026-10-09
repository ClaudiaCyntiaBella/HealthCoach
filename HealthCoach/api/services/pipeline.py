from api.services.gemini import identify_food
from api.services.nutrition import get_nutrition_repository
from api.services.recommendation import generate_recommendation


def analyze_food_images(images) -> dict:
    identification = identify_food(images)
    match = get_nutrition_repository().find_exact(identification.food_name)
    recommendation = generate_recommendation(match)

    return {
        "identification": identification.to_dict(),
        "matching": {
            "normalized_name": match.normalized_name,
            "status": match.matching_status,
            "duplicate_count": match.duplicate_count,
        },
        "nutrition": match.nutrition,
        "recommendation": recommendation["recommendation"],
        "note": recommendation["note"],
    }

