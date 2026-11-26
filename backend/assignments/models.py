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
