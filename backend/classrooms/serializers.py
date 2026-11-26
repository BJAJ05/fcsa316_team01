"""Input validation and response representation for classroom endpoints."""

from rest_framework import serializers

from .models import Classroom, Enrollment

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
CODE_ERRORS = {
    "required": "Ангийн кодыг оруулна уу.",
    "blank": "Ангийн кодыг оруулна уу.",
    "null": "Ангийн кодыг оруулна уу.",
    "invalid": "Ангийн код буруу байна.",
}


# Input-only serializer: it validates data and never saves it itself
# (services.py does), so DRF's abstract create()/update() are intentionally not implemented.
class CreateClassSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    """Validate the name and subject supplied when a teacher creates a class."""

    name = serializers.CharField(max_length=100, error_messages=NAME_ERRORS)
    subject = serializers.CharField(max_length=100, error_messages=SUBJECT_ERRORS)


class JoinClassSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    """Validate the class code a student types to join a class (US-03)."""

    # Spaces around the code are removed here; services.join_class() also uppercases it.
    code = serializers.CharField(error_messages=CODE_ERRORS)


class EnrolledStudentSerializer(serializers.ModelSerializer):
    """One row of a class roster (US-04): the student's id and email, and when they joined."""

    id = serializers.IntegerField(source="student.pk", read_only=True)
    email = serializers.EmailField(source="student.email", read_only=True)

    class Meta:
        model = Enrollment
        fields = ("id", "email", "joined_at")
        read_only_fields = fields


class ClassroomSerializer(serializers.ModelSerializer):
    """A class as its teacher and its students see it, including the join code."""

    teacher_email = serializers.EmailField(source="teacher.email", read_only=True)
    student_count = serializers.IntegerField(source="enrollments.count", read_only=True)

    class Meta:
        model = Classroom
        fields = ("id", "name", "subject", "code", "teacher_email", "student_count", "created_at")
        read_only_fields = fields
