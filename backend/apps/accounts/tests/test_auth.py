"""Tests for the session authentication API."""

import json

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class CsrfEndpointTests(TestCase):
    """The CSRF endpoint sets the cookie and returns the token."""

    def test_get_sets_csrf_cookie_and_returns_token(self) -> None:
        response = self.client.get(reverse("accounts:csrf"))

        self.assertEqual(response.status_code, 200)
        token = response.json()["csrfToken"]
        self.assertTrue(token)
        self.assertIn(settings.CSRF_COOKIE_NAME, response.cookies)

        cookie = response.cookies[settings.CSRF_COOKIE_NAME]
        self.assertTrue(cookie.value)
        self.assertEqual(cookie["samesite"], settings.CSRF_COOKIE_SAMESITE)
        self.assertEqual(bool(cookie["secure"]), settings.CSRF_COOKIE_SECURE)


class LoginTests(TestCase):
    """Login starts a session for valid credentials and rejects invalid ones."""

    def setUp(self) -> None:
        self.password = "correct-horse-battery-staple"
        self.user = User.objects.create_user(
            username="alice",
            email="alice@example.com",
            password=self.password,
            first_name="Alice",
        )
        self.url = reverse("accounts:login")

    def test_login_returns_user_and_starts_session(self) -> None:
        response = self.client.post(
            self.url,
            data=json.dumps(
                {"username": "alice", "password": self.password}
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "id": self.user.pk,
                "username": "alice",
                "email": "alice@example.com",
                "first_name": "Alice",
                "last_name": "",
            },
        )
        self.assertEqual(
            int(self.client.session["_auth_user_id"]),
            self.user.pk,
        )
        self.assertIn(settings.SESSION_COOKIE_NAME, response.cookies)

    def test_login_rejects_invalid_credentials(self) -> None:
        response = self.client.post(
            self.url,
            data=json.dumps({"username": "alice", "password": "wrong"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Invalid username or password."})
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_login_rejects_missing_fields(self) -> None:
        response = self.client.post(
            self.url,
            data=json.dumps({"username": "alice"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("password", response.json())

    def test_login_requires_csrf_token(self) -> None:
        client = Client(enforce_csrf_checks=True)

        response = client.post(
            self.url,
            data=json.dumps(
                {"username": "alice", "password": self.password}
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 403)
        self.assertNotIn("_auth_user_id", client.session)

    def test_login_accepts_csrf_token_from_cookie(self) -> None:
        client = Client(enforce_csrf_checks=True)
        csrf_response = client.get(reverse("accounts:csrf"))
        token = csrf_response.json()["csrfToken"]

        response = client.post(
            self.url,
            data=json.dumps(
                {"username": "alice", "password": self.password}
            ),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=token,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(int(client.session["_auth_user_id"]), self.user.pk)


class CurrentUserTests(TestCase):
    """The current-user endpoint reflects the session state."""

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="alice",
            password="correct-horse-battery-staple",
        )
        self.url = reverse("accounts:me")

    def test_anonymous_request_returns_unauthorized(self) -> None:
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response["WWW-Authenticate"], "Session")

    def test_authenticated_request_returns_user(self) -> None:
        self.client.force_login(self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["username"], "alice")
        self.assertNotIn("password", response.json())


class LogoutTests(TestCase):
    """Logout ends the session and requires authentication."""

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="alice",
            password="correct-horse-battery-staple",
        )
        self.url = reverse("accounts:logout")

    def test_anonymous_logout_returns_unauthorized(self) -> None:
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 401)

    def test_logout_clears_session(self) -> None:
        self.client.force_login(self.user)

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 204)
        self.assertNotIn("_auth_user_id", self.client.session)
        me_response = self.client.get(reverse("accounts:me"))
        self.assertEqual(me_response.status_code, 401)

    def test_logout_requires_csrf_token(self) -> None:
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)

        response = client.post(self.url)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(int(client.session["_auth_user_id"]), self.user.pk)


class SessionCookieTests(TestCase):
    """Session cookies use the configured security attributes."""

    def test_session_cookie_is_httponly_and_samesite_lax(self) -> None:
        User.objects.create_user(
            username="alice",
            password="correct-horse-battery-staple",
        )
        response = self.client.post(
            reverse("accounts:login"),
            data=json.dumps(
                {"username": "alice", "password": "correct-horse-battery-staple"}
            ),
            content_type="application/json",
        )

        cookie = response.cookies[settings.SESSION_COOKIE_NAME]
        self.assertTrue(cookie["httponly"])
        self.assertEqual(cookie["samesite"], "Lax")
        self.assertEqual(bool(cookie["secure"]), settings.SESSION_COOKIE_SECURE)
