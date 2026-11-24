"""
Presentation / API layer for `classrooms` (US-02, US-03, US-04).

Views (DRF APIView/ViewSet) check permissions, validate input with serializers and
call functions in `services.py`. Keep business logic out of views.
"""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsTeacher

from . import services
from .serializers import ClassroomSerializer, CreateClassSerializer


class ClassListCreateView(APIView):
    """GET/POST /api/classes/ — list a teacher's classes or create one."""

    permission_classes = [IsTeacher]

    def get(self, request):
        """Return only the authenticated teacher's classes."""
        classes = services.list_teacher_classes(request.user)
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
