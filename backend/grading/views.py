"""
Presentation / API layer for `grading` (US-07).

Views check permissions, validate input with serializers and call functions in
`services.py`. Keep business logic out of views.
"""

from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsStudent
from assignments.services import AssignmentNotFound

from . import services
from .serializers import AnswerResultSerializer, SubmissionInputSerializer, SubmissionSerializer

ASSIGNMENT_NOT_FOUND_MESSAGE = "Даалгавар олдсонгүй."
SUBMISSION_NOT_FOUND_MESSAGE = "Илгээлт олдсонгүй."
ASSIGNMENT_CLOSED_MESSAGE = "Даалгаврын хугацаа дууссан байна."
ALREADY_SUBMITTED_MESSAGE = "Та энэ даалгаврыг аль хэдийн илгээсэн байна."
EMPTY_ASSIGNMENT_MESSAGE = "Энэ даалгаварт асуулт алга байна."
INVALID_ANSWER_MESSAGE = "Асуулт энэ даалгаварт хамаарахгүй."


def _submission_response(submission):
    """The submission with each question's result (never the correct answers)."""
    results = AnswerResultSerializer(services.list_answers(submission), many=True).data
    return {**SubmissionSerializer(submission).data, "results": results}


class SubmissionCreateView(APIView):
    """POST /api/submissions/ {assignment, answers} → a student submits and gets graded."""

    permission_classes = [IsStudent]

    def post(self, request):
        """Grade the answers, save them, and return the score and each question's result."""
        serializer = SubmissionInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            submission = services.submit_assignment(
                request.user, data["assignment"], data["answers"]
            )
        except AssignmentNotFound as exc:
            raise NotFound(ASSIGNMENT_NOT_FOUND_MESSAGE) from exc
        except services.AssignmentClosed as exc:
            raise ValidationError({"non_field_errors": [ASSIGNMENT_CLOSED_MESSAGE]}) from exc
        except services.AlreadySubmitted as exc:
            raise ValidationError({"non_field_errors": [ALREADY_SUBMITTED_MESSAGE]}) from exc
        except services.EmptyAssignment as exc:
            raise ValidationError({"non_field_errors": [EMPTY_ASSIGNMENT_MESSAGE]}) from exc
        except services.InvalidAnswer as exc:
            raise ValidationError({"answers": [INVALID_ANSWER_MESSAGE]}) from exc
        return Response(_submission_response(submission), status=status.HTTP_201_CREATED)


class SubmissionDetailView(APIView):
    """GET /api/submissions/<id>/ → one of the student's own graded submissions."""

    permission_classes = [IsStudent]

    def get(self, request, submission_id):
        """Return the submission if it is the student's own."""
        try:
            submission = services.get_submission(request.user, submission_id)
        except services.SubmissionNotFound as exc:
            raise NotFound(SUBMISSION_NOT_FOUND_MESSAGE) from exc
        return Response(_submission_response(submission))
