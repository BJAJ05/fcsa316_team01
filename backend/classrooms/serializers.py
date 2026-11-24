"""Input validation and response representation for classroom endpoints."""

from rest_framework import serializers

from .models import Classroom

NAME_ERRORS = {
    "required": "Ангийн нэрээ оруулна уу.",
    "blank": "Ангийн нэрээ оруулна уу.",
    "null": "Ангийн нэрээ оруулна уу.",
    "invalid": "Ангийн нэр буруу байна.",
    "max_length": "Ангийн нэр {max_length} тэмдэгтээс урт байж болохгүй.",
}
SUBJECT_ERRORS = {
    "required": "Хичээлийн нэрээ оруулна уу.",
    "blank": "Хичээлийн нэрээ оруулна уу.",
    "null": "Хичээлийн нэрээ оруулна уу.",
    "invalid": "Хичээлийн нэр буруу байна.",
    "max_length": "Хичээлийн нэр {max_length} тэмдэгтээс урт байж болохгүй.",
}


# Input-only serializer: it validates data and never saves it itself
# (services.py does), so DRF's abstract create()/update() are intentionally not implemented.
class CreateClassSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    """Validate the name and subject supplied when a teacher creates a class."""

    name = serializers.CharField(max_length=100, error_messages=NAME_ERRORS)
    subject = serializers.CharField(max_length=100, error_messages=SUBJECT_ERRORS)


class ClassroomSerializer(serializers.ModelSerializer):
    """Class details returned to its teacher, including the student join code."""

    class Meta:
        model = Classroom
        fields = ("id", "name", "subject", "code", "created_at")
        read_only_fields = fields
