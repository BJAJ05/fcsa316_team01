"""Input validation and response representation for classroom endpoints."""

from rest_framework import serializers

from .models import Classroom


class CreateClassSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    """Validate the name and subject supplied when a teacher creates a class."""

    name = serializers.CharField(
        max_length=100,
        trim_whitespace=True,
        error_messages={
            "required": "Ангийн нэрээ оруулна уу.",
            "blank": "Ангийн нэрээ оруулна уу.",
        },
    )
    subject = serializers.CharField(
        max_length=100,
        trim_whitespace=True,
        error_messages={
            "required": "Хичээлийн нэрээ оруулна уу.",
            "blank": "Хичээлийн нэрээ оруулна уу.",
        },
    )


class ClassroomSerializer(serializers.ModelSerializer):
    """Class details returned to its teacher, including the student join code."""

    class Meta:
        model = Classroom
        fields = ("id", "name", "subject", "code", "created_at")
        read_only_fields = fields
