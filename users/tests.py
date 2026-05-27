from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            email="test@example.com",
            name="Test",
            surname="User",
            password="testpass123",
        )
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertTrue(user.avatar)

    def test_create_superuser(self):
        user = User.objects.create_superuser(
            email="admin@example.com",
            name="Admin",
            surname="User",
            password="adminpass123",
        )
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_str(self):
        user = User.objects.create_user(
            email="str@example.com",
            name="Name",
            surname="Surname",
            password="pass",
        )
        self.assertIn("str@example.com", str(user))


class RegisterViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_get(self):
        response = self.client.get(reverse("users:register"))
        self.assertEqual(response.status_code, 200)

    def test_register_post(self):
        response = self.client.post(reverse("users:register"), {
            "name": "John",
            "surname": "Doe",
            "email": "john@example.com",
            "password": "secret123",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email="john@example.com").exists())

    def test_register_duplicate_email(self):
        User.objects.create_user(email="dup@example.com", name="A", surname="B", password="pass")
        response = self.client.post(reverse("users:register"), {
            "name": "C",
            "surname": "D",
            "email": "dup@example.com",
            "password": "pass",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "уже существует")


class LoginViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="login@example.com",
            name="Log",
            surname="In",
            password="loginpass",
        )

    def test_login_get(self):
        response = self.client.get(reverse("users:login"))
        self.assertEqual(response.status_code, 200)

    def test_login_success(self):
        response = self.client.post(reverse("users:login"), {
            "email": "login@example.com",
            "password": "loginpass",
        })
        self.assertEqual(response.status_code, 302)

    def test_login_wrong_password(self):
        response = self.client.post(reverse("users:login"), {
            "email": "login@example.com",
            "password": "wrong",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Неверный")


class UsersListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        User.objects.create_user(email="u1@e.com", name="A", surname="B", password="p")
        User.objects.create_user(email="u2@e.com", name="C", surname="D", password="p")

    def test_users_list(self):
        response = self.client.get(reverse("users:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A")
