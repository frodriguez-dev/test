"""Configuration for the accounts app."""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """Session authentication endpoints built on Django's user system."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounts"
