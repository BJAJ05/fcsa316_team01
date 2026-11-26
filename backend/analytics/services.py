"""
Business layer for `analytics` (AnalyticsService in the architecture diagram).

Student progress and teacher class reports (reads data from the other apps).
Put the rules of US-12, US-13 here as plain functions so they can be unit tested
without HTTP. Views call these functions; these functions use the models.
"""

from django.db.models import (
    Avg,
    Case,
    Count,
    F,
    FloatField,
    Q,
    Value,
    When,
)
from django.db.models.expressions import ExpressionWrapper
from django.utils import timezone

from assignments.models import Assignment
from classrooms.services import list_classes
from grading.models import Submission


def student_progress(student):
    """Return assignment completion and average scores for each class the student joined."""
    classrooms = list(list_classes(student))
    if not classrooms:
        return []

    classroom_ids = [classroom.pk for classroom in classrooms]
    stats = (
        Assignment.objects.filter(classroom_id__in=classroom_ids)
        .values("classroom_id")
        .annotate(
            assignment_count=Count("pk", distinct=True),
            submitted_count=Count(
                "submissions__pk",
                filter=Q(submissions__student=student),
                distinct=True,
            ),
            average_percent=Avg(
                Case(
                    When(submissions__max_score=0, then=Value(0.0)),
                    default=ExpressionWrapper(
                        F("submissions__score") * Value(100.0)
                        / F("submissions__max_score"),
                        output_field=FloatField(),
                    ),
                    output_field=FloatField(),
                ),
                filter=Q(submissions__student=student),
            ),
        )
    )
    stats_by_class = {row["classroom_id"]: row for row in stats}

    # The student's percentage per assignment (at most one submission each).
    percent_by_assignment = {
        submission.assignment.pk: submission.percent
        for submission in Submission.objects.filter(
            student=student, assignment__classroom__in=classroom_ids
        ).select_related("assignment")
    }
    # .values() gives plain dicts: the editor's type checker knows their keys, whereas
    # attributes Django adds at runtime (classroom_id, Prefetch to_attr) look unknown to it.
    assignments_by_class = {classroom_id: [] for classroom_id in classroom_ids}
    for row in (
        Assignment.objects.filter(classroom__in=classroom_ids)
        .order_by("due_date", "pk")
        .values("pk", "classroom", "title", "due_date")
    ):
        assignments_by_class[row["classroom"]].append(
            {
                "id": row["pk"],
                "title": row["title"],
                # In the project's time zone (+08:00), like every other API's dates.
                "due_date": timezone.localtime(row["due_date"]),
                "percent": percent_by_assignment.get(row["pk"]),
            }
        )

    progress = []
    for classroom in classrooms:
        class_stats = stats_by_class.get(classroom.pk, {})
        assignment_count = class_stats.get("assignment_count", 0)
        submitted_count = class_stats.get("submitted_count", 0)
        average_percent = class_stats.get("average_percent")
        progress.append(
            {
                "class_id": classroom.pk,
                "class_name": classroom.name,
                "subject": classroom.subject,
                "assignment_count": assignment_count,
                "submitted_count": submitted_count,
                "completion_percent": (
                    round(submitted_count * 100 / assignment_count) if assignment_count else 0
                ),
                "average_percent": (
                    round(average_percent) if average_percent is not None else None
                ),
                "assignments": assignments_by_class[classroom.pk],
            }
        )
    return progress
