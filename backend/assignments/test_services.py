"""Unit tests for assignment business rules (services.py, US-05). Fixtures: backend/conftest.py."""

from datetime import timedelta

import pytest
from django.utils import timezone

from assignments import services
from assignments.models import Assignment
from classrooms.services import ClassNotFound, create_class, join_class

pytestmark = pytest.mark.django_db


def tomorrow():
    """A due date one day from now."""
    return timezone.now() + timedelta(days=1)


@pytest.fixture(name="classroom")
def fixture_classroom(teacher):
    """A class taught by `teacher`."""
    return create_class(teacher, "Biology 10A", "Biology")


def test_create_assignment_saves_it_in_the_teachers_class(teacher, classroom):
    due = tomorrow()

    assignment = services.create_assignment(teacher, classroom.pk, "Cells", "Read p. 12", due)

    saved = Assignment.objects.get(pk=assignment.pk)
    assert saved.classroom == classroom
    assert (saved.title, saved.instructions, saved.due_date) == ("Cells", "Read p. 12", due)


def test_create_assignment_in_another_teachers_class_raises_class_not_found(
    other_teacher, classroom
):
    with pytest.raises(ClassNotFound):
        services.create_assignment(other_teacher, classroom.pk, "Cells", "", tomorrow())
    assert not Assignment.objects.exists()


def test_list_assignments_returns_only_that_class_by_due_date(teacher, classroom):
    other_class = create_class(teacher, "Biology 10B", "Biology")
    later = services.create_assignment(teacher, classroom.pk, "Later", "", tomorrow())
    sooner = services.create_assignment(
        teacher, classroom.pk, "Sooner", "", timezone.now() + timedelta(hours=1)
    )
    services.create_assignment(teacher, other_class.pk, "Other class", "", tomorrow())

    assert list(services.list_assignments(teacher, classroom.pk)) == [sooner, later]


def test_enrolled_student_can_list_and_open_assignments(teacher, student, classroom):
    assignment = services.create_assignment(teacher, classroom.pk, "Cells", "", tomorrow())
    join_class(student, classroom.code)

    assert list(services.list_assignments(student, classroom.pk)) == [assignment]
    assert services.get_assignment(student, assignment.pk) == assignment


def test_student_who_has_not_joined_cannot_see_assignments(teacher, student, classroom):
    assignment = services.create_assignment(teacher, classroom.pk, "Cells", "", tomorrow())

    with pytest.raises(ClassNotFound):
        services.list_assignments(student, classroom.pk)
    with pytest.raises(services.AssignmentNotFound):
        services.get_assignment(student, assignment.pk)


def test_get_assignment_of_another_teacher_raises_not_found(teacher, other_teacher, classroom):
    assignment = services.create_assignment(teacher, classroom.pk, "Cells", "", tomorrow())

    with pytest.raises(services.AssignmentNotFound):
        services.get_assignment(other_teacher, assignment.pk)


def test_update_assignment_changes_only_the_given_fields(teacher, classroom):
    assignment = services.create_assignment(
        teacher, classroom.pk, "Cells", "Read p. 12", tomorrow()
    )

    services.update_assignment(teacher, assignment.pk, title="Cell structure")

    saved = Assignment.objects.get(pk=assignment.pk)
    assert (saved.title, saved.instructions) == ("Cell structure", "Read p. 12")


def test_delete_assignment_by_another_teacher_keeps_it(teacher, other_teacher, classroom):
    assignment = services.create_assignment(teacher, classroom.pk, "Cells", "", tomorrow())

    with pytest.raises(services.AssignmentNotFound):
        services.delete_assignment(other_teacher, assignment.pk)
    services.delete_assignment(teacher, assignment.pk)

    assert not Assignment.objects.exists()


def test_is_open_until_the_due_date_passes(classroom):
    open_one = Assignment.objects.create(classroom=classroom, title="Open", due_date=tomorrow())
    closed_one = Assignment.objects.create(
        classroom=classroom, title="Closed", due_date=timezone.now() - timedelta(minutes=1)
    )

    assert open_one.is_open is True
    assert closed_one.is_open is False
