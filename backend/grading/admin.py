"""Register grading models with the Django admin (/admin/)."""

from django.contrib import admin

from .models import Answer, Submission


class AnswerInline(admin.TabularInline):
    """The graded answers of a submission, shown on the submission's page."""

    model = Answer
    extra = 0


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    """Every student's graded submissions (US-07)."""

    list_display = ("assignment", "student", "score", "max_score", "submitted_at")
    list_filter = ("assignment__classroom",)
    search_fields = ("student__email", "assignment__title")
    inlines = [AnswerInline]
