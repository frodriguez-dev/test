"""Infrastructure views shared across the backend."""

from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from apps.core.serializers import HealthResponseSerializer


@extend_schema(
    tags=["infrastructure"],
    summary="Health check",
    description=(
        "Report that the application is running and able to serve requests. "
        "This endpoint does not touch the database and is meant for probes and "
        "startup checks."
    ),
    responses={200: HealthResponseSerializer},
)
@api_view(["GET"])
def health_check(request: Request) -> Response:
    """Report that the application is running and able to serve requests."""
    return Response({"status": "ok"})
