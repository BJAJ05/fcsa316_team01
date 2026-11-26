"""Business rules for classrooms: creating them (US-02) and joining them by code (US-03)."""

import secrets
import string

from django.db import IntegrityError, transaction

from .models import Classroom, Enrollment

CLASS_CODE_LENGTH = 6
CLASS_CODE_ALPHABET = string.ascii_uppercase + string.digits
MAX_CODE_ATTEMPTS = 10


class ClassNotFound(Exception):
    """No class with that code, or a class the user may not see."""


class AlreadyEnrolled(Exception):
    """The student has already joined this class."""


class StudentNotEnrolled(Exception):
    """The student is not (or no longer) in this class."""


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


def list_classes(user):
    """A teacher's own classes, or the classes a student joined; newest first."""
    if user.is_teacher:
        classes = Classroom.objects.filter(teacher=user)
    else:
        classes = Classroom.objects.filter(students=user)
    return classes.select_related("teacher").order_by("-created_at", "-pk")


def get_class(user, class_id):
    """
    One class the user may see (see list_classes). Raises ClassNotFound for any other class,
    so the API answers 404 and does not reveal that another teacher's class exists.
    """
    try:
        return list_classes(user).get(pk=class_id)
    except Classroom.DoesNotExist as error:
        raise ClassNotFound(class_id) from error


def normalize_class_code(code):
    """Codes are stored in uppercase; accept ` ab12cd ` as `AB12CD`."""
    return code.strip().upper()


def join_class(student, code):
    """Enroll a student in the class with this code. Raises ClassNotFound or AlreadyEnrolled."""
    try:
        classroom = Classroom.objects.select_related("teacher").get(code=normalize_class_code(code))
    except Classroom.DoesNotExist as error:
        raise ClassNotFound(code) from error

    if Enrollment.objects.filter(classroom=classroom, student=student).exists():
        raise AlreadyEnrolled(code)
    try:
        with transaction.atomic():
            Enrollment.objects.create(classroom=classroom, student=student)
    except IntegrityError as error:
        # Two "join" clicks at the same moment: the unique constraint lets only one through.
        raise AlreadyEnrolled(code) from error
    return classroom


# --- US-04: the class roster --------------------------------------------------------------


def _get_taught_class(teacher, class_id):
    """
    The teacher's own class. A student is refused here too (not only by the view's IsTeacher):
    for a student, get_class() would return a joined class, and a roster is the teacher's data.
    """
    if not teacher.is_teacher:
        raise ClassNotFound(class_id)
    return get_class(teacher, class_id)


def list_students(teacher, class_id):
    """The enrollments (student and join date) of the teacher's own class, by email."""
    classroom = _get_taught_class(teacher, class_id)
    return (
        Enrollment.objects.filter(classroom=classroom)
        .select_related("student")
        .order_by("student__email")
    )


def remove_student(teacher, class_id, student_id):
    """
    Take a student out of the teacher's own class (US-04). Raises StudentNotEnrolled if they
    are not in it. The student loses access to the class but may join again with its code;
    their past submissions stay in the database (progress and reports skip them).
    """
    classroom = _get_taught_class(teacher, class_id)
    deleted, _ = Enrollment.objects.filter(classroom=classroom, student_id=student_id).delete()
    if not deleted:
        raise StudentNotEnrolled(student_id)
