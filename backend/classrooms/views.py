"""
Presentation / API layer for `classrooms` (US-02, US-03, US-04).

Views (DRF APIView/ViewSet) check permissions, validate input with serializers and
call functions in `services.py`. Keep business logic out of views.
"""

from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsStudent, IsTeacher

from . import services
from .serializers import (
    ClassroomSerializer,
    CreateClassSerializer,
    EnrolledStudentSerializer,
    JoinClassSerializer,
)

CLASS_NOT_FOUND_MESSAGE = "Анги олдсонгүй."
CODE_NOT_FOUND_MESSAGE = "Ангийн код олдсонгүй."
ALREADY_ENROLLED_MESSAGE = "Та энэ ангид аль хэдийн элссэн байна."
STUDENT_NOT_ENROLLED_MESSAGE = "Сурагч энэ ангид элсээгүй байна."


class ClassListCreateView(APIView):
    """
    GET /api/classes/  → the user's classes (a teacher's own, or the ones a student joined).
    POST /api/classes/ → a teacher creates a class (US-02).
    """

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsTeacher()]
        return super().get_permissions()  # any logged-in user

    def get(self, request):
        """Return the classes this user teaches or has joined."""
        classes = services.list_classes(request.user)
        return Response(ClassroomSerializer(classes, many=True).data)

    def post(self, request):
        """Create a teacher-owned class and return its generated join code."""
        serializer = CreateClassSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        classroom = services.create_class(request.user, **serializer.validated_data)
        return Response(
            ClassroomSerializer(classroom).data,
            status=status.HTTP_201_CREATED,
        )


class ClassDetailView(APIView):
    """GET /api/classes/<id>/ → one class; 404 unless the user teaches it or has joined it."""

    def get(self, request, class_id):
        """Return the class if this user may see it."""
        try:
            classroom = services.get_class(request.user, class_id)
        except services.ClassNotFound as exc:
            raise NotFound(CLASS_NOT_FOUND_MESSAGE) from exc
        return Response(ClassroomSerializer(classroom).data)


class JoinClassView(APIView):
    """POST /api/classes/join/ {code} → a student joins a class with its code (US-03)."""

    permission_classes = [IsStudent]

    def post(self, request):
        """Enroll the student and return the joined class."""
        serializer = JoinClassSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            classroom = services.join_class(request.user, serializer.validated_data["code"])
        except services.ClassNotFound as exc:
            raise NotFound(CODE_NOT_FOUND_MESSAGE) from exc
        except services.AlreadyEnrolled as exc:
            raise ValidationError({"code": [ALREADY_ENROLLED_MESSAGE]}) from exc
        return Response(ClassroomSerializer(classroom).data, status=status.HTTP_201_CREATED)


class ClassStudentListView(APIView):
    """GET /api/classes/<id>/students/ → the roster of the teacher's own class (US-04)."""

    permission_classes = [IsTeacher]

    def get(self, request, class_id):
        """Return the class's students with the date each one joined."""
        try:
            enrollments = services.list_students(request.user, class_id)
        except services.ClassNotFound as exc:
            raise NotFound(CLASS_NOT_FOUND_MESSAGE) from exc
        return Response(EnrolledStudentSerializer(enrollments, many=True).data)


class ClassStudentDetailView(APIView):
    """DELETE /api/classes/<id>/students/<student_id>/ → the teacher removes a student (US-04)."""

    permission_classes = [IsTeacher]

    def delete(self, request, class_id, student_id):
        """Take the student out of the class."""
        try:
            services.remove_student(request.user, class_id, student_id)
        except services.ClassNotFound as exc:
            raise NotFound(CLASS_NOT_FOUND_MESSAGE) from exc
        except services.StudentNotEnrolled as exc:
            raise NotFound(STUDENT_NOT_ENROLLED_MESSAGE) from exc
        return Response(status=status.HTTP_204_NO_CONTENT)
