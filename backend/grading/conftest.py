"""
Fixtures for the grading tests (US-07): a class with an enrolled student, and an open
assignment with a multiple-choice and a fill-in question. Users: backend/conftest.py.
"""

from datetime import timedelta

import pytest
from django.utils import timezone

from assignments import services as assignment_services
from assignments.models import Assignment, Choice, Question
from classrooms import services as class_services


def add_questions(teacher, assignment):
    """A 2-point multiple-choice question ("4" is right) and a 3-point fill-in question."""
    multiple_choice = assignment_services.add_question(
        teacher,
        assignment.pk,
        {
            "kind": Question.Kind.MULTIPLE_CHOICE,
            "text": "2 + 2 = ?",
            "points": 2,
            "correct_answer": "",
            "choices": [{"text": "3", "is_correct": False}, {"text": "4", "is_correct": True}],
        },
    )
    fill_in = assignment_services.add_question(
        teacher,
        assignment.pk,
        {
            "kind": Question.Kind.FILL_IN,
            "text": "Монголын нийслэл?",
            "points": 3,
            "correct_answer": "Улаанбаатар",
            "choices": [],
        },
    )
    return multiple_choice, fill_in


def choice(question, text):
    """The option of `question` with this text."""
    return Choice.objects.get(question=question, text=text)


@pytest.fixture(name="classroom")
def fixture_classroom(teacher, student):
    """The teacher's class, which the student has joined."""
    classroom = class_services.create_class(teacher, "Math", "Math")
    class_services.join_class(student, classroom.code)
    return classroom


@pytest.fixture(name="assignment")
def fixture_assignment(classroom):
    """An open assignment of the class (due tomorrow), without questions."""
    return Assignment.objects.create(
        classroom=classroom, title="Quiz", due_date=timezone.now() + timedelta(days=1)
    )


@pytest.fixture(name="questions")
def fixture_questions(teacher, assignment):
    """The assignment's two questions: (multiple choice, fill-in)."""
    return add_questions(teacher, assignment)
