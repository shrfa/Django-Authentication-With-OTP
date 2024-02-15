from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from apps.users.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model

from apps.users.models import OtpVerification

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm

    list_display = ["id", "email", "first_name", "last_name"]
    search_fields = ["email"]
    ordering = ["-id"]

    fieldsets = (
        (None, {"fields": ("email",)}),
        (
            "Personal Info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "phone_number",
                )
            },
        ),
        (
            "Permissions",
            {"fields": ("is_staff", "is_superuser")},
        ),
    )
    readonly_fields = ["date_joined"]
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "password",
                    "confirm_password",
                    "first_name",
                    "last_name",
                ),
            },
        ),
    )


@admin.register(OtpVerification)
class OtpVerificationAdmin(admin.ModelAdmin):
    list_display = ("otp_code", "get_user_email", "created_at")
    list_filter = ("created_at",)
    search_fields = ("get_user_email",)
    readonly_fields = ("otp_code", "get_user_email", "created_at")

    fieldsets = (
        (None, {"fields": ("otp_code", "get_user_email", "created_at", "is_verified")}),
    )

    def get_user_email(self, obj):
        return obj.user_data.get("email", "")

    get_user_email.short_description = "User Email"
