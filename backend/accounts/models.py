"""Custom User model: login with email, and a teacher/student role (US-01)."""

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """Creates users identified by email instead of username."""

    use_in_migrations = True

    @classmethod
    def normalize_email(cls, email):
        """Store emails in lowercase so `Bat@Mail.com` and `bat@mail.com` are the same account."""
        return super().normalize_email(email).strip().lower()

    def get_by_natural_key(self, username):
        """Used by authenticate(): `username` is the email (USERNAME_FIELD); case-insensitive."""
        return self.get(email__iexact=username)

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("An email address is required.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create a normal (non-admin) user."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """Create an admin user that can log in to /admin/."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Project user model (settings.AUTH_USER_MODEL). Users log in with email + password.

    Always refer to it as `settings.AUTH_USER_MODEL` in ForeignKeys and
    `get_user_model()` in code, never `django.contrib.auth.models.User`.
    Every user is either a teacher or a student (`role`, US-01). Check it with
    `user.is_teacher` / `user.is_student`, or the IsTeacher/IsStudent permissions in API views.
    """

    class Role(models.TextChoices):
        """The two user roles. Stored value in English, label in Mongolian."""

        TEACHER = "teacher", "Багш"
        STUDENT = "student", "Сурагч"

    username = None
    email = models.EmailField("email address", unique=True)
    # Default is the role with fewer rights; registration always sets it explicitly.
    role = models.CharField("role", max_length=16, choices=Role.choices, default=Role.STUDENT)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

    @property
    def is_teacher(self):
        """True if the user registered as a teacher."""
        return self.role == self.Role.TEACHER

    @property
    def is_student(self):
        """True if the user registered as a student."""
        return self.role == self.Role.STUDENT
