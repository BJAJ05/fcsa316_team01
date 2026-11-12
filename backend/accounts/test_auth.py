"""Tests for US-01: role-based registration, login and JWT (services, API, permissions)."""

from types import SimpleNamespace

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from accounts import services
from accounts.permissions import IsStudent, IsTeacher

User = get_user_model()

PASSWORD = "a-Strong-pass-123"
EMAIL_TAKEN = "Энэ имэйл бүртгэлтэй байна."
BAD_LOGIN = "Имэйл эсвэл нууц үг буруу байна."


@pytest.fixture
def api():
    return APIClient()


def register(api, email="teacher@example.com", password=PASSWORD, role="teacher", **extra):
    return api.post(
        reverse("register"),
        {"email": email, "password": password, "role": role},
        format="json",
        **extra,
    )


# --- Business layer (services.py) -------------------------------------------


@pytest.mark.django_db
def test_register_user_creates_user_with_role():
    user = services.register_user("Teacher@Example.com", PASSWORD, User.Role.TEACHER)

    assert user.email == "teacher@example.com"
    assert user.is_teacher
    assert user.check_password(PASSWORD)


@pytest.mark.django_db
def test_register_user_rejects_duplicate_email_ignoring_case():
    services.register_user("bat@example.com", PASSWORD, User.Role.STUDENT)

    with pytest.raises(services.EmailAlreadyRegistered):
        services.register_user("BAT@Example.com", PASSWORD, User.Role.TEACHER)

    assert User.objects.count() == 1


@pytest.mark.django_db
def test_login_user_accepts_email_in_any_case():
    created = services.register_user("bat@example.com", PASSWORD, User.Role.STUDENT)

    assert services.login_user("Bat@Example.COM", PASSWORD) == created


@pytest.mark.django_db
@pytest.mark.parametrize(
    "email, password",
    [("bat@example.com", "wrong-password"), ("nobody@example.com", PASSWORD)],
)
def test_login_user_rejects_bad_credentials(email, password):
    services.register_user("bat@example.com", PASSWORD, User.Role.STUDENT)

    with pytest.raises(services.InvalidCredentials):
        services.login_user(email, password)


@pytest.mark.django_db
def test_login_user_rejects_inactive_user():
    user = services.register_user("bat@example.com", PASSWORD, User.Role.STUDENT)
    user.is_active = False
    user.save()

    with pytest.raises(services.InvalidCredentials):
        services.login_user("bat@example.com", PASSWORD)


@pytest.mark.django_db
def test_issue_tokens_puts_role_and_email_in_access_token():
    user = services.register_user("teacher@example.com", PASSWORD, User.Role.TEACHER)

    access = AccessToken(services.issue_tokens(user)["access"])

    assert access["role"] == "teacher"
    assert access["email"] == "teacher@example.com"


# --- POST /api/auth/register/ ------------------------------------------------


@pytest.mark.django_db
@pytest.mark.parametrize("role", ["teacher", "student"])
def test_register_returns_user_and_tokens(api, role):
    response = register(api, email=f"{role}@example.com", role=role)

    assert response.status_code == 201
    body = response.json()
    assert body["user"]["email"] == f"{role}@example.com"
    assert body["user"]["role"] == role
    assert AccessToken(body["access"])["role"] == role
    assert body["refresh"]
    assert User.objects.get(email=f"{role}@example.com").role == role


@pytest.mark.django_db
def test_register_with_taken_email_shows_message_and_creates_nothing(api):
    register(api, email="bat@example.com", role="student")

    response = register(api, email="Bat@Example.com", role="teacher")

    assert response.status_code == 400
    assert response.json() == {"email": [EMAIL_TAKEN]}
    assert User.objects.count() == 1
    assert User.objects.get().role == "student"


@pytest.mark.django_db
@pytest.mark.parametrize("role", ["", "admin", None])
def test_register_requires_teacher_or_student_role(api, role):
    response = register(api, role=role)

    assert response.status_code == 400
    assert "role" in response.json()
    assert not User.objects.exists()


@pytest.mark.django_db
def test_register_rejects_weak_password_in_mongolian(api):
    response = register(api, password="12345678")

    assert response.status_code == 400
    messages = response.json()["password"]
    assert "Нууц үг зөвхөн тооноос бүрдэж болохгүй." in messages
    assert not User.objects.exists()


@pytest.mark.django_db
def test_register_ignores_invalid_token_in_header(api):
    response = register(api, HTTP_AUTHORIZATION="Bearer not-a-real-token")

    assert response.status_code == 201


# --- POST /api/auth/login/ ---------------------------------------------------


@pytest.mark.django_db
def test_login_returns_user_with_role_and_tokens(api):
    services.register_user("teacher@example.com", PASSWORD, User.Role.TEACHER)

    response = api.post(
        reverse("login"), {"email": "Teacher@Example.com", "password": PASSWORD}, format="json"
    )

    assert response.status_code == 200
    body = response.json()
    assert body["user"]["role"] == "teacher"
    assert AccessToken(body["access"])["role"] == "teacher"
    assert body["refresh"]


@pytest.mark.django_db
def test_login_with_wrong_password_returns_401(api):
    services.register_user("teacher@example.com", PASSWORD, User.Role.TEACHER)

    response = api.post(
        reverse("login"), {"email": "teacher@example.com", "password": "wrong"}, format="json"
    )

    assert response.status_code == 401
    assert response.json() == {"detail": BAD_LOGIN}


# --- GET /api/auth/me/ and POST /api/auth/refresh/ ----------------------------


@pytest.mark.django_db
def test_me_returns_logged_in_user(api):
    tokens = register(api, email="student@example.com", role="student").json()
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

    response = api.get(reverse("me"))

    assert response.status_code == 200
    assert response.json() == {
        "id": User.objects.get().id,
        "email": "student@example.com",
        "role": "student",
    }


@pytest.mark.django_db
def test_me_requires_token(api):
    response = api.get(reverse("me"))

    assert response.status_code == 401


@pytest.mark.django_db
def test_refresh_gives_new_access_token_that_keeps_role(api):
    tokens = register(api, role="teacher").json()

    response = api.post(reverse("token-refresh"), {"refresh": tokens["refresh"]}, format="json")

    assert response.status_code == 200
    assert AccessToken(response.json()["access"])["role"] == "teacher"


@pytest.mark.django_db
def test_refresh_with_bad_token_returns_401(api):
    response = api.post(reverse("token-refresh"), {"refresh": "not-a-token"}, format="json")

    assert response.status_code == 401


# --- permissions.py ----------------------------------------------------------


@pytest.mark.parametrize(
    "role, teacher_allowed, student_allowed",
    [("teacher", True, False), ("student", False, True)],
)
def test_role_permissions(role, teacher_allowed, student_allowed):
    request = SimpleNamespace(user=User(email="x@example.com", role=role))

    assert IsTeacher().has_permission(request, None) is teacher_allowed
    assert IsStudent().has_permission(request, None) is student_allowed


def test_role_permissions_deny_anonymous_user():
    request = SimpleNamespace(user=AnonymousUser())

    assert not IsTeacher().has_permission(request, None)
    assert not IsStudent().has_permission(request, None)
