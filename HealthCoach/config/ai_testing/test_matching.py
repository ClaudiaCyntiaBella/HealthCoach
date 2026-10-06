"""Pengujian exact matching nama makanan Gemini terhadap dataset nutrisi."""

import csv
import unicodedata
from dataclasses import dataclass
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[2]
DATASET_PATH = PROJECT_DIR / "data" / "nutrition_cleaned.csv"

REQUIRED_COLUMNS = {
    "name",
    "name_normalized",
    "calories",
    "proteins",
    "fat",
    "carbohydrate",
}

IDENTIFIED = "IDENTIFIED"
UNKNOWN = "UNKNOWN"
MATCHED = "MATCHED"
NOT_MATCHED = "NOT_MATCHED"


@dataclass(frozen=True)
class MatchResult:
    """Status identifikasi dan pencocokan satu nama makanan."""

    identified_name: str
    normalized_name: str
    identification_status: str
    matching_status: str
    nutrition: dict[str, str] | None
    duplicate_count: int = 0

    @property
    def is_matched(self) -> bool:
        return self.matching_status == MATCHED


def normalize_food_name(food_name: str) -> str:
    """Samakan format nama makanan dengan kolom ``name_normalized`` dataset.

    Aturan ini telah dicek terhadap seluruh baris dataset: lowercase, buang
    tanda baca, dan rapikan whitespace. Contoh: ``Agar-agar`` menjadi
    ``agaragar`` dan ``  NASI   GORENG `` menjadi ``nasi goreng``.
    """
    if not isinstance(food_name, str):
        raise TypeError("Nama makanan harus berupa teks.")

    normalized = unicodedata.normalize("NFKC", food_name).lower()
    normalized = "".join(
        character
        for character in normalized
        if character.isalnum() or character.isspace()
    )
    return " ".join(normalized.split())


def load_nutrition_dataset(
    dataset_path: Path = DATASET_PATH,
) -> dict[str, list[dict[str, str]]]:
    """Muat CSV dan indekskan setiap baris berdasarkan ``name_normalized``."""
    if not dataset_path.is_file():
        raise FileNotFoundError(f"Dataset tidak ditemukan: {dataset_path}")

    with dataset_path.open(encoding="utf-8-sig", newline="") as dataset_file:
        reader = csv.DictReader(dataset_file)
        available_columns = set(reader.fieldnames or [])
        missing_columns = REQUIRED_COLUMNS - available_columns

        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(f"Kolom dataset wajib tidak ditemukan: {missing}")

        index: dict[str, list[dict[str, str]]] = {}
        for row in reader:
            index.setdefault(row["name_normalized"], []).append(row)

    return index


def match_food_name(
    identified_name: str | None,
    dataset_index: dict[str, list[dict[str, str]]],
) -> MatchResult:
    """Pisahkan status identifikasi Gemini dari exact matching dataset."""
    valid_identification = isinstance(identified_name, str) and bool(
        identified_name.strip()
    )

    if not valid_identification:
        return MatchResult(
            identified_name="-",
            normalized_name="-",
            identification_status=UNKNOWN,
            matching_status=NOT_MATCHED,
            nutrition=None,
        )

    identified_name = identified_name.strip()
    normalized_name = normalize_food_name(identified_name)

    # Contoh: hasil Gemini hanya berupa tanda baca. Tidak ada nama makanan
    # yang dapat dicocokkan, sehingga ini diperlakukan sebagai UNKNOWN.
    if not normalized_name:
        return MatchResult(
            identified_name=identified_name,
            normalized_name="-",
            identification_status=UNKNOWN,
            matching_status=NOT_MATCHED,
            nutrition=None,
        )

    matching_rows = dataset_index.get(normalized_name, [])

    if not matching_rows:
        return MatchResult(
            identified_name=identified_name,
            normalized_name=normalized_name,
            identification_status=IDENTIFIED,
            matching_status=NOT_MATCHED,
            nutrition=None,
        )

    # Dataset memiliki beberapa nama normalized duplikat. Baris pertama CSV
    # dipilih secara deterministik; jumlahnya tetap disimpan untuk transparansi.
    return MatchResult(
        identified_name=identified_name,
        normalized_name=normalized_name,
        identification_status=IDENTIFIED,
        matching_status=MATCHED,
        nutrition=matching_rows[0],
        duplicate_count=len(matching_rows),
    )


def print_match_result(result: MatchResult) -> None:
    """Tampilkan hasil matching dan nutrisi yang hanya berasal dari dataset."""
    print(f"Hasil Identifikasi Gemini : {result.identified_name}")
    print(f"Nama Normalized           : {result.normalized_name}")
    print(f"Status Identifikasi       : {result.identification_status}")
    print(f"Status Matching           : {result.matching_status}")

    if not result.is_matched:
        print("Nama Dataset              : -")
        print("Calories                  : -")
        print("Proteins                  : -")
        print("Fat                       : -")
        print("Carbohydrate              : -")

        if result.identification_status == UNKNOWN:
            print(
                "Keterangan                : Makanan belum dapat "
                "diidentifikasi dengan yakin dari foto."
            )
        else:
            print(
                "Keterangan                : Makanan berhasil diidentifikasi, "
                "tetapi informasi nutrisinya belum tersedia pada dataset "
                "HealthCoach."
            )
        return

    nutrition = result.nutrition
    assert nutrition is not None

    print(f"Nama Dataset              : {nutrition['name'].strip()}")
    print(f"Calories                  : {nutrition['calories']}")
    print(f"Proteins                  : {nutrition['proteins']}")
    print(f"Fat                       : {nutrition['fat']}")
    print(f"Carbohydrate              : {nutrition['carbohydrate']}")

    if result.duplicate_count > 1:
        print(
            "Keterangan                : Ditemukan "
            f"{result.duplicate_count} baris dataset dengan nama normalized sama; "
            "baris pertama digunakan."
        )


def run_test_cases() -> None:
    """Jalankan kasus uji exact matching untuk Issue #15."""
    dataset_index = load_nutrition_dataset()
    test_cases = (
        ("Nama persis sama", "Nasi Goreng", IDENTIFIED, MATCHED),
        ("Perbedaan huruf besar/kecil", "nASI gOrEnG", IDENTIFIED, MATCHED),
        ("Spasi berlebih", "  Nasi    Goreng  ", IDENTIFIED, MATCHED),
        ("Tidak tersedia pada dataset", "Pizza", IDENTIFIED, NOT_MATCHED),
        ("Hasil identifikasi kosong", "   ", UNKNOWN, NOT_MATCHED),
    )

    print("=" * 60)
    print("TEST MATCHING DATASET NUTRISI")
    print("=" * 60)
    print(f"Dataset                   : {DATASET_PATH}")
    print(f"Jumlah nama normalized    : {len(dataset_index)}")

    for label, identified_name, expected_identification, expected_matching in test_cases:
        print("\n" + "-" * 60)
        print(f"Test Case                 : {label}")
        result = match_food_name(identified_name, dataset_index)
        assert result.identification_status == expected_identification
        assert result.matching_status == expected_matching
        assert (result.nutrition is not None) == (expected_matching == MATCHED)
        print_match_result(result)


if __name__ == "__main__":
    run_test_cases()
