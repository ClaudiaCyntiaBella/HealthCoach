"""Pencarian exact-match nutrisi dari dataset resmi HealthCoach."""

import csv
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from django.apps import apps
from django.conf import settings

from api.exceptions import NutritionDataError


REQUIRED_COLUMNS = {
    "id",
    "name",
    "name_normalized",
    "calories",
    "proteins",
    "fat",
    "carbohydrate",
}


def normalize_food_name(food_name: str) -> str:
    normalized = unicodedata.normalize("NFKC", food_name).lower()
    normalized = "".join(
        char for char in normalized if char.isalnum() or char.isspace()
    )
    return " ".join(normalized.split())


@dataclass(frozen=True)
class NutritionMatch:
    identified_name: str | None
    normalized_name: str | None
    identification_status: str
    matching_status: str
    nutrition: dict | None
    duplicate_count: int = 0

    def to_dict(self) -> dict:
        return {
            "identified_name": self.identified_name,
            "normalized_name": self.normalized_name,
            "identification_status": self.identification_status,
            "matching_status": self.matching_status,
            "nutrition": self.nutrition,
            "duplicate_count": self.duplicate_count,
        }


class CsvNutritionRepository:
    """Adapter sementara; bisa diganti repository PostgreSQL tanpa mengubah view."""

    def __init__(self, dataset_path: Path | None = None):
        self.dataset_path = Path(dataset_path or settings.NUTRITION_DATASET_PATH)
        self._index = None
        self._modified_at = None

    def _load_index(self) -> dict[str, list[dict]]:
        try:
            modified_at = self.dataset_path.stat().st_mtime_ns
        except OSError as exc:
            raise NutritionDataError() from exc

        if self._index is not None and self._modified_at == modified_at:
            return self._index

        try:
            with self.dataset_path.open(encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle)
                missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
                if missing:
                    raise NutritionDataError()

                index: dict[str, list[dict]] = {}
                for row in reader:
                    key = row["name_normalized"].strip()
                    nutrition = {
                        "id": row["id"],
                        "name": row["name"].strip(),
                        "calories": row["calories"],
                        "proteins": row["proteins"],
                        "fat": row["fat"],
                        "carbohydrate": row["carbohydrate"],
                        "image": row.get("image", ""),
                    }
                    index.setdefault(key, []).append(nutrition)
        except (OSError, csv.Error, KeyError) as exc:
            raise NutritionDataError() from exc

        self._index = index
        self._modified_at = modified_at
        return index

    def find_exact(self, food_name: str | None) -> NutritionMatch:
        if not isinstance(food_name, str) or not food_name.strip():
            return NutritionMatch(
                identified_name=None,
                normalized_name=None,
                identification_status="UNKNOWN",
                matching_status="NOT_MATCHED",
                nutrition=None,
            )

        identified_name = food_name.strip()
        normalized_name = normalize_food_name(identified_name)
        if not normalized_name:
            return NutritionMatch(
                identified_name=identified_name,
                normalized_name=None,
                identification_status="UNKNOWN",
                matching_status="NOT_MATCHED",
                nutrition=None,
            )

        rows = self._load_index().get(normalized_name, [])
        return NutritionMatch(
            identified_name=identified_name,
            normalized_name=normalized_name,
            identification_status="IDENTIFIED",
            matching_status="MATCHED" if rows else "NOT_MATCHED",
            nutrition=rows[0] if rows else None,
            duplicate_count=len(rows),
        )


class DjangoNutritionRepository:
    """Adapter ORM untuk model PostgreSQL yang disediakan bagian database."""

    def __init__(self, model_label: str | None = None):
        self.model_label = model_label or settings.NUTRITION_MODEL

    def _model(self):
        try:
            return apps.get_model(self.model_label, require_ready=True)
        except (LookupError, ValueError) as exc:
            raise NutritionDataError() from exc

    def find_exact(self, food_name: str | None) -> NutritionMatch:
        if not isinstance(food_name, str) or not food_name.strip():
            return NutritionMatch(
                identified_name=None,
                normalized_name=None,
                identification_status="UNKNOWN",
                matching_status="NOT_MATCHED",
                nutrition=None,
            )

        identified_name = food_name.strip()
        normalized_name = normalize_food_name(identified_name)
        model = self._model()

        try:
            query = model.objects.filter(name_normalized=normalized_name).order_by("pk")
            duplicate_count = query.count()
            item = query.first()
        except Exception as exc:
            raise NutritionDataError() from exc

        nutrition = None
        if item is not None:
            nutrition = {
                "id": str(item.pk),
                "name": str(item.name),
                "calories": str(item.calories),
                "proteins": str(item.proteins),
                "fat": str(item.fat),
                "carbohydrate": str(item.carbohydrate),
                "image": str(getattr(item, "image", "") or ""),
            }

        return NutritionMatch(
            identified_name=identified_name,
            normalized_name=normalized_name,
            identification_status="IDENTIFIED",
            matching_status="MATCHED" if item is not None else "NOT_MATCHED",
            nutrition=nutrition,
            duplicate_count=duplicate_count,
        )


def get_nutrition_repository():
    if settings.NUTRITION_SOURCE == "database":
        return DjangoNutritionRepository()
    return CsvNutritionRepository()

