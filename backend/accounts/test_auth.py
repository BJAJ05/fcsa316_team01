"""
Tests for US-01: role-based registration, login and JWT (services, API, permissions).
The unit tests for register_user() itself are in test_register_user.py.
"""

import pytest
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse
from rest_framework.request import Request
from rest_framework.test import APIClient, APIRequestFactory
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken

from accounts import services
from accounts.models import User
from accounts.permissions import IsStudent, IsTeacher

PASSWORD = "a-Strong-pass-123"
EMAIL_TAKEN = "Энэ имэйл бүртгэлтэй байна."
BAD_LOGIN = "Имэйл эсвэл нууц үг буруу байна."


@pytest.fixture(name="api")
def fixture_api():
    """DRF test client for calling the API."""
    return APIClient()


def register(api, email="teacher@example.com", password=PASSWORD, role="teacher", **extra):
    """POST to the register endpoint and return the response."""
    return api.post(
        reverse("register"),
        {"email": email, "password": password, "role": role},
        format="json",
        **extra,
    )


# --- Business layer (services.py) -------------------------------------------


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

    raw_access = services.issue_tokens(user)["access"]

    # Decoded the way the API does it for every request (it also checks the signature and type).
    access = JWTAuthentication().get_validated_token(raw_access.encode())

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
        "id": User.objects.get().pk,
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


def request_from(user):
    """A DRF request made by `user`, for calling a permission class directly."""
    request = Request(APIRequestFactory().get("/"))
    request.user = user
    return request


@pytest.mark.parametrize(
    "role, teacher_allowed, student_allowed",
    [("teacher", True, False), ("student", False, True)],
)
def test_role_permissions(role, teacher_allowed, student_allowed):
    request = request_from(User(email="x@example.com", role=role))

    assert IsTeacher().has_permission(request, APIView()) is teacher_allowed
    assert IsStudent().has_permission(request, APIView()) is student_allowed


def test_role_permissions_deny_anonymous_user():
    request = request_from(AnonymousUser())

    assert not IsTeacher().has_permission(request, APIView())
    assert not IsStudent().has_permission(request, APIView())
