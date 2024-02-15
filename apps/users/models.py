from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

# Local Imports
from apps.users.managers import UserManager
from apps.users.fields import LowercaseEmailField


# Create your models here.
class User(AbstractUser):
    email = LowercaseEmailField(verbose_name=_("Email Address"), unique=True)
    phone_number = models.CharField(verbose_name=_("Phone Number"), max_length=50)
    is_deleted = models.BooleanField(verbose_name=_("Is Deleted"), default=False)
    is_verified = models.BooleanField(verbose_name=_("Is Verified"), default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        db_table = _("users")


class OtpVerification(models.Model):
    user_data = models.JSONField(verbose_name=_("User Data"), default=dict)
    otp_code = models.CharField(verbose_name=_("OTP Code"), max_length=6)
    created_at = models.DateTimeField(verbose_name=_("Created At"), auto_now_add=True)
    is_verified = models.BooleanField(verbose_name=_("Is Verified"), default=False)

    class Meta:
        verbose_name = _("OTP Verification")
        verbose_name_plural = _("OTP Verifications")
        db_table = _("otp_verifications")
