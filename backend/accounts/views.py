"""
Presentation / API layer for `accounts` (US-01).

Views (DRF APIView/ViewSet) check permissions, validate input with serializers and
call functions in `services.py`. Keep business logic out of views.
"""

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenRefreshView

from . import services
from .serializers import LoginSerializer, RegisterSerializer, UserSerializer

EMAIL_TAKEN_MESSAGE = "Энэ имэйл бүртгэлтэй байна."
INVALID_CREDENTIALS_MESSAGE = "Имэйл эсвэл нууц үг буруу байна."


def _auth_response(user, status_code):
    """{user, access, refresh} — the same shape for register and login."""
    return Response({"user": UserSerializer(user).data, **services.issue_tokens(user)}, status=status_code)


class RegisterView(APIView):
    """POST /api/auth/register/  {email, password, role} → 201 {user, access, refresh}"""

    # Public endpoint: no login needed, and a stale token in the header is ignored.
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = services.register_user(**serializer.validated_data)
        except services.EmailAlreadyRegistered:
            raise ValidationError({"email": [EMAIL_TAKEN_MESSAGE]})
        return _auth_response(user, status.HTTP_201_CREATED)


class LoginView(APIView):
    """POST /api/auth/login/  {email, password} → 200 {user, access, refresh} | 401"""

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = services.login_user(**serializer.validated_data)
        except services.InvalidCredentials:
            return Response({"detail": INVALID_CREDENTIALS_MESSAGE}, status=status.HTTP_401_UNAUTHORIZED)
        return _auth_response(user, status.HTTP_200_OK)


class RefreshView(TokenRefreshView):
    """POST /api/auth/refresh/  {refresh} → 200 {access} | 401 when the refresh token expired"""

    authentication_classes = []
    permission_classes = [AllowAny]


class MeView(APIView):
    """GET /api/auth/me/ → the logged-in user {id, email, role} (needs a token)."""

    def get(self, request):
        return Response(UserSerializer(request.user).data)
