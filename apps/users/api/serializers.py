from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
import re
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.exceptions import InvalidToken

User = get_user_model()


class PasswordValidatorMixin:
    def validate(self, attrs):
        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")
        self.regex = re.compile(r"[A-Za-z0-9@#$%^&+=]*$")

        if len(password) < 8:
            raise serializers.ValidationError(
                "Password must be at least 8 characters long."
            )
        elif password != confirm_password:
            raise serializers.ValidationError("Passwords do not match.")

        elif not self.regex.match(password):
            raise serializers.ValidationError(
                "The password can only contain alphanumeric characters and special symbols.",
                code="password_invalid",
            )

        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ["password"]


class UserSignUpSerializer(PasswordValidatorMixin, serializers.ModelSerializer):
    password = serializers.CharField(
        label=_("Password"),
        style={"input_type": "password"},
        trim_whitespace=False,
        required=True,
    )
    confirm_password = serializers.CharField(
        label=_("Confirm Password"),
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True,
        required=True,
    )

    class Meta:
        model = User
        fields = (
            "email",
            "phone_number",
            "first_name",
            "last_name",
            "password",
            "confirm_password",
        )

class VerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(min_length=4, max_length=4)


class ForgotPassSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPassSerializer(PasswordValidatorMixin, serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    password = serializers.CharField(
        label=_("Password"),
        style={"input_type": "password"},
        trim_whitespace=False,
        required=True,
    )
    confirm_password = serializers.CharField(
        label=_("Confirm Password"),
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True,
        required=True,
    )


class ChangePasswordSerializer(PasswordValidatorMixin, serializers.Serializer):
    old_password = serializers.CharField(
        label=_("Old Password"),
        style={"input_type": "password"},
        trim_whitespace=False,
        required=True,
    )
    password = serializers.CharField(
        label=_("Password"),
        style={"input_type": "password"},
        trim_whitespace=False,
        required=True,
    )
    confirm_password = serializers.CharField(
        label=_("Confirm Password"),
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True,
        required=True,
    )

    def validate(self, attrs):
        old_password = attrs.get("old_password")
        if not self.context["request"].user.check_password(old_password):
            raise serializers.ValidationError(_("old password is not correct"))
        attrs = super().validate(attrs)

        if attrs.get("password") == old_password:
            raise serializers.ValidationError(
                _(" The new password can't be the same as the old password")
            )

        return attrs

class CookieTokenRefreshSerializer(TokenRefreshSerializer):
    refresh = None

    def validate(self, attrs):
        attrs['refresh'] = self.context['request'].COOKIES.get('refresh_token')
        if attrs['refresh']:
            return super().validate(attrs)
        else:
            raise InvalidToken('No valid token found in cookie\'refresh_token\'')
