"""Session authentication views."""

from django.contrib.auth import login, logout
from django.middleware.csrf import get_token
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.serializers import (
    CsrfTokenResponseSerializer,
    LoginSerializer,
    UserSerializer,
)


class CsrfTokenView(APIView):
    """Provide a CSRF token for browser clients.

    The response sets the CSRF cookie and repeats the token in the body so the
    frontend can send it in the ``X-CSRFToken`` header on unsafe requests.
    """

    authentication_classes: list[type] = []
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["accounts"],
        summary="Get a CSRF token",
        description=(
            "Set the CSRF cookie and return the token. Send the token in the "
            "`X-CSRFToken` header on every unsafe request."
        ),
        auth=[],
        responses={200: CsrfTokenResponseSerializer},
    )
    def get(self, request: Request) -> Response:
        """Return the CSRF token and ensure the cookie is set."""
        return Response({"csrfToken": get_token(request)})


class LoginView(APIView):
    """Authenticate a user and start a Django session."""

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["accounts"],
        summary="Log in",
        description=(
            "Authenticate with a username and password and start a session. "
            "The response sets the session cookie. The request requires a valid "
            "CSRF token."
        ),
        auth=[],
        request=LoginSerializer,
        responses={
            200: UserSerializer,
            401: OpenApiResponse(description="Invalid credentials."),
        },
    )
    def post(self, request: Request) -> Response:
        """Validate credentials, start a session, and return the user."""
        serializer = LoginSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        login(request, user)

        return Response(UserSerializer(user).data)


class LogoutView(APIView):
    """End the current session."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["accounts"],
        summary="Log out",
        description=(
            "End the current session and clear its data. The request requires a "
            "valid CSRF token."
        ),
        request=None,
        responses={
            204: OpenApiResponse(description="Session ended."),
            401: OpenApiResponse(description="Authentication required."),
        },
    )
    def post(self, request: Request) -> Response:
        """Log out the current user."""
        logout(request)

        return Response(status=status.HTTP_204_NO_CONTENT)


class CurrentUserView(APIView):
    """Return the user for the current session."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["accounts"],
        summary="Get the current user",
        description="Return the user associated with the current session.",
        responses={
            200: UserSerializer,
            401: OpenApiResponse(description="Authentication required."),
        },
    )
    def get(self, request: Request) -> Response:
        """Return the authenticated user."""
        return Response(UserSerializer(request.user).data)
