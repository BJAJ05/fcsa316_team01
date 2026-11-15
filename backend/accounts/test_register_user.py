"""
Unit tests for accounts.services.register_user() (US-01), the business rule behind
POST /api/auth/register/. It normalizes the email, refuses an email that is already
registered in any letter case, and creates a teacher or student with a hashed password.

Each test is laid out as Arrange / Act / Assert.
"""

from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from accounts.services import EmailAlreadyRegistered, register_user

User = get_user_model()

PASSWORD = "a-Strong-pass-123"

pytestmark = pytest.mark.django_db


# --- Normal cases ---------------------------------------------------------------


def test_registers_teacher_with_hashed_password():
    # Arrange
    email = "teacher@example.com"

    # Act
    user = register_user(email, PASSWORD, User.Role.TEACHER)

    # Assert
    saved = User.objects.get(pk=user.pk)
    assert saved.email == email
    assert saved.role == User.Role.TEACHER
    assert saved.is_teacher
    assert saved.password != PASSWORD  # never stored as plain text
    assert saved.check_password(PASSWORD)


def test_registers_student():
    # Arrange
    email = "student@example.com"

    # Act
    user = register_user(email, PASSWORD, User.Role.STUDENT)

    # Assert
    assert user.role == User.Role.STUDENT
    assert user.is_student
    assert not user.is_teacher
    assert User.objects.count() == 1


# --- Edge cases -----------------------------------------------------------------


def test_normalizes_email_to_lowercase_without_spaces():
    # Arrange
    typed_email = "  Bat@Example.COM "

    # Act
    user = register_user(typed_email, PASSWORD, User.Role.STUDENT)

    # Assert
    assert user.email == "bat@example.com"
    assert User.objects.filter(email="bat@example.com").exists()


def test_rejects_same_email_in_different_case():
    # Arrange
    register_user("bat@example.com", PASSWORD, User.Role.STUDENT)

    # Act + Assert
    with pytest.raises(EmailAlreadyRegistered):
        register_user("BAT@example.com", PASSWORD, User.Role.TEACHER)

    # Assert: no second account, and the first one is unchanged
    assert User.objects.count() == 1
    assert User.objects.get().role == User.Role.STUDENT


def test_rejects_empty_email():
    # Arrange
    empty_email = ""

    # Act + Assert
    with pytest.raises(ValueError):
        register_user(empty_email, PASSWORD, User.Role.STUDENT)

    # Assert
    assert not User.objects.exists()


# --- Mock -------------------------------------------------------------------------


def test_simultaneous_signup_with_same_email_is_reported_as_already_registered():
    # Arrange: two sign-ups with the same email arrive at the same moment. Both pass the
    # "already registered?" check, then the database's unique constraint rejects the second
    # insert with an IntegrityError. That timing can't be reproduced in a test, so the
    # insert is replaced by a mock that fails the same way.
    database_rejects_insert = IntegrityError("duplicate key value violates unique constraint")

    with patch(
        "accounts.services.User.objects.create_user", side_effect=database_rejects_insert
    ) as create_user:
        # Act + Assert
        with pytest.raises(EmailAlreadyRegistered) as raised:
            register_user("Bat@Example.com", PASSWORD, User.Role.STUDENT)

    # Assert: the insert was attempted with the normalized email, the database error is kept
    # as the cause, and nothing was saved.
    create_user.assert_called_once_with(
        email="bat@example.com", password=PASSWORD, role=User.Role.STUDENT
    )
    assert raised.value.__cause__ is database_rejects_insert
    assert not User.objects.exists()
