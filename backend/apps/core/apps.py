"""Application configuration for the core app."""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Register infrastructure endpoints such as the health check."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
