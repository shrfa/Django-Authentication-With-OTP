# views.py
from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.conf import settings
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView


# Local Imports
from apps.users.api.serializers import UserSerializer, ChangePasswordSerializer
from apps.users.api.mixins import OTPMixin, ResetPasswordMixin
from apps.users.api.serializers import CookieTokenRefreshSerializer

otp_method = settings.OTP_DELIVERY_METHOD


User = get_user_model()


class UserViewSet(
    viewsets.ViewSet, OTPMixin, ResetPasswordMixin, generics.GenericAPIView
):
    """
    ViewSet for managing user-related actions.

    This ViewSet includes actions for OTP generation, verification, and retrieving user information.

    Actions:
    - generate_otp: Generates and sends a one-time password (OTP) for user verification.
    - verify_otp_and_create_user: Verifies an OTP and creates a user account.
    - me: Retrieves information about the currently authenticated user.

    """

    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in [
            "list",
            "retrieve",
            "me",
            "change_password",
            "reset_password",
        ]:
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    @action(detail=False, methods=["get"])
    def me(self, request):
        """
        Retrieve information about the currently authenticated user.

        Returns:
        - 200 OK with user information if the user is authenticated.
        - 401 Unauthorized if the user is not authenticated.

        """
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(detail=False, serializer_class=ChangePasswordSerializer, methods=["post"])
    def change_password(self, request):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            user = get_object_or_404(User, pk=request.user.id)
            user.set_password(serializer.validated_data["password"])
            user.save()
            return Response(
                status=status.HTTP_200_OK,
                data={"message": "Password has been changed successfully"},
            )
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)


class CookieTokenObtainPairView(TokenObtainPairView):
    def finalize_response(self, request, response, *args, **kwargs):
        if response.data.get("refresh"):
            cookie_max_age = 3600 * 24 * 14  # 14 days
            response.set_cookie(
                "refresh_token",
                response.data["refresh"],
                max_age=cookie_max_age,
                httponly=True,
            )
        del response.data["refresh"]
        return super().finalize_response(request, response, *args, **kwargs)


class CookieTokenRefreshView(TokenRefreshView):
    def finalize_response(self, request, response, *args, **kwargs):
        if response.data.get("refresh"):
            cookie_max_age = 3600 * 24 * 14  # 14 days
            response.set_cookie(
                "refresh_token",
                response.data["refresh"],
                max_age=cookie_max_age,
                httponly=True,
            )
        del response.data["refresh"]
        return super().finalize_response(request, response, *args, **kwargs)

    serializer_class = CookieTokenRefreshSerializer
