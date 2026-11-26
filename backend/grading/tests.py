"""API tests for /api/submissions/ (US-07). Fixtures: grading/conftest.py, backend/conftest.py."""

from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from accounts.models import User
from assignments.models import Assignment
from classrooms import services as class_services
from conftest import logged_in_client, make_user
from grading.conftest import add_questions, choice
from grading.models import Submission

pytestmark = pytest.mark.django_db

SUBMISSIONS_URL = "/api/submissions/"
RESULT_FIELDS = {
    "question", "text", "kind", "your_answer", "is_correct", "points_awarded", "points"
}


def submit(client, assignment, answers):
    """POST a submission of `assignment` with these answers."""
    return client.post(
        SUBMISSIONS_URL, {"assignment": assignment.pk, "answers": answers}, format="json"
    )


def classmate_api(classroom):
    """API client of a second student who has joined the same class."""
    classmate = make_user("classmate@example.com", User.Role.STUDENT)
    class_services.join_class(classmate, classroom.code)
    return logged_in_client(classmate)


# --- POST /api/submissions/ -----------------------------------------------------------


def test_student_submits_and_sees_the_score_and_each_result(student_api, assignment, questions):
    multiple_choice, fill_in = questions

    response = submit(
        student_api,
        assignment,
        [
            {"question": multiple_choice.pk, "choice": choice(multiple_choice, "3").pk},
            {"question": fill_in.pk, "text": " улаанбаатар "},
        ],
    )

    assert response.status_code == 201
    data = response.json()
    assert (data["score"], data["max_score"], data["percent"]) == (3, 5, 60)
    assert (data["assignment"], data["assignment_title"]) == (assignment.pk, "Quiz")
    assert data["classroom"] == assignment.classroom.pk
    assert [
        (r["question"], r["your_answer"], r["is_correct"], r["points_awarded"], r["points"])
        for r in data["results"]
    ] == [(multiple_choice.pk, "3", False, 0, 2), (fill_in.pk, "улаанбаатар", True, 3, 3)]


def test_results_never_reveal_the_correct_answers(student_api, assignment, questions):
    multiple_choice, fill_in = questions

    response = submit(
        student_api,
        assignment,
        [
            {"question": multiple_choice.pk, "choice": choice(multiple_choice, "3").pk},
            {"question": fill_in.pk, "text": "Дархан"},
        ],
    )

    body = response.content.decode()
    assert "Улаанбаатар" not in body  # the fill-in answer
    assert '"4"' not in body  # the correct option
    assert all(set(result) == RESULT_FIELDS for result in response.json()["results"])


def test_unanswered_questions_are_graded_as_wrong(student_api, assignment, questions):
    response = submit(student_api, assignment, [])

    assert response.status_code == 201
    assert response.json()["score"] == 0
    assert [(r["your_answer"], r["is_correct"]) for r in response.json()["results"]] == [
        (None, False),
        (None, False),
    ]
    assert len(questions) == len(response.json()["results"])


@pytest.mark.usefixtures("questions")
def test_second_submission_is_refused_in_mongolian(student_api, assignment):
    submit(student_api, assignment, [])

    response = submit(student_api, assignment, [])

    assert response.status_code == 400
    assert response.json() == {
        "non_field_errors": ["Та энэ даалгаврыг аль хэдийн илгээсэн байна."]
    }
    assert Submission.objects.count() == 1


@pytest.mark.usefixtures("questions")
def test_closed_assignment_is_refused_in_mongolian(student_api, assignment):
    assignment.due_date = timezone.now() - timedelta(minutes=1)
    assignment.save()

    response = submit(student_api, assignment, [])

    assert response.status_code == 400
    assert response.json() == {"non_field_errors": ["Даалгаврын хугацаа дууссан байна."]}


def test_assignment_without_questions_is_refused_in_mongolian(student_api, assignment):
    response = submit(student_api, assignment, [])

    assert response.status_code == 400
    assert response.json() == {"non_field_errors": ["Энэ даалгаварт асуулт алга байна."]}


