"""Unit tests for classroom business rules (services.py). Fixtures: backend/conftest.py."""

from unittest.mock import patch

import pytest
from django.db import IntegrityError

from accounts.models import User
from classrooms import services
from classrooms.models import Classroom, Enrollment
from conftest import make_user

pytestmark = pytest.mark.django_db


# --- US-02: creating a class -------------------------------------------------------


def test_create_class_assigns_teacher_and_generates_six_character_code(teacher):
    classroom = services.create_class(teacher, "Biology 101", "Biology")

    saved = Classroom.objects.get(pk=classroom.pk)
    assert saved.teacher == teacher
    assert saved.name == "Biology 101"
    assert saved.subject == "Biology"
    assert len(saved.code) == 6
    # Only A–Z and 0–9. (Not `isupper()`: it is False for an all-digit code such as "123456".)
    assert set(saved.code) <= set(services.CLASS_CODE_ALPHABET)


def test_create_class_retries_when_generated_code_is_already_in_use(teacher):
    Classroom.objects.create(
        teacher=teacher, name="Existing class", subject="Biology", code="AAAAAA"
    )

    with patch(
        "classrooms.services._generate_class_code",
        side_effect=("AAAAAA", "BBBBBB"),
    ):
        classroom = services.create_class(teacher, "New class", "Chemistry")

    assert classroom.code == "BBBBBB"
    assert Classroom.objects.count() == 2


def test_list_classes_for_teacher_returns_only_their_classes(teacher, other_teacher):
    own_class = services.create_class(teacher, "First", "Biology")
    services.create_class(other_teacher, "Second", "Chemistry")

    assert list(services.list_classes(teacher)) == [own_class]


# --- US-03: joining a class with its code ---------------------------------------------


def test_join_class_accepts_lowercase_code_with_spaces(teacher, student):
    classroom = services.create_class(teacher, "Biology 101", "Biology")

    joined = services.join_class(student, f"  {classroom.code.lower()} ")

    assert joined == classroom
    assert list(classroom.students.all()) == [student]


def test_join_class_with_unknown_code_raises_and_enrolls_nobody(teacher, student):
    services.create_class(teacher, "Biology 101", "Biology")

    with pytest.raises(services.ClassNotFound):
        services.join_class(student, "ZZZZZZ")

    assert not Enrollment.objects.exists()


def test_join_class_twice_raises_already_enrolled(teacher, student):
    classroom = services.create_class(teacher, "Biology 101", "Biology")
    services.join_class(student, classroom.code)

    with pytest.raises(services.AlreadyEnrolled):
        services.join_class(student, classroom.code)

    assert Enrollment.objects.count() == 1


def test_join_class_at_the_same_moment_is_reported_as_already_enrolled(teacher, student):
    # Two "join" requests both pass the "already joined?" check; the database's unique
    # constraint then rejects the second insert. The mock fails the insert the same way.
    classroom = services.create_class(teacher, "Biology 101", "Biology")
    database_rejects_insert = IntegrityError("duplicate key value violates unique constraint")

    with patch(
        "classrooms.services.Enrollment.objects.create", side_effect=database_rejects_insert
    ):
        with pytest.raises(services.AlreadyEnrolled) as raised:
            services.join_class(student, classroom.code)

    assert raised.value.__cause__ is database_rejects_insert


def test_list_classes_for_student_returns_only_joined_classes(teacher, student):
    joined = services.create_class(teacher, "Joined", "Biology")
    services.create_class(teacher, "Not joined", "Chemistry")
    services.join_class(student, joined.code)

    assert list(services.list_classes(student)) == [joined]


def test_get_class_hides_classes_the_user_cannot_see(teacher, other_teacher, student):
    classroom = services.create_class(teacher, "Biology 101", "Biology")

    assert services.get_class(teacher, classroom.pk) == classroom
    with pytest.raises(services.ClassNotFound):
        services.get_class(other_teacher, classroom.pk)
    with pytest.raises(services.ClassNotFound):
        services.get_class(student, classroom.pk)  # not joined yet

    services.join_class(student, classroom.code)
    assert services.get_class(student, classroom.pk) == classroom


# --- US-04: the class roster ----------------------------------------------------------


def test_list_students_returns_enrolled_students_by_email(teacher, student):
    classroom = services.create_class(teacher, "Biology 101", "Biology")
    another = make_user("anar@example.com", User.Role.STUDENT)
    services.join_class(student, classroom.code)
    services.join_class(another, classroom.code)

    roster = services.list_students(teacher, classroom.pk)

    assert [enrollment.student for enrollment in roster] == [another, student]


def test_roster_of_another_teachers_class_is_not_found(teacher, other_teacher):
    classroom = services.create_class(teacher, "Biology 101", "Biology")

    with pytest.raises(services.ClassNotFound):
        services.list_students(other_teacher, classroom.pk)
    with pytest.raises(services.ClassNotFound):
        services.remove_student(other_teacher, classroom.pk, 1)


def test_student_cannot_use_roster_services_even_for_a_joined_class(teacher, student):
    classroom = services.create_class(teacher, "Biology 101", "Biology")
    services.join_class(student, classroom.code)

    with pytest.raises(services.ClassNotFound):
        services.list_students(student, classroom.pk)
    with pytest.raises(services.ClassNotFound):
        services.remove_student(student, classroom.pk, student.pk)
    assert Enrollment.objects.count() == 1


def test_removed_student_loses_the_class_and_may_join_again(teacher, student):
    classroom = services.create_class(teacher, "Biology 101", "Biology")
    services.join_class(student, classroom.code)

    services.remove_student(teacher, classroom.pk, student.pk)

    assert not Enrollment.objects.exists()
    with pytest.raises(services.ClassNotFound):
        services.get_class(student, classroom.pk)
    services.join_class(student, classroom.code)
    assert services.get_class(student, classroom.pk) == classroom


def test_removing_a_student_who_is_not_in_the_class_raises(teacher, student):
    classroom = services.create_class(teacher, "Biology 101", "Biology")

    with pytest.raises(services.StudentNotEnrolled):
        services.remove_student(teacher, classroom.pk, student.pk)
