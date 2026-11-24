"""Business rules for creating and listing classrooms."""

import secrets
import string

from django.db import IntegrityError, transaction

from .models import Classroom

CLASS_CODE_LENGTH = 6
CLASS_CODE_ALPHABET = string.ascii_uppercase + string.digits
MAX_CODE_ATTEMPTS = 10


def _generate_class_code():
    """Return a random six-character code for a class."""
    return "".join(secrets.choice(CLASS_CODE_ALPHABET) for _ in range(CLASS_CODE_LENGTH))


def create_class(teacher, name, subject):
    """Create a class and retry if its generated code collides with an existing class."""
    last_collision = None
    for _ in range(MAX_CODE_ATTEMPTS):
        code = _generate_class_code()
        try:
            with transaction.atomic():
                return Classroom.objects.create(
                    teacher=teacher,
                    name=name,
                    subject=subject,
                    code=code,
                )
        except IntegrityError as error:
            if not Classroom.objects.filter(code=code).exists():
                raise
            last_collision = error

    raise RuntimeError("Could not generate a unique class code.") from last_collision


def list_teacher_classes(teacher):
    """Return the classes owned by a teacher, newest first."""
    return Classroom.objects.filter(teacher=teacher).order_by("-created_at", "-pk")
