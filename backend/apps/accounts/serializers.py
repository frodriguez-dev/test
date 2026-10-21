"""Serializers for session authentication endpoints."""

from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed


class UserSerializer(serializers.ModelSerializer):
    """Public representation of the authenticated user."""

    class Meta:
        model = get_user_model()
        fields = ("id", "username", "email", "first_name", "last_name")
        read_only_fields = fields


class LoginSerializer(serializers.Serializer):
    """Credentials accepted by the login endpoint."""

    username = serializers.CharField()
    password = serializers.CharField(
        trim_whitespace=False,
        style={"input_type": "password"},
    )

    def validate(self, attrs: dict) -> dict:
        """Authenticate the credentials and return the matching user."""
        request = self.context.get("request")
        user = authenticate(
            request=request,
            username=attrs["username"],
            password=attrs["password"],
        )
        if user is None:
            raise AuthenticationFailed("Invalid username or password.")

        attrs["user"] = user
        return attrs


class CsrfTokenResponseSerializer(serializers.Serializer):
    """CSRF token returned to browser clients."""

    csrfToken = serializers.CharField(
        help_text=("Token to send in the `X-CSRFToken` header on unsafe requests.")
    )
