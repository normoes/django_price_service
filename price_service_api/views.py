import logging

from django.http import JsonResponse
from rest_framework import generics, mixins, response, status

from .models import Price
from .serializers import (
    PriceOutputSerializer,
)
from .exchange import update_price


logger = logging.getLogger(__name__)


class PriceList(mixins.ListModelMixin, generics.GenericAPIView):

    # queryset = Price.objects.all()
    serializer_class = PriceOutputSerializer

    def get_queryset(self):
        return Price.objects.filter().order_by("-created")

    def get(self, request, *args, **kwargs):
        logger.info("Get all quotes.")
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        logger.info("Force getting new price for BTC/USD.")
        price = update_price()
        if not price:
            return JsonResponse({"error": "An error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        serializer = PriceOutputSerializer(price)

        return response.Response(serializer.data, status=status.HTTP_201_CREATED)
