
"""Repository pencarian nutrisi dari dataset resmi HealthCoach."""

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
    """Menormalkan nama makanan agar konsisten dengan dataset."""
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
    match_method: str = "NONE"
    reference_name: str | None = None

    def to_dict(self) -> dict:
        return {
            "identified_name": self.identified_name,
            "normalized_name": self.normalized_name,
            "identification_status": self.identification_status,
            "matching_status": self.matching_status,
            "nutrition": self.nutrition,
            "duplicate_count": self.duplicate_count,
            "match_method": self.match_method,
            "reference_name": self.reference_name,
        }


class CsvNutritionRepository:
    """Repository nutrisi berbasis CSV."""

    def __init__(self, dataset_path: Path | None = None):
        self.dataset_path = Path(
            dataset_path or settings.NUTRITION_DATASET_PATH
        )
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
            with self.dataset_path.open(
                encoding="utf-8-sig", newline=""
            ) as handle:
                reader = csv.DictReader(handle)

                missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
                if missing:
                    raise NutritionDataError()

                index: dict[str, list[dict]] = {}

                for row in reader:
                    key = normalize_food_name(
                        row["name_normalized"].strip()
                    )

                    if not key:
                        continue

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

        except NutritionDataError:
            raise
        except (OSError, csv.Error, KeyError, AttributeError) as exc:
            raise NutritionDataError() from exc

        self._index = index
        self._modified_at = modified_at

        return index

    def _find_rows(self, normalized_name: str) -> list[dict]:
        return self._load_index().get(normalized_name, [])

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

        rows = self._find_rows(normalized_name)

        return NutritionMatch(
            identified_name=identified_name,
            normalized_name=normalized_name,
            identification_status="IDENTIFIED",
            matching_status="MATCHED" if rows else "NOT_MATCHED",
            nutrition=rows[0] if rows else None,
            duplicate_count=len(rows),
            match_method="EXACT" if rows else "NONE",
        )

    def find_for_identification(
        self,
        food_name: str | None,
        canonical_food_name: str | None,
    ) -> NutritionMatch:
        """Cari nama spesifik dahulu, lalu nama dasar secara exact."""

        exact_match = self.find_exact(food_name)

        if exact_match.matching_status == "MATCHED":
            return exact_match

        if not isinstance(food_name, str) or not food_name.strip():
            return exact_match

        if (
            not isinstance(canonical_food_name, str)
            or not canonical_food_name.strip()
        ):
            return exact_match

        canonical_name = canonical_food_name.strip()
        normalized_canonical = normalize_food_name(canonical_name)

        if not normalized_canonical:
            return exact_match

        rows = self._find_rows(normalized_canonical)

        if not rows:
            return exact_match

        return NutritionMatch(
            identified_name=food_name.strip(),
            normalized_name=exact_match.normalized_name,
            identification_status="IDENTIFIED",
            matching_status="MATCHED",
            nutrition=rows[0],
            duplicate_count=len(rows),
            match_method="CANONICAL",
            reference_name=rows[0]["name"],
        )


class DjangoNutritionRepository:
    """Repository nutrisi berbasis model PostgreSQL Django."""

    def __init__(self, model_label: str | None = None):
        self.model_label = model_label or settings.NUTRITION_MODEL

    def _model(self):
        try:
            return apps.get_model(
                self.model_label,
                require_ready=True,
            )
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

        if not normalized_name:
            return NutritionMatch(
                identified_name=identified_name,
                normalized_name=None,
                identification_status="UNKNOWN",
                matching_status="NOT_MATCHED",
                nutrition=None,
            )

        model = self._model()

        try:
            query = model.objects.filter(
                name_normalized=normalized_name
            ).order_by("pk")

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
            match_method="EXACT" if item is not None else "NONE",
        )

    def find_for_identification(
        self,
        food_name: str | None,
        canonical_food_name: str | None,
    ) -> NutritionMatch:
        """Cari nama spesifik dahulu, lalu nama dasar secara exact."""

        exact_match = self.find_exact(food_name)

        if exact_match.matching_status == "MATCHED":
            return exact_match

        if not isinstance(food_name, str) or not food_name.strip():
            return exact_match

        if (
            not isinstance(canonical_food_name, str)
            or not canonical_food_name.strip()
        ):
            return exact_match

        canonical_name = canonical_food_name.strip()
        normalized_canonical = normalize_food_name(canonical_name)

        if not normalized_canonical:
            return exact_match

        model = self._model()

        try:
            query = model.objects.filter(
                name_normalized=normalized_canonical
            ).order_by("pk")

            duplicate_count = query.count()
            item = query.first()

        except Exception as exc:
            raise NutritionDataError() from exc

        if item is None:
            return exact_match

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
            identified_name=food_name.strip(),
            normalized_name=exact_match.normalized_name,
            identification_status="IDENTIFIED",
            matching_status="MATCHED",
            nutrition=nutrition,
            duplicate_count=duplicate_count,
            match_method="CANONICAL",
            reference_name=str(item.name),
        )


def get_nutrition_repository():
    if settings.NUTRITION_SOURCE == "database":
        return DjangoNutritionRepository()

    return CsvNutritionRepository()
