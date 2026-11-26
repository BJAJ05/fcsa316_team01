"""Data Access layer for `grading`: submitted and graded assignments (US-07)."""

from django.conf import settings
from django.db import models

from assignments.models import Assignment, Choice, Question


class Submission(models.Model):
    """A student's graded answers to one assignment; one per student (US-07)."""

    assignment = models.ForeignKey(
        Assignment, on_delete=models.CASCADE, related_name="submissions"
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="submissions"
    )
    score = models.PositiveIntegerField("score")
    max_score = models.PositiveIntegerField("max score")
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["assignment", "student"], name="unique_submission"),
        ]

    def __str__(self):
        return f"{self.student} – {self.assignment}: {self.score}/{self.max_score}"

    @property
    def percent(self):
        """The score as a whole percentage, 0–100."""
        return round(self.score * 100 / self.max_score) if self.max_score else 0


class Answer(models.Model):
    """A student's answer to one question and its result (US-07)."""

    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    choice = models.ForeignKey(
        Choice, on_delete=models.SET_NULL, null=True, blank=True, related_name="answers"
    )
    text = models.CharField("text", max_length=255, blank=True)
    is_correct = models.BooleanField("correct")
    points_awarded = models.PositiveSmallIntegerField("points awarded", default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["submission", "question"], name="unique_answer"),
        ]

    def __str__(self):
        return f"{self.submission} – {self.question}"
