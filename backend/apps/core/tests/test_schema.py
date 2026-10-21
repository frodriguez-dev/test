"""Tests for the generated OpenAPI schema and documentation endpoints."""

import yaml
from django.conf import settings
from django.test import SimpleTestCase
from django.urls import reverse
from drf_spectacular.generators import SchemaGenerator
from drf_spectacular.validation import validate_schema

COMMITTED_SCHEMA_PATH = settings.BASE_DIR.parent / "docs" / "api" / "openapi.yaml"


def generate_schema() -> dict:
    """Return the OpenAPI document generated from the current URL configuration."""
    return SchemaGenerator().get_schema(request=None, public=True)


class SchemaEndpointTests(SimpleTestCase):
    """The schema and Swagger UI are exposed and describe the health endpoint."""

    def test_schema_endpoint_returns_openapi_document(self) -> None:
        response = self.client.get(reverse("api-schema"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            response["Content-Type"].startswith("application/vnd.oai.openapi")
        )
        schema = yaml.safe_load(response.content)
        self.assertTrue(schema["openapi"].startswith("3."))
        self.assertIn("/api/health/", schema["paths"])

    def test_docs_endpoint_serves_swagger_ui(self) -> None:
        response = self.client.get(reverse("api-docs"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response["Content-Type"])

    def test_health_endpoint_is_documented_with_its_response(self) -> None:
        health = generate_schema()["paths"]["/api/health/"]["get"]

        self.assertEqual(health["summary"], "Health check")
        self.assertEqual(
            health["responses"]["200"]["content"]["application/json"]["schema"],
            {"$ref": "#/components/schemas/HealthResponse"},
        )


class AuthSchemaTests(SimpleTestCase):
    """The generated schema documents the session authentication endpoints."""

    def test_auth_endpoints_are_documented(self) -> None:
        paths = generate_schema()["paths"]

        self.assertIn("/api/v1/auth/csrf/", paths)
        self.assertIn("/api/v1/auth/login/", paths)
        self.assertIn("/api/v1/auth/logout/", paths)
        self.assertIn("/api/v1/auth/me/", paths)

    def test_login_documents_its_request_and_user_response(self) -> None:
        login = generate_schema()["paths"]["/api/v1/auth/login/"]["post"]

        self.assertEqual(login["summary"], "Log in")
        self.assertEqual(
            login["requestBody"]["content"]["application/json"]["schema"],
            {"$ref": "#/components/schemas/Login"},
        )
        self.assertEqual(
            login["responses"]["200"]["content"]["application/json"]["schema"],
            {"$ref": "#/components/schemas/User"},
        )

    def test_login_is_public_and_current_user_requires_a_session(self) -> None:
        schema = generate_schema()
        login = schema["paths"]["/api/v1/auth/login/"]["post"]
        current_user = schema["paths"]["/api/v1/auth/me/"]["get"]

        self.assertNotIn("security", login)
        self.assertEqual(current_user["security"], [{"cookieAuth": []}])


class SchemaContractTests(SimpleTestCase):
    """The generated contract is valid and the committed snapshot is current."""

    def test_generated_schema_is_valid(self) -> None:
        validate_schema(generate_schema())

    def test_committed_schema_matches_generated_schema(self) -> None:
        self.assertTrue(
            COMMITTED_SCHEMA_PATH.is_file(),
            f"Missing committed schema at {COMMITTED_SCHEMA_PATH}",
        )
        with COMMITTED_SCHEMA_PATH.open(encoding="utf-8") as schema_file:
            committed = yaml.safe_load(schema_file)

        self.assertEqual(
            committed,
            generate_schema(),
            "docs/api/openapi.yaml is out of date. Regenerate it with "
            "'uv run manage.py spectacular --file ../docs/api/openapi.yaml'.",
        )

    def test_committed_schema_is_valid(self) -> None:
        with COMMITTED_SCHEMA_PATH.open(encoding="utf-8") as schema_file:
            validate_schema(yaml.safe_load(schema_file))
