"""Unit tests for assignment business rules (services.py, US-05). Fixtures: backend/conftest.py."""

from datetime import timedelta

import pytest
from django.utils import timezone

from assignments import services
from assignments.models import Assignment, Choice, Question
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


# --- US-06: questions ----------------------------------------------------------------------


def multiple_choice(text="2 + 2 = ?", points=2):
    """Validated data of a multiple-choice question, as QuestionInputSerializer returns it."""
    return {
        "kind": "multiple_choice",
        "text": text,
        "points": points,
        "correct_answer": "",
        "choices": [{"text": "3", "is_correct": False}, {"text": "4", "is_correct": True}],
    }


def test_add_question_saves_choices_and_puts_it_last(teacher, classroom):
    assignment = services.create_assignment(teacher, classroom.pk, "Math", "", tomorrow())

    first = services.add_question(teacher, assignment.pk, multiple_choice("First"))
    second = services.add_question(teacher, assignment.pk, multiple_choice("Second"))

    assert (first.position, second.position) == (0, 1)
    assert [(c.text, c.is_correct) for c in Choice.objects.filter(question=first)] == [
        ("3", False),
        ("4", True),
    ]
    # question_count is added by .annotate() in services, not a model field, so the editor
    # cannot know it: read it the way the serializer does.
    assert getattr(services.get_assignment(teacher, assignment.pk), "question_count") == 2


def test_add_question_to_another_teachers_assignment_is_refused(
    teacher, other_teacher, classroom
):
    assignment = services.create_assignment(teacher, classroom.pk, "Math", "", tomorrow())

    with pytest.raises(services.AssignmentNotFound):
        services.add_question(other_teacher, assignment.pk, multiple_choice())
    assert not Question.objects.exists()


def test_delete_question_removes_it_with_its_choices(teacher, classroom):
    assignment = services.create_assignment(teacher, classroom.pk, "Math", "", tomorrow())
    question = services.add_question(teacher, assignment.pk, multiple_choice())

    services.delete_question(teacher, assignment.pk, question.pk)

    assert not Question.objects.exists()
    assert not Choice.objects.exists()


def test_delete_question_of_another_assignment_raises_not_found(teacher, classroom):
    first = services.create_assignment(teacher, classroom.pk, "First", "", tomorrow())
    second = services.create_assignment(teacher, classroom.pk, "Second", "", tomorrow())
    question = services.add_question(teacher, first.pk, multiple_choice())

    with pytest.raises(services.QuestionNotFound):
        services.delete_question(teacher, second.pk, question.pk)
    assert Question.objects.filter(pk=question.pk).exists()
