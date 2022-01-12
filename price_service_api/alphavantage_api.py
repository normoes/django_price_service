from decimal import Decimal
import logging

import requests
from requests.exceptions import RequestException
from django.conf import settings


logger = logging.getLogger(__name__)

URL = "{host}&from_currency={from_currency}&to_currency={to_currency}&apikey={api_key}"


def get_price_for(from_currency: str = "BTC", to_currency: str = "USD") -> Decimal:
    """Requests a new price for the given pair."""
    try:
        url = URL.format(
            host=settings.ALPHAVANTAGE_DATA.get("HOST", ""),
            from_currency=from_currency,
            to_currency=to_currency,
            api_key=settings.ALPHAVANTAGE_DATA.get("API_KEY", ""),
        )
        # TODO: Use reusable session.
        response = requests.get(url, timeout=(5, 10))
        if response is None:
            raise ValueError("API error, because of empty response.")
        if response.status_code != requests.codes.ok:
            raise ValueError(f"[{response.status_code}] Unexpected result: '{response.text}'")
        result = response.json()
        # Normalize API result.
        exchange_rates_ = result.get("Realtime Currency Exchange Rate", {})
        exchange_rates = {}
        for key, value in exchange_rates_.items():
            key_ = key.split()
            exchange_rates[" ".join(key_[1:]).strip().lower() if len(key_) > 1 else key] = value
        logger.debug(exchange_rates)
        return Decimal(exchange_rates.get("exchange rate", "0"))
    except (ValueError, RequestException) as exc:
        logger.error(str(exc))
    return Decimal("0")
