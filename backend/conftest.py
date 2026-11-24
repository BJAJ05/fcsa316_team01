"""
Shared pytest fixtures for every app: one user per role, and API clients logged in as them.

    pytestmark = pytest.mark.django_db   # the fixtures below save users, so tests need the DB

    def test_something(teacher_api, student):
        response = teacher_api.get("/api/classes/")

`@pytest.fixture(name=...)` keeps the function names different from the fixture names, so
Pylint does not report `redefined-outer-name` when one fixture uses another.
"""

import pytest
from rest_framework.test import APIClient

from accounts.models import User

PASSWORD = "a-Strong-pass-123"


def make_user(email, role):
    """Save a user with the given role (password: PASSWORD)."""
    return User.objects.create_user(email=email, password=PASSWORD, role=role)


def logged_in_client(user):
    """An API client that sends every request as `user` (no token needed)."""
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture(name="teacher")
def fixture_teacher():
    """A teacher."""
    return make_user("teacher@example.com", User.Role.TEACHER)


@pytest.fixture(name="other_teacher")
def fixture_other_teacher():
    """A second teacher, for checking that teachers cannot see each other's data."""
    return make_user("other.teacher@example.com", User.Role.TEACHER)


@pytest.fixture(name="student")
def fixture_student():
    """A student."""
    return make_user("student@example.com", User.Role.STUDENT)


@pytest.fixture(name="teacher_api")
def fixture_teacher_api(teacher):
    """API client logged in as `teacher`."""
    return logged_in_client(teacher)


@pytest.fixture(name="student_api")
def fixture_student_api(student):
    """API client logged in as `student`."""
    return logged_in_client(student)
