
import csv
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from api.models import Nutrition


class Command(BaseCommand):
    help = "Impor dataset nutrisi CSV ke database HealthCoach."

    def handle(self, *args, **options):
        dataset_path = settings.NUTRITION_DATASET_PATH

        if not dataset_path.is_file():
            raise CommandError(
                f"Dataset tidak ditemukan: {dataset_path}"
            )

        required_columns = {
            "id",
            "calories",
            "proteins",
            "fat",
            "carbohydrate",
            "name",
            "image",
            "name_normalized",
        }

        try:
            with dataset_path.open(
                encoding="utf-8-sig", newline=""
            ) as handle:
                reader = csv.DictReader(handle)

                missing = required_columns - set(reader.fieldnames or [])
                if missing:
                    raise CommandError(
                        f"Kolom CSV tidak lengkap: {sorted(missing)}"
                    )

                rows = []
                seen_ids = set()

                for line_number, row in enumerate(reader, start=2):
                    try:
                        food_id = int(row["id"])
                        if food_id <= 0 or food_id in seen_ids:
                            raise ValueError("ID tidak valid atau duplikat")

                        item = {
                            "id": food_id,
                            "name": row["name"].strip(),
                            "name_normalized": row["name_normalized"].strip(),
                            "calories": Decimal(row["calories"]),
                            "proteins": Decimal(row["proteins"]),
                            "fat": Decimal(row["fat"]),
                            "carbohydrate": Decimal(row["carbohydrate"]),
                            "image": row.get("image", "").strip(),
                        }

                        if not item["name"] or not item["name_normalized"]:
                            raise ValueError("Nama makanan kosong")

                        if any(
                            not value.is_finite()
                            for key, value in item.items()
                            if key in {
                                "calories", "proteins", "fat", "carbohydrate"
                            }
                        ):
                            raise ValueError("Nilai nutrisi tidak valid")

                        rows.append(item)
                        seen_ids.add(food_id)

                    except (ValueError, InvalidOperation, TypeError) as exc:
                        raise CommandError(
                            f"Data CSV bermasalah pada baris "
                            f"{line_number}: {exc}"
                        ) from exc

        except (OSError, csv.Error) as exc:
            raise CommandError(f"Gagal membaca CSV: {exc}") from exc

        if not rows:
            raise CommandError("Dataset tidak memiliki data untuk diimpor.")

        with transaction.atomic():
            Nutrition.objects.bulk_create(
                [Nutrition(**row) for row in rows],
                batch_size=500,
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Berhasil mengimpor {len(rows)} data nutrisi."
            )
        )
