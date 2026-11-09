"""Tests for the custom email-based User model and its admin pages."""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


@pytest.mark.django_db
def test_create_user_uses_email_as_login():
    user = User.objects.create_user(email="student@example.com", password="s3cret-pass")

    assert user.email == "student@example.com"
    assert user.check_password("s3cret-pass")
    assert not user.is_staff
    assert not user.is_superuser
    assert User.USERNAME_FIELD == "email"


@pytest.mark.django_db
def test_create_user_requires_email():
    with pytest.raises(ValueError):
        User.objects.create_user(email="", password="s3cret-pass")


@pytest.mark.django_db
def test_create_superuser_sets_admin_flags():
    admin_user = User.objects.create_superuser(email="admin@example.com", password="s3cret-pass")

    assert admin_user.is_staff
    assert admin_user.is_superuser


@pytest.mark.django_db
@pytest.mark.parametrize("url_name", ["admin:accounts_user_changelist", "admin:accounts_user_add"])
def test_user_admin_pages_render(client, url_name):
    admin_user = User.objects.create_superuser(email="admin@example.com", password="s3cret-pass")
    client.force_login(admin_user)

    response = client.get(reverse(url_name))

    assert response.status_code == 200


@pytest.mark.django_db
def test_admin_can_create_user_with_email(client):
    admin_user = User.objects.create_superuser(email="admin@example.com", password="s3cret-pass")
    client.force_login(admin_user)

    response = client.post(
        reverse("admin:accounts_user_add"),
        {
            "email": "teacher@example.com",
            "usable_password": "true",
            "password1": "a-Strong-pass-123",
            "password2": "a-Strong-pass-123",
        },
    )

    assert response.status_code == 302
    assert User.objects.get(email="teacher@example.com").check_password("a-Strong-pass-123")
