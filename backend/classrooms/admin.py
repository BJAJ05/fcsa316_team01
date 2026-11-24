"""Register classroom models with the Django admin (/admin/)."""

from django.contrib import admin

from .models import Classroom


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    """Admin list view for teacher-created classes."""

    list_display = ("name", "subject", "code", "teacher", "created_at")
    search_fields = ("name", "subject", "code", "teacher__email")
