"""API tests for /api/assignments/ (US-05). Fixtures: backend/conftest.py."""

from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from assignments.models import Assignment
from classrooms.services import create_class, join_class
from conftest import logged_in_client

pytestmark = pytest.mark.django_db

ASSIGNMENTS_URL = "/api/assignments/"


def detail_url(assignment):
    """URL of one assignment."""
    return f"/api/assignments/{assignment.pk}/"


def in_days(days):
    """An ISO 8601 date-time `days` from now, as the frontend sends it."""
    return (timezone.now() + timedelta(days=days)).isoformat()


@pytest.fixture(name="classroom")
def fixture_classroom(teacher):
    """A class taught by `teacher`."""
    return create_class(teacher, "Biology 10A", "Biology")


@pytest.fixture(name="assignment")
def fixture_assignment(classroom):
    """An open assignment in `classroom`, due tomorrow."""
    return Assignment.objects.create(
        classroom=classroom,
        title="Cells",
        instructions="Read p. 12",
        due_date=timezone.now() + timedelta(days=1),
    )


def new_assignment(classroom, **changes):
    """A valid POST body for `classroom`, with some fields changed."""
    body = {
        "classroom": classroom.pk,
        "title": "Cells",
        "instructions": "Read p. 12",
        "due_date": in_days(7),
    }
    body.update(changes)
    return body


# --- POST /api/assignments/ ----------------------------------------------------------


def test_teacher_creates_assignment_in_own_class(teacher_api, classroom):
    response = teacher_api.post(ASSIGNMENTS_URL, new_assignment(classroom), format="json")

    assert response.status_code == 201
    data = response.json()
    assert set(data) == {
        "id", "classroom", "title", "instructions", "due_date", "is_open", "created_at"
    }
    assert (data["classroom"], data["title"], data["is_open"]) == (classroom.pk, "Cells", True)
    assert data["due_date"].endswith("+08:00")  # shown in the project's time zone
    assert Assignment.objects.get().classroom == classroom


def test_instructions_may_be_left_out(teacher_api, classroom):
    body = new_assignment(classroom)
    del body["instructions"]

    response = teacher_api.post(ASSIGNMENTS_URL, body, format="json")

    assert response.status_code == 201
    assert response.json()["instructions"] == ""


