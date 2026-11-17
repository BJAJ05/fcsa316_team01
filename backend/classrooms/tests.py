"""API tests for classroom creation and teacher-only access."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from classrooms.models import Classroom

User = get_user_model()

pytestmark = pytest.mark.django_db


def make_user(email, role):
    """Create a user for authenticated API requests."""
    return User.objects.create_user(
        email=email,
        password="a-Strong-pass-123",
        role=role,
    )


def test_teacher_can_create_class_and_receive_join_code():
    teacher = make_user("teacher@example.com", User.Role.TEACHER)
    client = APIClient()
    client.force_authenticate(user=teacher)

    response = client.post(
        "/api/classes/",
        {"name": "Biology 101", "subject": "Biology"},
        format="json",
    )

    assert response.status_code == 201
    assert response.data["name"] == "Biology 101"
    assert response.data["subject"] == "Biology"
    assert len(response.data["code"]) == 6
    assert Classroom.objects.get().teacher == teacher


def test_student_cannot_create_or_list_classes():
    student = make_user("student@example.com", User.Role.STUDENT)
    client = APIClient()
    client.force_authenticate(user=student)

    create_response = client.post(
        "/api/classes/",
        {"name": "Biology 101", "subject": "Biology"},
        format="json",
    )
    list_response = client.get("/api/classes/")

    assert create_response.status_code == 403
    assert list_response.status_code == 403
    assert not Classroom.objects.exists()


def test_create_class_requires_nonblank_name_and_subject():
    teacher = make_user("teacher@example.com", User.Role.TEACHER)
    client = APIClient()
    client.force_authenticate(user=teacher)

    response = client.post(
        "/api/classes/",
        {"name": "  ", "subject": ""},
        format="json",
    )

    assert response.status_code == 400
    assert set(response.data) == {"name", "subject"}
    assert not Classroom.objects.exists()


def test_teacher_list_only_includes_their_own_classes():
    first_teacher = make_user("first@example.com", User.Role.TEACHER)
    second_teacher = make_user("second@example.com", User.Role.TEACHER)
    Classroom.objects.create(
        teacher=first_teacher,
        name="First class",
        subject="Biology",
        code="AAAAAA",
    )
    Classroom.objects.create(
        teacher=second_teacher,
        name="Second class",
        subject="Chemistry",
        code="BBBBBB",
    )
    client = APIClient()
    client.force_authenticate(user=first_teacher)

    response = client.get("/api/classes/")

    assert response.status_code == 200
    assert [item["name"] for item in response.data] == ["First class"]
