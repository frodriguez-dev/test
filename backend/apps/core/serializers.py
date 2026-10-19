"""Serializers for infrastructure endpoints."""

from rest_framework import serializers


class HealthResponseSerializer(serializers.Serializer):
    """Response returned by the health check endpoint."""

    status = serializers.CharField(
        help_text="Readiness marker; `ok` when the application can serve requests."
    )
