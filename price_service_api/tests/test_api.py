from decimal import Decimal
from datetime import datetime, timezone
from unittest import mock

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from freezegun import freeze_time
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from ..models import Price


class PriceListViewTest(TestCase):
    def setUp(self):
        """Sets up the User in Default test database and log in."""
        self.credentials = {"username": "TestUser", "password": "TestPassword"}
        User.objects.create_user(**self.credentials)
        self.client.login(username="TestUser", password="TestPassword")

    def test_no_price(self):
        """Test price listing with empty list."""
        response = self.client.get(reverse("price_service_api:list-prices"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "application/json")
        res = response.json()
        self.assertEqual(res["results"], [])

    def test_single_price(self):
        """Test price listing with a single entry."""

        time_ = timezone.now()
        price = Price.objects.create(
            **{
                "symbol": "BTC/USD",
                "price": Decimal("43176"),
                "created": time_,
            }
        )

        with freeze_time(time_):
            response = self.client.get(reverse("price_service_api:list-prices"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "application/json")
        res = response.json()

        # Normalize creation time.
        result_created = (
            datetime.fromisoformat(res["results"][0]["created"][:-1])
            .replace(microsecond=0)
            .replace(tzinfo=timezone.utc)
        )
        price_created = price.created.replace(microsecond=0).replace(tzinfo=timezone.utc)

        self.assertEqual(result_created, price_created)
        self.assertEqual(res["results"][0]["price"], str(price.price))
        self.assertEqual(res["results"][0]["symbol"], price.symbol)
