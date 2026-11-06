"""Endpoint API riwayat analisis makanan pengguna."""

from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import FoodAnalysisHistory
from .history_serializers import FoodAnalysisHistorySerializer


class FoodAnalysisHistoryListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        histories = FoodAnalysisHistory.objects.filter(
            user=request.user
        ).order_by("-created_at", "-id")

        serializer = FoodAnalysisHistorySerializer(
            histories,
            many=True,
        )

        return Response(
            {
                "success": True,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class FoodAnalysisHistoryDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, request, history_id):
        return get_object_or_404(
            FoodAnalysisHistory,
            id=history_id,
            user=request.user,
        )

    def get(self, request, history_id):
        history = self.get_object(request, history_id)

        serializer = FoodAnalysisHistorySerializer(history)

        return Response(
            {
                "success": True,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def delete(self, request, history_id):
        history = self.get_object(request, history_id)
        history.delete()

        return Response(
            {
                "success": True,
                "message": "Riwayat analisis berhasil dihapus.",
            },
            status=status.HTTP_200_OK,
        )