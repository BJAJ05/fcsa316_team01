"""Django app configuration for `analytics`."""

from django.apps import AppConfig


class AnalyticsConfig(AppConfig):
    """Registers the analytics (progress and class reports) app with Django."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "analytics"
