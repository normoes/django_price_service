import logging

from django.db import transaction

from .serializers import (
    PriceInputSerializer,
)
from . import alphavantage_api


logger = logging.getLogger(__name__)


def update_price():
    """Store a new price in the database."""
    price_value = alphavantage_api.get_price_for(from_currency="BTC", to_currency="USD")
    if not price_value:
        return None
    data = {
        "symbol": "BTC/USD",
        "price": price_value,
    }
    serializer = PriceInputSerializer(data=data)
    serializer.is_valid(raise_exception=True)

    price = None
    with transaction.atomic():
        price = serializer.save()

    logger.info(f"Stored '{price}'.")

    return price
