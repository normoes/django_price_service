import json
from decimal import Decimal
from typing import Dict, Any
from unittest import mock

from django.db.models import Q
from django.test import TestCase
from django.utils import timezone
from freezegun import freeze_time
import requests

from ..models import Price
from ..exchange import update_price
from ..alphavantage_api import get_price_for, URL


class TestExchangeTasks(TestCase):
    @mock.patch("price_service_api.exchange.alphavantage_api")
    def test_update_price(self, alphavantage_mock):
        """Test storing a new price.

        Everything works.
        """
        time_ = timezone.now()
        with freeze_time(time_):
            Price.objects.create(
                **{
                    "symbol": "BTC/USD",
                    "price": Decimal("43176"),
                    "created": time_,
                }
            )

        alphavantage_mock.get_price_for.return_value = Decimal("43176")
        with freeze_time(time_):
            price = update_price()

        db_entry = Price.objects.filter().order_by("-created").first()
        self.assertEqual(db_entry.symbol, price.symbol)
        self.assertEqual(db_entry.created, price.created)
        self.assertEqual(db_entry.price, price.price)

        alphavantage_mock.get_price_for.assert_called_once_with(from_currency="BTC", to_currency="USD")

    @mock.patch("price_service_api.exchange.alphavantage_api")
    def test_update_price_exchange_api_error(self, alphavantage_mock):
        """Test storing a new price.

        The alphavantage API request produced an error.
        The method returns 'None' as price.
        """
        alphavantage_mock.get_price_for.return_value = Decimal("0")
        price = update_price()

        self.assertIsNone(price)

        alphavantage_mock.get_price_for.assert_called_once_with(from_currency="BTC", to_currency="USD")


class TestAlphavantageTasks(TestCase):
    @mock.patch("price_service_api.alphavantage_api.requests.get")
    def test_get_price_alphavantage(self, requests_get_mock):
        """Test getting a new price info.

        Everything works.
        """

        response_json = {
            "Realtime Currency Exchange Rate": {
                "01. From_currency Code": "BTC",
                "02. From_currency Name": "Bitcoin",
                "03. To_currency Code": "USD",
                "04. To_currency Name": "United States Dollar",
                "05. Exchange Rate": "43810.15000000",
                "06. Last Refreshed": "2022-01-12 21:41:02",
                "07. Time Zone": "UTC",
                "08. Bid Price": "43810.14000000",
                "09. Ask Price": "43810.15000000",
            }
        }

        requests_get_mock.return_value = mock.MagicMock(
            status_code=requests.codes.ok, json=lambda: response_json, text="<html>...</html>"
        )
        price = get_price_for(from_currency="BTC", to_currency="USD")

        self.assertEqual(price, Decimal("43810.1500000"))

        requests_get_mock.assert_called_once()

    @mock.patch("price_service_api.alphavantage_api.requests.get")
    def test_get_price_alphavantage_api_error(self, requests_get_mock):
        """Test getting a new price info.

        The alphavantage API request produced an error.
        """
        requests_get_mock.get.side_effect = requests.exceptions.ConnectionError
        price = get_price_for(from_currency="BTC", to_currency="USD")

        self.assertEqual(price, Decimal("0"))

        requests_get_mock.assert_called_once()
