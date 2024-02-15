from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.shortcuts import get_object_or_404

# Local Imports
from apps.users.models import OtpVerification
from apps.users.utils import send_otp, generate_otp
from apps.users.api.serializers import (
    UserSignUpSerializer,
    ForgotPassSerializer,
    VerificationSerializer,
    ResetPassSerializer,
)

otp_method = settings.OTP_DELIVERY_METHOD
User = get_user_model()


class OTPMixin:
    @action(detail=False, methods=["post"], serializer_class=UserSignUpSerializer)
    def generate_otp(self, request):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data["email"]
            phone_number = serializer.validated_data["phone_number"]
            user_data = {
                "first_name": serializer.validated_data["first_name"],
                "last_name": serializer.validated_data["last_name"],
                "email": email,
                "phone_number": phone_number,
                "password": serializer.validated_data["password"],
            }

            otp_code = generate_otp(6)

            # Send OTP using the configured method (Twilio, SendGrid, Smtp)
            send_otp(email, otp_method, otp_code)

            OtpVerification.objects.create(user_data=user_data, otp_code=otp_code)
            return Response(
                {"message": "OTP sent successfully"}, status=status.HTTP_200_OK
            )

    @action(detail=False, methods=["post"], serializer_class=VerificationSerializer)
    def verify_otp_and_create_user(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            input_otp = serializer.validated_data["otp"]

            try:
                verification = OtpVerification.objects.filter(
                    user_data__email=email, otp=input_otp, is_verified=False
                ).first()

                expiration_time = verification.created_at + timezone.timedelta(
                    minutes=5
                )

                if timezone.now() > expiration_time:
                    verification.delete()
                    return Response(
                        {"message": "OTP has expired"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                verification.is_verified = True
                verification.save()
                user_data = verification.user_data
                user = User.objects.create_user(**user_data)
                user.save()

                response_data = {"message": "User created successfully"}
                return Response(response_data, status=status.HTTP_201_CREATED)
            except OtpVerification.DoesNotExist:
                return Response(
                    {"message": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordMixin:
    @action(detail=False, methods=["post"], serializer_class=ForgotPassSerializer)
    def forgot_password(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                response_data = {"error": "User not found"}
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)

            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = (
                f"{settings.FRONTEND_RESET_PASSWORD_URL}?uid={uid}&token={token}"
            )

            template = "reset_password.html"
            context = {"link": reset_link, "first_name": user.first_name}

            send_otp("Password Reset Link", template, context, email)

            response_data = {"message": "Password reset link sent successfully"}
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], serializer_class=ResetPassSerializer)
    def reset_password(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            uid = serializer.validated_data["uid"]
            token = serializer.validated_data["token"]
            password = serializer.validated_data["password"]

            user_id = force_str(urlsafe_base64_decode(uid))
            user = get_object_or_404(User, pk=user_id)

            # Check if the token is valid and hasn't been used
            if (
                default_token_generator.check_token(user, token)
                and not user.password_reset_timestamp
            ):
                # Check if the token has expired (e.g., 5 minutes)
                token_timestamp = user.password_reset_timestamp

                current_time = datetime.now()
                time_difference = current_time - token_timestamp
                token_expiry_duration = timedelta(minutes=5)

                if time_difference <= token_expiry_duration:
                    user.set_password(password)
                    user.save()

                    # Set the timestamp to indicate the token has been used
                    user.password_reset_timestamp = current_time
                    user.save()

                    response_data = {"message": "Password reset successfully"}
                    return Response(response_data, status=status.HTTP_200_OK)
                else:
                    response_data = {"error": "Token has expired"}
                    return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            else:
                response_data = {"error": "Invalid or already used token"}
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
