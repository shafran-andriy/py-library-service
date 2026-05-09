from django.test import TestCase
from django.contrib.auth import get_user_model

from user.serializers import UserSerializer


class UserSerializerTests(TestCase):
    def test_create_user_with_encrypted_password(self):
        data = {
            "email": "test@example.com",
            "password": "strongpass",
            "first_name": "Test",
            "last_name": "User",
        }
        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        self.assertNotEqual(user.password, data["password"])
        self.assertTrue(user.check_password(data["password"]))

    def test_update_user_password(self):
        User = get_user_model()
        user = User.objects.create_user(email="up@example.com", password="oldpass")
        serializer = UserSerializer(user, data={"password": "newpass"}, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        user.refresh_from_db()
        self.assertTrue(user.check_password("newpass"))