@pytest.mark.usefixtures("questions")
def test_answer_to_a_question_of_another_assignment_is_refused(teacher, student_api, assignment):
    other = Assignment.objects.create(
        classroom=assignment.classroom, title="Other", due_date=assignment.due_date
    )
    other_question, _ = add_questions(teacher, other)

    response = submit(student_api, assignment, [{"question": other_question.pk, "text": "x"}])

    assert response.status_code == 400
    assert response.json() == {"answers": ["Асуулт энэ даалгаварт хамаарахгүй."]}


@pytest.mark.parametrize(
    "body, errors",
    [
        (
            {},
            {
                "assignment": ["Даалгаврыг сонгоно уу."],
                "answers": ["Хариултуудыг жагсаалтаар илгээнэ үү."],
            },
        ),
        (
            {"assignment": 1, "answers": "abc"},
            {"answers": {"non_field_errors": ["Хариултуудыг жагсаалтаар илгээнэ үү."]}},
        ),
        (
            {"assignment": 1, "answers": [{"question": 5}, {"question": 5}]},
            {"answers": ["Нэг асуултад нэг л хариулт илгээнэ үү."]},
        ),
        (
            {"assignment": 1, "answers": ["abc"]},
            {"answers": {"0": {"non_field_errors": ["Хариулт буруу байна."]}}},
        ),
    ],
)
def test_invalid_submissions_are_rejected_in_mongolian(student_api, body, errors):
    response = student_api.post(SUBMISSIONS_URL, body, format="json")

    assert response.status_code == 400
    assert response.json() == errors


@pytest.mark.usefixtures("questions")
def test_student_outside_the_class_gets_404(assignment):
    outsider = logged_in_client(make_user("outsider@example.com", User.Role.STUDENT))

    response = submit(outsider, assignment, [])

    assert response.status_code == 404
    assert response.json() == {"detail": "Даалгавар олдсонгүй."}


@pytest.mark.usefixtures("questions")
def test_teacher_cannot_submit_and_login_is_required(teacher_api, assignment):
    assert submit(teacher_api, assignment, []).status_code == 403
    assert submit(APIClient(), assignment, []).status_code == 401
    assert not Submission.objects.exists()


# --- GET /api/submissions/<id>/ --------------------------------------------------------


@pytest.mark.usefixtures("questions")
def test_students_open_only_their_own_result(student_api, teacher_api, classroom, assignment):
    submission_id = submit(student_api, assignment, []).json()["id"]
    url = f"{SUBMISSIONS_URL}{submission_id}/"

    own = student_api.get(url)
    assert own.status_code == 200
    assert (own.json()["id"], len(own.json()["results"])) == (submission_id, 2)

    classmate = classmate_api(classroom).get(url)
    assert classmate.status_code == 404
    assert classmate.json() == {"detail": "Илгээлт олдсонгүй."}
    assert teacher_api.get(url).status_code == 403


# --- The student's result on the assignment (GET /api/assignments/...) ----------------


@pytest.mark.usefixtures("questions")
def test_assignment_shows_only_the_requesting_students_result(
    student_api, teacher_api, classroom, assignment
):
    list_url = f"/api/assignments/?classroom={classroom.pk}"
    detail_url = f"/api/assignments/{assignment.pk}/"
    assert student_api.get(list_url).json()[0]["submission"] is None

    submission_id = submit(student_api, assignment, []).json()["id"]

    expected = {"id": submission_id, "score": 0, "max_score": 5, "percent": 0}
    assert student_api.get(list_url).json()[0]["submission"] == expected
    assert student_api.get(detail_url).json()["submission"] == expected
    assert classmate_api(classroom).get(list_url).json()[0]["submission"] is None
    assert teacher_api.get(list_url).json()[0]["submission"] is None


def test_questions_cannot_change_after_a_submission(
    student_api, teacher_api, assignment, questions
):
    multiple_choice, _ = questions
    submit(student_api, assignment, [])
    locked = {"non_field_errors": ["Илгээлт хийгдсэн тул асуултыг өөрчлөх боломжгүй."]}

    added = teacher_api.post(
        f"/api/assignments/{assignment.pk}/questions/",
        {"kind": "fill_in", "text": "New?", "correct_answer": "Yes"},
        format="json",
    )
    deleted = teacher_api.delete(
        f"/api/assignments/{assignment.pk}/questions/{multiple_choice.pk}/"
    )

    assert (added.status_code, added.json()) == (400, locked)
    assert (deleted.status_code, deleted.json()) == (400, locked)
