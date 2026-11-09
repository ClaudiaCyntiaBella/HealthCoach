
"""Endpoint utama API HealthCoach."""

import logging
import uuid

from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import FoodAnalysisHistory
from .serializers import FoodAnalysisUploadSerializer
from .services.pipeline import analyze_food_images


logger = logging.getLogger(__name__)


class HealthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(
            {
                "success": True,
                "status": "ok",
                "service": "HealthCoach API",
            }
        )


class FoodAnalysisView(APIView):
    """Menganalisis foto makanan dan menyimpan riwayat pengguna login."""

    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [AllowAny]

    def post(self, request):
        request_id = str(uuid.uuid4())
        images = request.FILES.getlist("images")

        # Kompatibilitas frontend lama yang menggunakan field "image".
        if not images and request.FILES.get("image"):
            images = [request.FILES["image"]]

        serializer = FoodAnalysisUploadSerializer(
            data={"images": images}
        )
        serializer.is_valid(raise_exception=True)

        logger.info(
            "Memulai analisis %s dengan %d foto",
            request_id,
            len(images),
        )

        # Menjalankan pipeline analisis yang sudah tersedia.
        result = analyze_food_images(
            serializer.validated_data["images"]
        )

        # Hanya hasil analisis pengguna login yang disimpan.
        history_id = None

        if (
            request.user.is_authenticated
            and result.get("identification", {}).get(
                "identification_status"
            ) != "UNKNOWN"
        ):
            history = FoodAnalysisHistory.objects.create(
                user=request.user,
                result=result,
            )
            history_id = history.id

            logger.info(
                "Riwayat analisis berhasil disimpan: request_id=%s history_id=%s",
                request_id,
                history_id,
            )

        return Response(
            {
                "success": True,
                "data": result,
                "meta": {
                    "request_id": request_id,
                    "images_received": len(images),
                    "history_id": history_id,
                },
            },
            status=status.HTTP_200_OK,
        )
