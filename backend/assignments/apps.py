"""Django app configuration for `assignments`."""

from django.apps import AppConfig


class AssignmentsConfig(AppConfig):
    """Registers the assignments (assignments and questions) app with Django."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "assignments"
