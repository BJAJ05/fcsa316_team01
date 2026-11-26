"""
Presentation / API layer for `assignments` (US-05).

Views check permissions, validate input with serializers and call functions in
`services.py`. Keep business logic out of views.
"""

from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsTeacher
from classrooms.services import ClassNotFound

from . import services
from .serializers import AssignmentInputSerializer, AssignmentSerializer, ClassroomQuerySerializer

CLASS_NOT_FOUND_MESSAGE = "Анги олдсонгүй."
ASSIGNMENT_NOT_FOUND_MESSAGE = "Даалгавар олдсонгүй."
# Fields a teacher may change with PATCH; the class of an assignment stays the same.
EDITABLE_FIELDS = ("title", "instructions", "due_date")


class AssignmentListCreateView(APIView):
    """
    GET /api/assignments/?classroom=<id> → assignments of a class the user teaches or joined.
    POST /api/assignments/               → a teacher creates an assignment in their class.
    """

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsTeacher()]
        return super().get_permissions()  # any logged-in user

    def get(self, request):
        """List the class's assignments, earliest due date first."""
        query = ClassroomQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        try:
            assignments = services.list_assignments(
                request.user, query.validated_data["classroom"]
            )
        except ClassNotFound as exc:
            raise NotFound(CLASS_NOT_FOUND_MESSAGE) from exc
        return Response(AssignmentSerializer(assignments, many=True).data)

    def post(self, request):
        """Create an assignment in one of the teacher's own classes."""
        serializer = AssignmentInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            assignment = services.create_assignment(
                request.user,
                data["classroom"],
                data["title"],
                data["instructions"],
                data["due_date"],
            )
        except ClassNotFound as exc:
            raise NotFound(CLASS_NOT_FOUND_MESSAGE) from exc
        return Response(AssignmentSerializer(assignment).data, status=status.HTTP_201_CREATED)


class AssignmentDetailView(APIView):
    """
    GET    /api/assignments/<id>/ → one assignment (its teacher, or an enrolled student).
    PATCH  /api/assignments/<id>/ → its teacher changes title, instructions or due date.
    DELETE /api/assignments/<id>/ → its teacher deletes it.
    """

    def get_permissions(self):
        if self.request.method in ("PATCH", "DELETE"):
            return [IsTeacher()]
        return super().get_permissions()  # any logged-in user

    def get(self, request, assignment_id):
        """Return the assignment if the user may see it."""
        try:
            assignment = services.get_assignment(request.user, assignment_id)
        except services.AssignmentNotFound as exc:
            raise NotFound(ASSIGNMENT_NOT_FOUND_MESSAGE) from exc
        return Response(AssignmentSerializer(assignment).data)

    def patch(self, request, assignment_id):
        """Change the given fields of the teacher's own assignment."""
        serializer = AssignmentInputSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        fields = {
            name: value
            for name, value in serializer.validated_data.items()
            if name in EDITABLE_FIELDS and name in request.data
        }
        try:
            assignment = services.update_assignment(request.user, assignment_id, **fields)
        except services.AssignmentNotFound as exc:
            raise NotFound(ASSIGNMENT_NOT_FOUND_MESSAGE) from exc
        return Response(AssignmentSerializer(assignment).data)

    def delete(self, request, assignment_id):
        """Delete the teacher's own assignment."""
        try:
            services.delete_assignment(request.user, assignment_id)
        except services.AssignmentNotFound as exc:
            raise NotFound(ASSIGNMENT_NOT_FOUND_MESSAGE) from exc
        return Response(status=status.HTTP_204_NO_CONTENT)
