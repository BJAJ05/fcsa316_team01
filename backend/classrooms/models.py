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
        related_name="taught_classes",
    )
    # Students who joined with the class code (US-03); the rows live in Enrollment.
    students = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="Enrollment",
        related_name="joined_classes",
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class Enrollment(models.Model):
    """A student's membership in a class (the Class_Student table of Lab 5)."""

    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name="enrollments")
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            # A student joins a class once; the database refuses a second row.
            models.UniqueConstraint(fields=["classroom", "student"], name="unique_enrollment"),
        ]

    def __str__(self):
        return f"{self.student} → {self.classroom}"
