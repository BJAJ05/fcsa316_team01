"""API tests for /api/classes/ (US-02 create, US-03 join). Fixtures: backend/conftest.py."""

import pytest
from rest_framework.test import APIClient

from classrooms import services
from classrooms.models import Classroom, Enrollment

pytestmark = pytest.mark.django_db

CLASSES_URL = "/api/classes/"
JOIN_URL = "/api/classes/join/"


def detail_url(classroom):
    """URL of one class."""
    return f"/api/classes/{classroom.pk}/"


# --- US-02: POST /api/classes/ -----------------------------------------------------


def test_teacher_can_create_class_and_receive_join_code(teacher, teacher_api):
    response = teacher_api.post(
        CLASSES_URL, {"name": "Biology 101", "subject": "Biology"}, format="json"
    )

    assert response.status_code == 201
    assert response.data["name"] == "Biology 101"
    assert response.data["subject"] == "Biology"
    assert len(response.data["code"]) == 6
    assert response.data["teacher_email"] == teacher.email
    assert response.data["student_count"] == 0
    assert Classroom.objects.get().teacher == teacher


def test_student_cannot_create_class(student_api):
    response = student_api.post(
        CLASSES_URL, {"name": "Biology 101", "subject": "Biology"}, format="json"
    )

    assert response.status_code == 403
    assert not Classroom.objects.exists()


def test_create_class_requires_nonblank_name_and_subject(teacher_api):
    response = teacher_api.post(CLASSES_URL, {"name": "  ", "subject": ""}, format="json")

    assert response.status_code == 400
    assert set(response.data) == {"name", "subject"}
    assert not Classroom.objects.exists()


def test_create_class_rejects_too_long_or_null_values_in_mongolian(teacher_api):
    response = teacher_api.post(CLASSES_URL, {"name": "x" * 101, "subject": None}, format="json")

    assert response.status_code == 400
    assert response.json() == {
        "name": ["Ангийн нэр 100 тэмдэгтээс урт байж болохгүй."],
        "subject": ["Хичээлийн нэрээ оруулна уу."],
    }
    assert not Classroom.objects.exists()


def test_teacher_list_only_includes_their_own_classes(teacher, other_teacher, teacher_api):
    services.create_class(teacher, "First class", "Biology")
    services.create_class(other_teacher, "Second class", "Chemistry")

    response = teacher_api.get(CLASSES_URL)

    assert response.status_code == 200
    assert [item["name"] for item in response.data] == ["First class"]


# --- US-03: POST /api/classes/join/ --------------------------------------------------


def test_student_joins_class_with_code(teacher, student, student_api):
    classroom = services.create_class(teacher, "Biology 101", "Biology")

    response = student_api.post(JOIN_URL, {"code": f" {classroom.code.lower()} "}, format="json")

    assert response.status_code == 201
    assert response.data["id"] == classroom.pk
    assert response.data["teacher_email"] == teacher.email
    assert response.data["student_count"] == 1
    assert list(classroom.students.all()) == [student]


def test_join_with_unknown_code_shows_message_and_enrolls_nobody(teacher, student_api):
    services.create_class(teacher, "Biology 101", "Biology")

    response = student_api.post(JOIN_URL, {"code": "ZZZZZZ"}, format="json")

    assert response.status_code == 404
    assert response.json() == {"detail": "Ангийн код олдсонгүй."}
    assert not Enrollment.objects.exists()


def test_join_same_class_twice_returns_400(teacher, student_api):
    classroom = services.create_class(teacher, "Biology 101", "Biology")
    student_api.post(JOIN_URL, {"code": classroom.code}, format="json")

    response = student_api.post(JOIN_URL, {"code": classroom.code}, format="json")

    assert response.status_code == 400
    assert response.json() == {"code": ["Та энэ ангид аль хэдийн элссэн байна."]}
    assert Enrollment.objects.count() == 1


def test_join_requires_code(student_api):
    response = student_api.post(JOIN_URL, {"code": "   "}, format="json")

    assert response.status_code == 400
    assert response.json() == {"code": ["Ангийн кодыг оруулна уу."]}


def test_teacher_cannot_join_class(teacher, other_teacher):
    classroom = services.create_class(teacher, "Biology 101", "Biology")
    client = APIClient()
    client.force_authenticate(user=other_teacher)

    response = client.post(JOIN_URL, {"code": classroom.code}, format="json")

    assert response.status_code == 403
    assert not Enrollment.objects.exists()


def test_join_and_list_require_login():
    client = APIClient()

    assert client.post(JOIN_URL, {"code": "AB12CD"}, format="json").status_code == 401
    assert client.get(CLASSES_URL).status_code == 401


# --- US-03: GET /api/classes/ and /api/classes/<id>/ for students --------------------


def test_student_list_only_includes_joined_classes(teacher, student, student_api):
    joined = services.create_class(teacher, "Joined", "Biology")
    services.create_class(teacher, "Not joined", "Chemistry")
    services.join_class(student, joined.code)

    response = student_api.get(CLASSES_URL)

    assert response.status_code == 200
    assert [item["name"] for item in response.data] == ["Joined"]


def test_teacher_sees_student_count_go_up(teacher, student, teacher_api):
    classroom = services.create_class(teacher, "Biology 101", "Biology")
    services.join_class(student, classroom.code)

    response = teacher_api.get(CLASSES_URL)

    assert response.data[0]["student_count"] == 1


def test_class_detail_only_for_its_teacher_and_joined_students(
    teacher, other_teacher, student, teacher_api, student_api
):
    classroom = services.create_class(teacher, "Biology 101", "Biology")
    other_teacher_api = APIClient()
    other_teacher_api.force_authenticate(user=other_teacher)

    assert teacher_api.get(detail_url(classroom)).status_code == 200
    assert other_teacher_api.get(detail_url(classroom)).json() == {"detail": "Анги олдсонгүй."}
    assert student_api.get(detail_url(classroom)).status_code == 404  # not joined yet

    services.join_class(student, classroom.code)
    response = student_api.get(detail_url(classroom))
    assert response.status_code == 200
    assert response.data["name"] == "Biology 101"
