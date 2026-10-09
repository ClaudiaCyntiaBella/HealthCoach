import logging
import uuid

from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import FoodAnalysisUploadSerializer
from .services.pipeline import analyze_food_images


logger = logging.getLogger(__name__)


class HealthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"success": True, "status": "ok", "service": "HealthCoach API"})


class FoodAnalysisView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [AllowAny]

    def post(self, request):
        request_id = str(uuid.uuid4())
        images = request.FILES.getlist("images")

        # Kompatibilitas sementara untuk frontend versi lama yang mengirim `image`.
        if not images and request.FILES.get("image"):
            images = [request.FILES["image"]]

        serializer = FoodAnalysisUploadSerializer(data={"images": images})
        serializer.is_valid(raise_exception=True)

        logger.info("Memulai analisis %s dengan %d foto", request_id, len(images))
        result = analyze_food_images(serializer.validated_data["images"])

        return Response(
            {
                "success": True,
                "data": result,
                "meta": {
                    "request_id": request_id,
                    "images_received": len(images),
                },
            },
            status=status.HTTP_200_OK,
        )

