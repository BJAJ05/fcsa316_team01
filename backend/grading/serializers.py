"""Input validation and response representation for submission endpoints (US-07)."""

from rest_framework import serializers

from .models import Answer, Submission

ASSIGNMENT_MESSAGE = "Даалгаврыг сонгоно уу."
QUESTION_MESSAGE = "Асуултыг сонгоно уу."
ANSWER_TEXT_MESSAGE = "Хариулт буруу байна."
ANSWERS_LIST_MESSAGE = "Хариултуудыг жагсаалтаар илгээнэ үү."
DUPLICATE_ANSWER_MESSAGE = "Нэг асуултад нэг л хариулт илгээнэ үү."


# Input-only serializers: they validate data and never save it themselves
# (services.py does), so DRF's abstract create()/update() are intentionally not implemented.
class AnswerInputSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    """One answer: the question, and the chosen option (multiple choice) or the typed text."""

    # Sent when an answer is not an object (DRF's default message is English).
    default_error_messages = {"invalid": "Хариулт буруу байна."}

    question = serializers.IntegerField(
        error_messages={
            "required": QUESTION_MESSAGE,
            "null": QUESTION_MESSAGE,
            "invalid": QUESTION_MESSAGE,
        }
    )
    choice = serializers.IntegerField(
        required=False,
        allow_null=True,
        default=None,
        error_messages={"invalid": "Сонголт буруу байна."},
    )
    text = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
        max_length=255,
        error_messages={
            "null": ANSWER_TEXT_MESSAGE,
            "invalid": ANSWER_TEXT_MESSAGE,
            "max_length": "Хариулт {max_length} тэмдэгтээс урт байж болохгүй.",
        },
    )


class SubmissionInputSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    """A submission: the assignment and the answers (unanswered questions may be left out)."""

    assignment = serializers.IntegerField(
        error_messages={
            "required": ASSIGNMENT_MESSAGE,
            "null": ASSIGNMENT_MESSAGE,
            "invalid": ASSIGNMENT_MESSAGE,
        }
    )
    # The dict is written here so the type checker infers it as DRF's error_messages type.
    answers = AnswerInputSerializer(
        many=True,
        error_messages={
            "required": ANSWERS_LIST_MESSAGE,
            "null": ANSWERS_LIST_MESSAGE,
            "not_a_list": ANSWERS_LIST_MESSAGE,
        },
    )

    def validate_answers(self, value):
        """At most one answer per question."""
        question_ids = [answer["question"] for answer in value]
        if len(question_ids) != len(set(question_ids)):
            raise serializers.ValidationError(DUPLICATE_ANSWER_MESSAGE)
        return value


class SubmissionSerializer(serializers.ModelSerializer):
    """A graded submission: the score, and where it belongs (assignment, class)."""

    assignment_title = serializers.CharField(source="assignment.title", read_only=True)
    classroom = serializers.IntegerField(source="assignment.classroom_id", read_only=True)
    percent = serializers.IntegerField(read_only=True)

    class Meta:
        model = Submission
        fields = (
            "id",
            "assignment",
            "assignment_title",
            "classroom",
            "score",
            "max_score",
            "percent",
            "submitted_at",
        )
        read_only_fields = fields


class AnswerResultSerializer(serializers.ModelSerializer):
    """
    One question's result: the student's own answer and whether it was right. The correct
    answer is never included (classmates could share it before the due date).
    """

    question = serializers.IntegerField(source="question.pk", read_only=True)
    text = serializers.CharField(source="question.text", read_only=True)
    kind = serializers.CharField(source="question.kind", read_only=True)
    points = serializers.IntegerField(source="question.points", read_only=True)
    your_answer = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = (
            "question",
            "text",
            "kind",
            "your_answer",
            "is_correct",
            "points_awarded",
            "points",
        )
        read_only_fields = fields

    def get_your_answer(self, obj):
        """The chosen option's text, the typed text, or None if the question was not answered."""
        if obj.choice is not None:
            return obj.choice.text
        return obj.text or None
