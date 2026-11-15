"""
Business layer for `accounts` (AuthService in the architecture diagram).

Users, registration, login and JWT tokens (US-01).
Plain functions so they can be unit tested without HTTP. Views call these
functions; these functions use the models.
"""

from django.contrib.auth import authenticate, get_user_model
from django.db import IntegrityError, transaction
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class EmailAlreadyRegistered(Exception):
    """Someone tried to register with an email that already has an account."""


class InvalidCredentials(Exception):
    """The email/password pair does not match an active account."""


def register_user(email, password, role):
    """Create a teacher or student account. Raises EmailAlreadyRegistered."""
    email = User.objects.normalize_email(email)
    if User.objects.filter(email__iexact=email).exists():
        raise EmailAlreadyRegistered(email)
    try:
        with transaction.atomic():
            return User.objects.create_user(email=email, password=password, role=role)
    except IntegrityError as error:
        # Two sign-ups with the same email at the same moment: the unique constraint decides.
        raise EmailAlreadyRegistered(email) from error


def login_user(email, password):
    """Return the user for a correct email/password pair. Raises InvalidCredentials."""
    user = authenticate(email=email, password=password)
    if user is None:
        raise InvalidCredentials()
    return user


def issue_tokens(user):
    """
    JWT pair for `user`. The tokens carry the user's role and email, so the frontend
    can show the right dashboard. (Permission checks on the server use the database,
    not these claims.)
    """
    refresh = RefreshToken.for_user(user)
    refresh["role"] = user.role
    refresh["email"] = user.email
    # The access token (and every access token refreshed later) copies these claims.
    return {"refresh": str(refresh), "access": str(refresh.access_token)}
