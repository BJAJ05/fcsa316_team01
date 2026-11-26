"""Tests for `analytics`. Run with `pytest` from the backend folder."""

from datetime import timedelta

import pytest
from django.utils import timezone

from accounts.models import User
from analytics.services import student_progress
from assignments.models import Assignment
from classrooms.services import create_class, join_class
from conftest import logged_in_client, make_user
from grading.models import Submission

pytestmark = pytest.mark.django_db


def make_assignment(classroom, title):
    """Create an assignment due tomorrow."""
    return Assignment.objects.create(
        classroom=classroom,
        title=title,
        due_date=timezone.now() + timedelta(days=1),
    )


def test_student_progress_for_classes_without_assignments_is_empty(student):
    assert not student_progress(student)


def test_student_progress_aggregates_only_the_students_submissions(teacher, student):
    classroom = create_class(teacher, "Биологи 10А", "Биологи")
    join_class(student, classroom.code)
    assignments = [make_assignment(classroom, f"Даалгавар {index}") for index in range(4)]
    Submission.objects.create(
        assignment=assignments[0], student=student, score=8, max_score=10
    )
    Submission.objects.create(
        assignment=assignments[1], student=student, score=7, max_score=10
    )
    classmate = make_user("classmate@example.com", User.Role.STUDENT)
    Submission.objects.create(
        assignment=assignments[2], student=classmate, score=10, max_score=10
    )

    result = student_progress(student)

    assert result == [
        {
            "class_id": classroom.pk,
            "class_name": "Биологи 10А",
            "subject": "Биологи",
            "assignment_count": 4,
            "submitted_count": 2,
            "completion_percent": 50,
            "average_percent": 75,
            "assignments": [
                {
                    "id": assignment.pk,
                    "title": assignment.title,
                    "due_date": assignment.due_date,
                    "percent": percent,
                }
                for assignment, percent in zip(assignments, [80, 70, None, None])
            ],
        }
    ]


def test_student_progress_without_submissions_has_zero_completion_and_null_average(
    teacher, student
):
    classroom = create_class(teacher, "Математик", "Математик")
    join_class(student, classroom.code)
    assignment = make_assignment(classroom, "Тэгшитгэл")

    result = student_progress(student)

    assert result[0]["completion_percent"] == 0
    assert result[0]["average_percent"] is None
    assert result[0]["assignments"][0]["percent"] is None
    assert result[0]["assignments"][0]["id"] == assignment.pk


def test_student_progress_for_enrolled_class_without_assignments(teacher, student):
    classroom = create_class(teacher, "Физик", "Физик")
    join_class(student, classroom.code)

    result = student_progress(student)

    assert result[0]["assignment_count"] == 0
    assert result[0]["submitted_count"] == 0
    assert result[0]["completion_percent"] == 0
    assert result[0]["average_percent"] is None
    assert result[0]["assignments"] == []


def test_student_progress_excludes_classes_the_student_did_not_join(teacher, student):
    classroom = create_class(teacher, "Биологи", "Биологи")
    make_assignment(classroom, "Эс")

    assert not student_progress(student)


def test_student_progress_endpoint_is_student_only(teacher, student):
    response = logged_in_client(student).get("/api/analytics/progress/")
    assert response.status_code == 200
    assert response.data == []

    teacher_response = logged_in_client(teacher).get("/api/analytics/progress/")
    assert teacher_response.status_code == 403
