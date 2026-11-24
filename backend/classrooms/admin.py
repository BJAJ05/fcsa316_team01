"""Register classroom models with the Django admin (/admin/)."""

from django.contrib import admin

from .models import Classroom, Enrollment


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    """Admin list view for teacher-created classes."""

    list_display = ("name", "subject", "code", "teacher", "created_at")
    search_fields = ("name", "subject", "code", "teacher__email")


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    """Which student joined which class, and when (US-03)."""

    list_display = ("student", "classroom", "joined_at")
    search_fields = ("student__email", "classroom__name", "classroom__code")
