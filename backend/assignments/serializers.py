"""Input validation and response representation for assignment endpoints (US-05, US-06)."""

from django.utils import timezone
from rest_framework import serializers

from .models import Assignment, Choice, Question

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
    question_count = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = (
            "id",
            "classroom",
            "title",
            "instructions",
            "due_date",
            "is_open",
            "question_count",
            "created_at",
        )
        read_only_fields = fields

    def get_question_count(self, obj):
        """Counted by the services' query; counted here for a just-created assignment."""
        counted = getattr(obj, "question_count", None)
        if counted is None:
            counted = Question.objects.filter(assignment=obj).count()
        return counted


# --- Questions (US-06) -------------------------------------------------------------------

MIN_CHOICES = 2
MAX_CHOICES = 6
KIND_MESSAGE = "Асуултын төрлийг сонгоно уу."
TEXT_MESSAGE = "Асуултын текстийг оруулна уу."
POINTS_MESSAGE = "Оноо 1-ээс бага байж болохгүй."

KIND_ERRORS = {
    "required": KIND_MESSAGE,
    "null": KIND_MESSAGE,
    "blank": KIND_MESSAGE,
    "invalid_choice": KIND_MESSAGE,
}
TEXT_ERRORS = {
    "required": TEXT_MESSAGE,
    "null": TEXT_MESSAGE,
    "blank": TEXT_MESSAGE,
    "invalid": TEXT_MESSAGE,
}
POINTS_ERRORS = {
    "invalid": "Оноо бүхэл тоо байх ёстой.",
    "null": "Оноо бүхэл тоо байх ёстой.",
    "min_value": POINTS_MESSAGE,
    "max_value": "Оноо {max_value}-аас их байж болохгүй.",
}
CHOICE_TEXT_ERRORS = {
    "null": "Сонголтын текст буруу байна.",
    "invalid": "Сонголтын текст буруу байна.",
    "max_length": "Сонголт {max_length} тэмдэгтээс урт байж болохгүй.",
}
CHOICES_ERRORS = {
    "not_a_list": "Сонголтуудыг жагсаалтаар илгээнэ үү.",
    "null": "Сонголтуудыг жагсаалтаар илгээнэ үү.",
}
CORRECT_ANSWER_ERRORS = {
    "null": "Зөв хариултыг оруулна уу.",
    "invalid": "Зөв хариултыг оруулна уу.",
    "max_length": "Зөв хариулт {max_length} тэмдэгтээс урт байж болохгүй.",
}


class ChoiceInputSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    """One option of a new multiple-choice question; empty options are dropped later."""

    text = serializers.CharField(
        max_length=255, allow_blank=True, error_messages=CHOICE_TEXT_ERRORS
    )
    is_correct = serializers.BooleanField(default=False)


class QuestionInputSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    """
    Validate a new question (US-06). Multiple choice needs 2–6 non-empty options with exactly
    one correct; fill-in needs a correct answer.
    """

    kind = serializers.ChoiceField(choices=Question.Kind.choices, error_messages=KIND_ERRORS)
    text = serializers.CharField(error_messages=TEXT_ERRORS)
    points = serializers.IntegerField(
        min_value=1, max_value=100, default=1, error_messages=POINTS_ERRORS
    )
    choices = ChoiceInputSerializer(many=True, required=False, error_messages=CHOICES_ERRORS)
    correct_answer = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        default="",
        error_messages=CORRECT_ANSWER_ERRORS,
    )

    def validate(self, attrs):
        if attrs["kind"] == Question.Kind.MULTIPLE_CHOICE:
            choices = [
                {"text": choice["text"].strip(), "is_correct": choice["is_correct"]}
                for choice in attrs.get("choices", [])
                if choice["text"].strip()
            ]
            correct = sum(1 for choice in choices if choice["is_correct"])
            if len(choices) < MIN_CHOICES:
                message = f"Хамгийн багадаа {MIN_CHOICES} сонголт оруулна уу."
            elif len(choices) > MAX_CHOICES:
                message = f"Хамгийн ихдээ {MAX_CHOICES} сонголт оруулна уу."
            elif correct == 0:
                message = "Зөв хариултыг сонгоно уу."
            elif correct > 1:
                message = "Зөвхөн нэг зөв хариулт сонгоно уу."
            else:
                return {**attrs, "choices": choices, "correct_answer": ""}
            raise serializers.ValidationError({"choices": [message]})

        correct_answer = attrs["correct_answer"].strip()
        if not correct_answer:
            raise serializers.ValidationError({"correct_answer": ["Зөв хариултыг оруулна уу."]})
        return {**attrs, "choices": [], "correct_answer": correct_answer}


class TeacherChoiceSerializer(serializers.ModelSerializer):
    """An option as the teacher sees it, with whether it is the correct one."""

    class Meta:
        model = Choice
        fields = ("id", "text", "is_correct")
        read_only_fields = fields


class StudentChoiceSerializer(serializers.ModelSerializer):
    """An option as a student sees it: never says whether it is correct."""

    class Meta:
        model = Choice
        fields = ("id", "text")
        read_only_fields = fields


class TeacherQuestionSerializer(serializers.ModelSerializer):
    """A question with its correct answer, for the assignment's teacher."""

    choices = TeacherChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ("id", "kind", "text", "points", "position", "correct_answer", "choices")
        read_only_fields = fields


class StudentQuestionSerializer(serializers.ModelSerializer):
    """A question without its correct answer, for students (US-06, US-07)."""

    choices = StudentChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ("id", "kind", "text", "points", "choices")
        read_only_fields = fields
