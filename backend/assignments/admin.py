"""Register assignment models with the Django admin (/admin/)."""

from django.contrib import admin

from .models import Assignment, Choice, Question


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    """Assignments of every class, with their due dates (US-05)."""

    list_display = ("title", "classroom", "due_date", "created_at")
    list_filter = ("classroom",)
    search_fields = ("title", "classroom__name", "classroom__code")


class ChoiceInline(admin.TabularInline):
    """The options of a multiple-choice question, edited on the question's page."""

    model = Choice
    extra = 0


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Questions of every assignment, with their options (US-06)."""

    list_display = ("text", "assignment", "kind", "points", "position")
    list_filter = ("kind",)
    search_fields = ("text", "assignment__title")
    inlines = [ChoiceInline]
