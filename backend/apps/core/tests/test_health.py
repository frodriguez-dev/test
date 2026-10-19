"""Tests for the health check endpoint."""

from django.test import SimpleTestCase
from django.urls import reverse


class HealthCheckTests(SimpleTestCase):
    """The health endpoint reports readiness without touching the database."""

    def test_get_returns_json_ok(self) -> None:
        response = self.client.get(reverse("core:health"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertEqual(response.json(), {"status": "ok"})

    def test_post_is_not_allowed(self) -> None:
        response = self.client.post(reverse("core:health"))

        self.assertEqual(response.status_code, 405)
