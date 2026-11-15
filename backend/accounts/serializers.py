"""Presentation layer for `accounts`: input validation and response shapes (US-01)."""

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

User = get_user_model()

EMAIL_ERRORS = {
    "required": "Имэйлээ оруулна уу.",
    "blank": "Имэйлээ оруулна уу.",
    "invalid": "Имэйл хаяг буруу байна.",
}
PASSWORD_ERRORS = {
    "required": "Нууц үгээ оруулна уу.",
    "blank": "Нууц үгээ оруулна уу.",
}

# Django's password validators (settings.AUTH_PASSWORD_VALIDATORS) speak English;
# show their errors in Mongolian, keyed by the validator's error code.
PASSWORD_RULE_MESSAGES = {
    "password_too_short": "Нууц үг хэтэрхий богино байна. Хамгийн багадаа {min_length} тэмдэгт оруулна уу.",
    "password_too_common": "Энэ нууц үг хэтэрхий түгээмэл байна.",
    "password_entirely_numeric": "Нууц үг зөвхөн тооноос бүрдэж болохгүй.",
    "password_too_similar": "Нууц үг имэйл хаягтай хэт төстэй байна.",
}


def _password_messages(error):
    messages = []
    for item in error.error_list:
        template = PASSWORD_RULE_MESSAGES.get(item.code)
        messages.append(template.format(**(item.params or {})) if template else item.messages[0])
    return messages


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "role")
        read_only_fields = fields


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(error_messages=EMAIL_ERRORS)
    password = serializers.CharField(
        write_only=True, trim_whitespace=False, error_messages=PASSWORD_ERRORS
    )
    role = serializers.ChoiceField(
        choices=User.Role.choices,
        error_messages={
            "required": "Дүрээ сонгоно уу.",
            "invalid_choice": "Багш эсвэл Сурагч дүрийг сонгоно уу.",
        },
    )

    def validate(self, attrs):
        candidate = User(email=attrs["email"], role=attrs["role"])
        try:
            validate_password(attrs["password"], user=candidate)
        except DjangoValidationError as error:
            raise serializers.ValidationError({"password": _password_messages(error)}) from error
        return attrs


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(error_messages=EMAIL_ERRORS)
    password = serializers.CharField(
        write_only=True, trim_whitespace=False, error_messages=PASSWORD_ERRORS
    )
