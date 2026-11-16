"""Django app configuration for `classrooms`."""

from django.apps import AppConfig


class ClassroomsConfig(AppConfig):
    """Registers the classrooms (classes, class codes, rosters) app with Django."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "classrooms"
