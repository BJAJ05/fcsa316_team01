"""Unit tests for classroom business rules."""

from unittest.mock import patch

import pytest

from accounts.models import User
from classrooms.models import Classroom
from classrooms.services import CLASS_CODE_ALPHABET, create_class, list_teacher_classes

pytestmark = pytest.mark.django_db


def test_create_class_assigns_teacher_and_generates_six_character_code():
    teacher = User.objects.create_user(
        email="teacher@example.com",
        password="a-Strong-pass-123",
        role=User.Role.TEACHER,
    )

    classroom = create_class(teacher, "Biology 101", "Biology")

    saved = Classroom.objects.get(pk=classroom.pk)
    assert saved.teacher == teacher
    assert saved.name == "Biology 101"
    assert saved.subject == "Biology"
    assert len(saved.code) == 6
    # Only A–Z and 0–9. (Not `isupper()`: it is False for an all-digit code such as "123456".)
    assert set(saved.code) <= set(CLASS_CODE_ALPHABET)


def test_create_class_retries_when_generated_code_is_already_in_use():
    teacher = User.objects.create_user(
        email="teacher@example.com",
        password="a-Strong-pass-123",
        role=User.Role.TEACHER,
    )
    Classroom.objects.create(
        teacher=teacher,
        name="Existing class",
        subject="Biology",
        code="AAAAAA",
    )

    with patch(
        "classrooms.services._generate_class_code",
        side_effect=("AAAAAA", "BBBBBB"),
    ):
        classroom = create_class(teacher, "New class", "Chemistry")

    assert classroom.code == "BBBBBB"
    assert Classroom.objects.count() == 2


def test_list_teacher_classes_returns_only_that_teachers_classes():
    first_teacher = User.objects.create_user(
        email="first@example.com",
        password="a-Strong-pass-123",
        role=User.Role.TEACHER,
    )
    second_teacher = User.objects.create_user(
        email="second@example.com",
        password="a-Strong-pass-123",
        role=User.Role.TEACHER,
    )
    first_class = create_class(first_teacher, "First", "Biology")
    create_class(second_teacher, "Second", "Chemistry")

    assert list(list_teacher_classes(first_teacher)) == [first_class]
