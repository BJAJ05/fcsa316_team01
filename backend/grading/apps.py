"""Django app configuration for `grading`."""

from django.apps import AppConfig


class GradingConfig(AppConfig):
    """Registers the grading (submissions and automatic grading) app with Django."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "grading"
