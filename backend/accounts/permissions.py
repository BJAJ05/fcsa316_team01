"""
Role-based permissions (US-01). Use them in views of other apps, e.g.

    from accounts.permissions import IsTeacher

    class CreateClassView(APIView):
        permission_classes = [IsTeacher]
"""

from rest_framework.permissions import BasePermission

from .models import User


# A visitor without a valid token is an AnonymousUser, not a User, so the isinstance()
# checks below refuse them (and tell the editor that `user` has `is_teacher`/`is_student`).
class IsTeacher(BasePermission):
    """Allows the request only for a logged-in teacher."""

    message = "Энэ үйлдлийг зөвхөн багш хийх боломжтой."

    def has_permission(self, request, view):
        user = request.user
        return isinstance(user, User) and user.is_teacher


class IsStudent(BasePermission):
    """Allows the request only for a logged-in student."""

    message = "Энэ үйлдлийг зөвхөн сурагч хийх боломжтой."

    def has_permission(self, request, view):
        user = request.user
        return isinstance(user, User) and user.is_student
