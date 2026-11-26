"""Register assignment models with the Django admin (/admin/)."""

from django.contrib import admin

from .models import Assignment


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    """Assignments of every class, with their due dates (US-05)."""

    list_display = ("title", "classroom", "due_date", "created_at")
    list_filter = ("classroom",)
    search_fields = ("title", "classroom__name", "classroom__code")
