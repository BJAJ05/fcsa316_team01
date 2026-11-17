"""Data Access layer for `classrooms`."""

from django.conf import settings
from django.db import models


class Classroom(models.Model):
    """A teacher-owned class that students can identify by its join code."""

    name = models.CharField("class name", max_length=100)
    subject = models.CharField("subject", max_length=100)
    code = models.CharField("class code", max_length=6, unique=True, editable=False)
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="classrooms",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.code})"