def test_teacher_cannot_create_assignment_in_another_teachers_class(other_teacher, classroom):
    response = logged_in_client(other_teacher).post(
        ASSIGNMENTS_URL, new_assignment(classroom), format="json"
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Анги олдсонгүй."}
    assert not Assignment.objects.exists()


def test_student_cannot_create_assignment(student_api, classroom):
    response = student_api.post(ASSIGNMENTS_URL, new_assignment(classroom), format="json")

    assert response.status_code == 403
    assert not Assignment.objects.exists()


def test_create_requires_login(classroom):
    response = APIClient().post(ASSIGNMENTS_URL, new_assignment(classroom), format="json")

    assert response.status_code == 401


def test_due_date_in_the_past_is_rejected_in_mongolian(teacher_api, classroom):
    response = teacher_api.post(
        ASSIGNMENTS_URL, new_assignment(classroom, due_date=in_days(-1)), format="json"
    )

    assert response.status_code == 400
    assert response.json() == {"due_date": ["Дуусах хугацаа ирээдүйд байх ёстой."]}
    assert not Assignment.objects.exists()


def test_missing_title_due_date_and_class_are_reported_in_mongolian(teacher_api):
    response = teacher_api.post(ASSIGNMENTS_URL, {"title": "  "}, format="json")

    assert response.status_code == 400
    assert response.json() == {
        "classroom": ["Ангийг сонгоно уу."],
        "title": ["Даалгаврын нэрийг оруулна уу."],
        "due_date": ["Дуусах хугацааг оруулна уу."],
    }


def test_title_longer_than_200_characters_is_rejected(teacher_api, classroom):
    response = teacher_api.post(
        ASSIGNMENTS_URL, new_assignment(classroom, title="x" * 201), format="json"
    )

    assert response.status_code == 400
    assert response.json() == {"title": ["Даалгаврын нэр 200 тэмдэгтээс урт байж болохгүй."]}


def test_invalid_due_date_is_rejected(teacher_api, classroom):
    response = teacher_api.post(
        ASSIGNMENTS_URL, new_assignment(classroom, due_date="tomorrow"), format="json"
    )

    assert response.status_code == 400
    assert response.json() == {"due_date": ["Дуусах хугацаа буруу байна."]}


# --- GET /api/assignments/?classroom=<id> --------------------------------------------


def test_teacher_lists_assignments_of_own_class(teacher_api, classroom, assignment):
    response = teacher_api.get(ASSIGNMENTS_URL, {"classroom": classroom.pk})

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [assignment.pk]


def test_enrolled_student_sees_assignments_as_open(student, student_api, classroom, assignment):
    join_class(student, classroom.code)

    response = student_api.get(ASSIGNMENTS_URL, {"classroom": classroom.pk})

    assert response.status_code == 200
    assert [(item["title"], item["is_open"]) for item in response.json()] == [("Cells", True)]
    assert assignment.pk == response.json()[0]["id"]


def test_student_who_has_not_joined_gets_404(student_api, classroom, assignment):
    response = student_api.get(ASSIGNMENTS_URL, {"classroom": classroom.pk})

    assert response.status_code == 404
    assert response.json() == {"detail": "Анги олдсонгүй."}
    assert assignment.pk  # exists, but stays hidden


def test_list_without_classroom_parameter_asks_to_choose_a_class(teacher_api):
    for query in ({}, {"classroom": "abc"}):
        response = teacher_api.get(ASSIGNMENTS_URL, query)

        assert response.status_code == 400
        assert response.json() == {"classroom": ["Ангийг сонгоно уу."]}


# --- GET /api/assignments/<id>/ --------------------------------------------------------


def test_enrolled_student_opens_assignment(student, student_api, classroom, assignment):
    join_class(student, classroom.code)

    response = student_api.get(detail_url(assignment))

    assert response.status_code == 200
    assert response.json()["instructions"] == "Read p. 12"


def test_assignment_of_a_class_not_joined_is_404(student_api, assignment):
    response = student_api.get(detail_url(assignment))

    assert response.status_code == 404
    assert response.json() == {"detail": "Даалгавар олдсонгүй."}


def test_closed_assignment_is_not_open(teacher_api, assignment):
    Assignment.objects.filter(pk=assignment.pk).update(
        due_date=timezone.now() - timedelta(minutes=1)
    )

    response = teacher_api.get(detail_url(assignment))

    assert response.json()["is_open"] is False


# --- PATCH / DELETE /api/assignments/<id>/ --------------------------------------------


def test_teacher_changes_title_and_due_date(teacher_api, assignment):
    new_due = in_days(3)

    response = teacher_api.patch(
        detail_url(assignment), {"title": "Cell structure", "due_date": new_due}, format="json"
    )

    assert response.status_code == 200
    assignment.refresh_from_db()
    assert assignment.title == "Cell structure"
    assert assignment.instructions == "Read p. 12"  # not sent, so unchanged
    assert assignment.due_date.isoformat() == new_due


def test_patch_rejects_due_date_in_the_past(teacher_api, assignment):
    response = teacher_api.patch(detail_url(assignment), {"due_date": in_days(-1)}, format="json")

    assert response.status_code == 400
    assert response.json() == {"due_date": ["Дуусах хугацаа ирээдүйд байх ёстой."]}


def test_other_teacher_cannot_change_or_delete_assignment(other_teacher, assignment):
    client = logged_in_client(other_teacher)

    patched = client.patch(detail_url(assignment), {"title": "Hacked"}, format="json")
    deleted = client.delete(detail_url(assignment))

    assert (patched.status_code, deleted.status_code) == (404, 404)
    assignment.refresh_from_db()
    assert assignment.title == "Cells"


def test_student_cannot_change_or_delete_assignment(student, student_api, classroom, assignment):
    join_class(student, classroom.code)

    patched = student_api.patch(detail_url(assignment), {"title": "Mine"}, format="json")
    deleted = student_api.delete(detail_url(assignment))

    assert (patched.status_code, deleted.status_code) == (403, 403)
    assert Assignment.objects.filter(pk=assignment.pk).exists()


def test_teacher_deletes_assignment(teacher_api, assignment):
    response = teacher_api.delete(detail_url(assignment))

    assert response.status_code == 204
    assert not Assignment.objects.exists()
