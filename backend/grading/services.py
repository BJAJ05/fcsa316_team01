"""
Business layer for `grading` (GradingService in the architecture diagram), US-07.

A student submits answers to an assignment of a class they joined; scoring.grade() grades
them and the result is saved: one Submission per student and assignment, and one Answer for
every question of the assignment (unanswered questions are saved as wrong).
"""

from django.db import IntegrityError, transaction

from assignments.models import Choice, Question
from assignments.services import get_assignment

from .models import Answer, Submission
from .scoring import AnswerKey, grade


class AssignmentClosed(Exception):
    """The assignment's due date has passed."""


class AlreadySubmitted(Exception):
    """The student has already submitted this assignment (one attempt each)."""


class EmptyAssignment(Exception):
    """The assignment has no questions yet."""


class InvalidAnswer(Exception):
    """An answer names a question that is not part of the assignment."""


class SubmissionNotFound(Exception):
    """No submission with that id belongs to this student."""


def build_answer_keys(assignment):
    """The answer key of every question of the assignment, in question order (two queries)."""
    correct_choice_ids = dict(
        Choice.objects.filter(question__assignment=assignment, is_correct=True).values_list(
            "question_id", "pk"
        )
    )
    return [
        AnswerKey(
            question_id=question.pk,
            kind=question.kind,
            points=question.points,
            correct_choice_id=correct_choice_ids.get(question.pk),
            correct_answer=question.correct_answer,
        )
        for question in Question.objects.filter(assignment=assignment)
    ]


def submit_assignment(student, assignment_id, answers):
    """
    Grade and save a student's answers. `answers` is a list of {"question": id, "choice": id
    or None, "text": str} (validated by SubmissionInputSerializer); multiple-choice questions
    use "choice", fill-in questions use "text". Raises AssignmentNotFound (not in a joined
    class), AssignmentClosed, AlreadySubmitted, EmptyAssignment or InvalidAnswer.
    """
    assignment = get_assignment(student, assignment_id)
    if not assignment.is_open:
        raise AssignmentClosed(assignment_id)
    if Submission.objects.filter(assignment=assignment, student=student).exists():
        raise AlreadySubmitted(assignment_id)
    keys = build_answer_keys(assignment)
    if not keys:
        raise EmptyAssignment(assignment_id)

    keys_by_question = {key.question_id: key for key in keys}
    given = {}
    for answer in answers:
        key = keys_by_question.get(answer["question"])
        if key is None:
            raise InvalidAnswer(answer["question"])
        if key.kind == Question.Kind.MULTIPLE_CHOICE:
            given[key.question_id] = answer.get("choice")
        else:
            given[key.question_id] = answer.get("text", "")

    result = grade(keys, given)
    # Only keep a chosen option that belongs to its question (another one is graded as wrong).
    question_of_choice = dict(
        Choice.objects.filter(question__assignment=assignment).values_list("pk", "question_id")
    )
    try:
        with transaction.atomic():
            submission = Submission.objects.create(
                assignment=assignment,
                student=student,
                score=result.score,
                max_score=result.max_score,
            )
            Answer.objects.bulk_create(
                [
                    _answer_row(submission, keys_by_question, given, item, question_of_choice)
                    for item in result.results
                ]
            )
    except IntegrityError as error:
        # Two "submit" clicks at the same moment: the unique constraint lets only one through.
        raise AlreadySubmitted(assignment_id) from error
    return submission


def _answer_row(submission, keys_by_question, given, item, question_of_choice):
    """The Answer to save for one graded question (`item` is its scoring.QuestionResult)."""
    key = keys_by_question[item.question_id]
    answer = given.get(key.question_id)
    if key.kind == Question.Kind.MULTIPLE_CHOICE:
        own_choice = question_of_choice.get(answer) == key.question_id
        return Answer(
            submission=submission,
            question_id=key.question_id,
            choice_id=answer if own_choice else None,
            is_correct=item.is_correct,
            points_awarded=item.points_awarded,
        )
    return Answer(
        submission=submission,
        question_id=key.question_id,
        text=answer or "",
        is_correct=item.is_correct,
        points_awarded=item.points_awarded,
    )


def get_submission(student, submission_id):
    """One of the student's own submissions. Raises SubmissionNotFound for anyone else's."""
    try:
        return Submission.objects.select_related("assignment").get(
            pk=submission_id, student=student
        )
    except Submission.DoesNotExist as error:
        raise SubmissionNotFound(submission_id) from error


def list_answers(submission):
    """The submission's answers in question order, with their questions and chosen options."""
    return (
        Answer.objects.filter(submission=submission)
        .select_related("question", "choice")
        .order_by("question__position", "question__pk")
    )


def submissions_by_assignment(user, assignments):
    """
    {assignment id: the student's Submission} for these assignments, in one query, so the
    assignment list can show "Илгээсэн — 8/10". Teachers have no submissions: {}.
    """
    if not user.is_student:
        return {}
    submissions = Submission.objects.filter(
        student=user, assignment__in=assignments
    ).select_related("assignment")
    return {submission.assignment.pk: submission for submission in submissions}
