"""Authentication classes for the accounts app."""

from drf_spectacular.extensions import OpenApiAuthenticationExtension
from rest_framework.authentication import (
    SessionAuthentication as DRFSessionAuthentication,
)


class SessionAuthentication(DRFSessionAuthentication):
    """Session authentication that advertises its scheme.

    Django REST Framework's default implementation has no authentication
    header, so unauthenticated requests fail with ``403 Forbidden``. Returning a
    scheme makes them fail with ``401 Unauthorized`` instead, which lets the
    frontend distinguish "not signed in" from "not allowed".
    """

    def authenticate_header(self, request) -> str:
        """Return the authentication scheme for unauthenticated responses."""
        return "Session"


class SessionAuthenticationScheme(OpenApiAuthenticationExtension):
    """Describe session authentication in the generated OpenAPI contract."""

    target_class = "apps.accounts.authentication.SessionAuthentication"
    name = "cookieAuth"

    def get_security_definition(self, auto_schema) -> dict:
        """Return the session cookie security scheme."""
        return {
            "type": "apiKey",
            "in": "cookie",
            "name": "sessionid",
        }
