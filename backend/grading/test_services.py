"""Tests for submitting and grading assignments (grading/services.py, US-07)."""

from datetime import timedelta
from unittest.mock import patch

import pytest
from django.db import IntegrityError
from django.utils import timezone

from accounts.models import User
from assignments import services as assignment_services
from assignments.models import Assignment, Question
from conftest import make_user
from grading.conftest import add_questions, choice
from grading import services
from grading.models import Answer, Submission

pytestmark = pytest.mark.django_db


def test_submit_grades_and_saves_an_answer_for_every_question(student, assignment, questions):
    multiple_choice, fill_in = questions

    submission = services.submit_assignment(
        student,
        assignment.pk,
        [{"question": fill_in.pk, "choice": None, "text": " улаанбаатар "}],
    )

    assert (submission.score, submission.max_score, submission.percent) == (3, 5, 60)
    answers = {answer.question: answer for answer in Answer.objects.filter(submission=submission)}
    assert set(answers) == {multiple_choice, fill_in}  # the unanswered question is saved too
    assert (answers[multiple_choice].is_correct, answers[multiple_choice].choice) == (False, None)
    assert (answers[fill_in].is_correct, answers[fill_in].points_awarded) == (True, 3)


def test_correct_option_is_saved_with_the_answer(student, assignment, questions):
    multiple_choice, _ = questions
    right = choice(multiple_choice, "4")

    submission = services.submit_assignment(
        student, assignment.pk, [{"question": multiple_choice.pk, "choice": right.pk, "text": ""}]
    )

    answer = Answer.objects.get(submission=submission, question=multiple_choice)
    assert (answer.choice, answer.is_correct, submission.score) == (right, True, 2)


def test_option_of_another_question_is_wrong_and_not_saved(teacher, student, assignment, questions):
    multiple_choice, _ = questions
    other_assignment = Assignment.objects.create(
        classroom=assignment.classroom, title="Other", due_date=assignment.due_date
    )
    other_question, _ = add_questions(teacher, other_assignment)
    foreign_option = choice(other_question, "4")

    submission = services.submit_assignment(
        student,
        assignment.pk,
        [{"question": multiple_choice.pk, "choice": foreign_option.pk, "text": ""}],
    )

    answer = Answer.objects.get(submission=submission, question=multiple_choice)
    assert (answer.choice, answer.is_correct, submission.score) == (None, False, 0)


@pytest.mark.usefixtures("questions")
def test_second_submission_is_refused(student, assignment):
    services.submit_assignment(student, assignment.pk, [])

    with pytest.raises(services.AlreadySubmitted):
        services.submit_assignment(student, assignment.pk, [])

    assert Submission.objects.count() == 1


@pytest.mark.usefixtures("questions")
def test_submit_at_the_same_moment_is_reported_as_already_submitted(student, assignment):
    # Both requests pass the "already submitted?" check; the unique constraint rejects the second.
    database_rejects_insert = IntegrityError("duplicate key value violates unique constraint")

    with patch(
        "grading.services.Submission.objects.create", side_effect=database_rejects_insert
    ):
        with pytest.raises(services.AlreadySubmitted):
            services.submit_assignment(student, assignment.pk, [])

    assert not Answer.objects.exists()


@pytest.mark.usefixtures("questions")
def test_closed_assignment_cannot_be_submitted(student, assignment):
    assignment.due_date = timezone.now() - timedelta(minutes=1)
    assignment.save()

    with pytest.raises(services.AssignmentClosed):
        services.submit_assignment(student, assignment.pk, [])

    assert not Submission.objects.exists()


def test_assignment_without_questions_cannot_be_submitted(student, assignment):
    with pytest.raises(services.EmptyAssignment):
        services.submit_assignment(student, assignment.pk, [])


@pytest.mark.usefixtures("questions")
def test_answer_to_a_question_of_another_assignment_is_refused(teacher, student, assignment):
    other_assignment = Assignment.objects.create(
        classroom=assignment.classroom, title="Other", due_date=assignment.due_date
    )
    other_question, _ = add_questions(teacher, other_assignment)

    with pytest.raises(services.InvalidAnswer):
        services.submit_assignment(
            student, assignment.pk, [{"question": other_question.pk, "choice": None, "text": ""}]
        )

    assert not Submission.objects.exists()


@pytest.mark.usefixtures("questions")
def test_student_outside_the_class_cannot_submit(assignment):
    outsider = make_user("outsider@example.com", User.Role.STUDENT)

    with pytest.raises(assignment_services.AssignmentNotFound):
        services.submit_assignment(outsider, assignment.pk, [])



@pytest.mark.usefixtures("questions")
def test_students_only_get_their_own_submissions(student, assignment):
    submission = services.submit_assignment(student, assignment.pk, [])
    classmate = make_user("classmate@example.com", User.Role.STUDENT)

    assert services.get_submission(student, submission.pk) == submission
    with pytest.raises(services.SubmissionNotFound):
        services.get_submission(classmate, submission.pk)


def test_questions_are_locked_once_the_assignment_has_a_submission(
    teacher, student, assignment, questions
):
    multiple_choice, _ = questions
    services.submit_assignment(student, assignment.pk, [])

    with pytest.raises(assignment_services.QuestionsLocked):
        add_questions(teacher, assignment)
    with pytest.raises(assignment_services.QuestionsLocked):
        assignment_services.delete_question(teacher, assignment.pk, multiple_choice.pk)

    assert Question.objects.filter(assignment=assignment).count() == 2


@pytest.mark.usefixtures("questions")
def test_submissions_by_assignment_is_for_students_only(teacher, student, assignment):
    submission = services.submit_assignment(student, assignment.pk, [])

    assert services.submissions_by_assignment(student, [assignment]) == {assignment.pk: submission}
    assert services.submissions_by_assignment(teacher, [assignment]) == {}
