"""Data Access layer for `assignments`: assignments (US-05) and their questions (US-06)."""

from django.db import models
from django.utils import timezone

from classrooms.models import Classroom


class Assignment(models.Model):
    """An exercise in a class with a due date (US-05)."""

    classroom = models.ForeignKey(
        Classroom, on_delete=models.CASCADE, related_name="assignments"
    )
    title = models.CharField("title", max_length=200)
    instructions = models.TextField("instructions", blank=True)
    due_date = models.DateTimeField("due date")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["due_date", "pk"]

    def __str__(self):
        return self.title

    @property
    def is_open(self):
        """True until the due date passes (Lab 5: Assignment.isOpen())."""
        return timezone.now() <= self.due_date


class Question(models.Model):
    """One question of an assignment: multiple choice or fill-in (US-06)."""

    class Kind(models.TextChoices):
        """The two question templates."""

        MULTIPLE_CHOICE = "multiple_choice", "Олон сонголттой"
        FILL_IN = "fill_in", "Нөхөх"

    assignment = models.ForeignKey(
        Assignment, on_delete=models.CASCADE, related_name="questions"
    )
    kind = models.CharField("kind", max_length=20, choices=Kind.choices)
    text = models.TextField("text")
    points = models.PositiveSmallIntegerField("points", default=1)
    position = models.PositiveSmallIntegerField("position", default=0)
    # Only fill-in questions use it; multiple choice marks the right Choice instead.
    correct_answer = models.CharField("correct answer", max_length=255, blank=True)

    class Meta:
        ordering = ["position", "pk"]

    def __str__(self):
        return self.text[:50]


class Choice(models.Model):
    """One option of a multiple-choice question (Lab 5: Question_Option)."""

    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    text = models.CharField("text", max_length=255)
    is_correct = models.BooleanField("correct", default=False)

    class Meta:
        ordering = ["pk"]

    def __str__(self):
        return self.text
