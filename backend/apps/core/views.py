"""Infrastructure views shared across the backend."""

from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response


@api_view(["GET"])
def health_check(request: Request) -> Response:
    """Report that the application is running and able to serve requests."""
    return Response({"status": "ok"})
