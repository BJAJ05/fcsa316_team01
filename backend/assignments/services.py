"""
Business layer for `assignments` (AssignmentService in the architecture diagram).

US-05: teachers create, change and delete assignments in their own classes; teachers and
enrolled students list and open them. Access goes through classrooms.services, so a user
only ever reaches assignments of classes they teach or have joined.
US-06: teachers add multiple-choice and fill-in questions to their own assignments.
US-07: once a student has submitted an assignment, its questions can no longer change.
"""

from django.db import transaction
from django.db.models import Count

from classrooms.services import get_class, list_classes

from .models import Assignment, Choice, Question


class AssignmentNotFound(Exception):
    """No assignment with that id, or one in a class the user may not see."""


class QuestionNotFound(Exception):
    """No question with that id in the given assignment."""


class QuestionsLocked(Exception):
    """The assignment already has submissions, so its questions can no longer change (US-07)."""


def _ensure_questions_can_change(assignment):
    """Graded submissions must keep matching the questions they were graded against."""
    if Assignment.objects.filter(pk=assignment.pk, submissions__isnull=False).exists():
        raise QuestionsLocked(assignment.pk)


def _with_question_count(assignments):
    """Add `question_count` to each assignment of the QuerySet (one query, US-06)."""
    # Django ignores Meta.ordering in GROUP BY queries such as this one, so order again.
    return assignments.annotate(question_count=Count("questions")).order_by("due_date", "pk")


def list_assignments(user, class_id):
    """Assignments of one class the user may see, earliest due date first."""
    classroom = get_class(user, class_id)  # raises ClassNotFound
    return _with_question_count(Assignment.objects.filter(classroom=classroom))


def get_assignment(user, assignment_id):
    """
    One assignment in a class the user teaches or has joined. Raises AssignmentNotFound for
    any other assignment, so the API answers 404 without revealing that it exists.
    """
    try:
        return _with_question_count(Assignment.objects.select_related("classroom")).get(
            pk=assignment_id, classroom__in=list_classes(user)
        )
    except Assignment.DoesNotExist as error:
        raise AssignmentNotFound(assignment_id) from error


def create_assignment(teacher, class_id, title, instructions, due_date):
    """Create an assignment in one of the teacher's own classes (raises ClassNotFound)."""
    classroom = get_class(teacher, class_id)
    return Assignment.objects.create(
        classroom=classroom, title=title, instructions=instructions, due_date=due_date
    )


def update_assignment(teacher, assignment_id, **fields):
    """Change the title, instructions and/or due date of the teacher's own assignment."""
    assignment = get_assignment(teacher, assignment_id)
    for name, value in fields.items():
        setattr(assignment, name, value)
    if fields:
        assignment.save(update_fields=list(fields))
    return assignment


def delete_assignment(teacher, assignment_id):
    """Delete the teacher's own assignment (raises AssignmentNotFound for any other)."""
    get_assignment(teacher, assignment_id).delete()


def list_questions(assignment):
    """The assignment's questions in order, each with its choices loaded."""
    return Question.objects.filter(assignment=assignment).prefetch_related("choices")


def add_question(teacher, assignment_id, data):
    """
    Add a question to the teacher's own assignment, at the end of its list. `data` is the
    validated question: kind, text, points, correct_answer and (multiple choice) choices.
    Raises QuestionsLocked once the assignment has submissions.
    """
    assignment = get_assignment(teacher, assignment_id)
    _ensure_questions_can_change(assignment)
    with transaction.atomic():
        question = Question.objects.create(
            assignment=assignment,
            kind=data["kind"],
            text=data["text"],
            points=data["points"],
            position=Question.objects.filter(assignment=assignment).count(),
            correct_answer=data["correct_answer"],
        )
        Choice.objects.bulk_create(
            Choice(question=question, text=choice["text"], is_correct=choice["is_correct"])
            for choice in data["choices"]
        )
    return question


def delete_question(teacher, assignment_id, question_id):
    """Delete one question of the teacher's own assignment (QuestionsLocked after submissions)."""
    assignment = get_assignment(teacher, assignment_id)
    _ensure_questions_can_change(assignment)
    deleted, _ = Question.objects.filter(pk=question_id, assignment=assignment).delete()
    if not deleted:
        raise QuestionNotFound(question_id)
