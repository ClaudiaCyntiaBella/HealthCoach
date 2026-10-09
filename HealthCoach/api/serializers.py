from pathlib import Path

from django.conf import settings
from rest_framework import serializers


ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


class FoodAnalysisUploadSerializer(serializers.Serializer):
    images = serializers.ListField(
        child=serializers.ImageField(allow_empty_file=False, use_url=False),
        allow_empty=False,
        help_text="Kirim 1-5 foto dengan multipart field bernama images.",
    )

    def validate_images(self, images):
        if len(images) > settings.MAX_UPLOAD_IMAGES:
            raise serializers.ValidationError(
                f"Maksimal {settings.MAX_UPLOAD_IMAGES} foto dalam satu analisis."
            )

        max_size = settings.MAX_IMAGE_SIZE_MB * 1024 * 1024
        max_total = settings.MAX_TOTAL_UPLOAD_MB * 1024 * 1024
        total_size = 0

        for image in images:
            suffix = Path(image.name).suffix.lower()
            content_type = (image.content_type or "").lower()

            if suffix not in ALLOWED_IMAGE_EXTENSIONS:
                raise serializers.ValidationError(
                    f"Ekstensi file {image.name} tidak didukung. Gunakan JPG, PNG, atau WEBP."
                )
            if content_type not in ALLOWED_IMAGE_TYPES:
                raise serializers.ValidationError(
                    f"Tipe file {image.name} tidak didukung."
                )
            if image.size > max_size:
                raise serializers.ValidationError(
                    f"Ukuran {image.name} melebihi {settings.MAX_IMAGE_SIZE_MB} MB."
                )
            total_size += image.size

        if total_size > max_total:
            raise serializers.ValidationError(
                f"Total ukuran foto melebihi {settings.MAX_TOTAL_UPLOAD_MB} MB."
            )

        return images

