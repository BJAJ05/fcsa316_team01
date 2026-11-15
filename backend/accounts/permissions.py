"""
Role-based permissions (US-01). Use them in views of other apps, e.g.

    from accounts.permissions import IsTeacher

    class CreateClassView(APIView):
        permission_classes = [IsTeacher]
"""

from rest_framework.permissions import BasePermission


class IsTeacher(BasePermission):
    message = "Энэ үйлдлийг зөвхөн багш хийх боломжтой."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.is_teacher)


class IsStudent(BasePermission):
    message = "Энэ үйлдлийг зөвхөн сурагч хийх боломжтой."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.is_student)
