"""
Presentation / API layer for `analytics` (US-12, US-13).

Views (DRF APIView/ViewSet) check permissions, validate input with serializers and
call functions in `services.py`. Keep business logic out of views.
"""

from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsStudent

from . import services


class StudentProgressView(APIView):
    """GET /api/analytics/progress/ → progress for the authenticated student's classes."""

    permission_classes = [IsStudent]

    def get(self, request):
        """Return completion rates, average scores, and assignment results."""
        return Response(services.student_progress(request.user))
