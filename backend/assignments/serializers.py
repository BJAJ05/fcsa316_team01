"""Input validation and response representation for assignment endpoints (US-05)."""

from django.utils import timezone
from rest_framework import serializers

from .models import Assignment

CLASSROOM_MISSING_MESSAGE = "Ангийг сонгоно уу."
DUE_DATE_IN_PAST_MESSAGE = "Дуусах хугацаа ирээдүйд байх ёстой."

CLASSROOM_ERRORS = {
    "required": CLASSROOM_MISSING_MESSAGE,
    "null": CLASSROOM_MISSING_MESSAGE,
    "invalid": CLASSROOM_MISSING_MESSAGE,
}
TITLE_ERRORS = {
    "required": "Даалгаврын нэрийг оруулна уу.",
    "blank": "Даалгаврын нэрийг оруулна уу.",
    "null": "Даалгаврын нэрийг оруулна уу.",
    "invalid": "Даалгаврын нэр буруу байна.",
    "max_length": "Даалгаврын нэр {max_length} тэмдэгтээс урт байж болохгүй.",
}
INSTRUCTIONS_ERRORS = {
    "null": "Заавар буруу байна.",
    "invalid": "Заавар буруу байна.",
}
DUE_DATE_ERRORS = {
    "required": "Дуусах хугацааг оруулна уу.",
    "null": "Дуусах хугацааг оруулна уу.",
    "invalid": "Дуусах хугацаа буруу байна.",
    "date": "Дуусах хугацаа буруу байна.",
    "make_aware": "Дуусах хугацаа буруу байна.",
    "overflow": "Дуусах хугацаа буруу байна.",
}


# Input-only serializers: they validate data and never save it themselves
# (services.py does), so DRF's abstract create()/update() are intentionally not implemented.
class ClassroomQuerySerializer(serializers.Serializer):  # pylint: disable=abstract-method
    """Validate `?classroom=<id>` when listing a class's assignments."""

    classroom = serializers.IntegerField(error_messages=CLASSROOM_ERRORS)


class AssignmentInputSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    """Validate a new assignment (POST) or the changed fields of one (PATCH, partial=True)."""

    classroom = serializers.IntegerField(error_messages=CLASSROOM_ERRORS)
    title = serializers.CharField(max_length=200, error_messages=TITLE_ERRORS)
    instructions = serializers.CharField(
        required=False, allow_blank=True, default="", error_messages=INSTRUCTIONS_ERRORS
    )
    due_date = serializers.DateTimeField(error_messages=DUE_DATE_ERRORS)

    def validate_due_date(self, value):
        """A new or changed due date must be in the future."""
        if value <= timezone.now():
            raise serializers.ValidationError(DUE_DATE_IN_PAST_MESSAGE)
        return value


class AssignmentSerializer(serializers.ModelSerializer):
    """An assignment as teachers and students see it."""

    is_open = serializers.BooleanField(read_only=True)

    class Meta:
        model = Assignment
        fields = ("id", "classroom", "title", "instructions", "due_date", "is_open", "created_at")
        read_only_fields = fields
