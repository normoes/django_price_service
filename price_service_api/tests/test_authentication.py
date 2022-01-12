from django.contrib import auth
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient


class LogInTest(TestCase):
    """Tests login."""

    def setUp(self):
        """Sets up the User in Default test database."""
        self.credentials = {"username": "TestUser", "password": "TestPassword"}
        User.objects.create_user(**self.credentials)

    def test_login_success(self):
        response = self.client.login(username="TestUser", password="TestPassword")
        self.assertTrue(response)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

    def test_login_fail(self):
        response = self.client.login(username="BadUserName", password="BadPassword")
        self.assertFalse(response)
        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated)


class LogOutTest(TestCase):
    """Tests logout."""

    def setUp(self):
        """Sets up the User in Default test database."""
        self.credentials = {"username": "TestUser", "password": "TestPassword"}
        User.objects.create_user(**self.credentials)

    def test_logout_success(self):
        response = self.client.login(username="TestUser", password="TestPassword")
        self.assertTrue(response)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

        response = self.client.logout()
        self.assertFalse(response)
        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated)


class TokenAuthenticationTest(TestCase):
    def setUp(self):
        """Sets up the User in Default test database and sets APIClient as self.client."""
        self.credentials = {"username": "TestUser", "password": "TestPassword"}
        User.objects.create_user(**self.credentials)
        self.client = APIClient()

    def test_no_publication_with_api_good_token(self):
        """Test publication listing with empty list by using a good API Token."""
        token = Token.objects.get(user__username="TestUser")
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

        response = self.client.get(reverse("price_service_api:list-prices"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "application/json")
        res = response.json()
        self.assertEqual(res["results"], [])

    def test_no_publication_with_bad_api_token(self):
        """Test publication listing with empty list by using a bad API Token."""
        bad_token = "BadToken"
        self.client.credentials(HTTP_AUTHORIZATION="Token " + bad_token)
        response = self.client.get(reverse("price_service_api:list-prices"))

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.headers["content-type"], "application/json")
        self.assertDictEqual(response.json(), {"detail": "Invalid token."})
