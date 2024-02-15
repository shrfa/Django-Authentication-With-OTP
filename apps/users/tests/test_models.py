from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.users.models import OtpVerification

class UserModelTest(TestCase):
    def setUp(self):
        self.user_data = {
            "email": "test@example.com",
            "phone_number": "1234567890",
            "password": "testpassword",
        }
        self.user = get_user_model().objects.create_user(**self.user_data)

    def test_user_creation(self):
        self.assertEqual(self.user.email, self.user_data["email"])
        self.assertEqual(self.user.phone_number, self.user_data["phone_number"])
        self.assertTrue(self.user.check_password(self.user_data["password"]))
        self.assertFalse(self.user.is_deleted)
        self.assertFalse(self.user.is_verified)

    def test_user_manager_create_superuser(self):
        superuser = get_user_model().objects.create_superuser(
            email="admin@example.com", password="adminpassword"
        )
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

class OtpVerificationModelTest(TestCase):
    def setUp(self):
        self.user_data = {
            "email": "test@example.com",
            "phone_number": "1234567890",
            "password": "testpassword",
        }
        self.user = get_user_model().objects.create_user(**self.user_data)
        self.otp_data = {
            "user_data": {"user_id": self.user.id, "username": self.user.username},
            "otp_code": "123456",
        }
        self.otp_verification = OtpVerification.objects.create(**self.otp_data)

    def test_otp_verification_creation(self):
        self.assertEqual(self.otp_verification.user_data["user_id"], self.user.id)
        self.assertEqual(self.otp_verification.otp_code, self.otp_data["otp_code"])
        self.assertFalse(self.otp_verification.is_verified)
