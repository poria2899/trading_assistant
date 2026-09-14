from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class RegistrationTests(TestCase):
    def test_register_creates_user_and_logs_in(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "password1": "SuperSecret123!",
                "password2": "SuperSecret123!",
            },
        )
        self.assertRedirects(response, reverse("core:home"))
        self.assertTrue(User.objects.filter(username="newuser").exists())
        # Registering also logs the user in, so the home page is reachable
        # immediately without a separate login step.
        home = self.client.get(reverse("core:home"))
        self.assertEqual(home.status_code, 200)
        self.assertContains(home, "newuser")


class LoginLogoutTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="existing", password="SuperSecret123!")

    def test_login_redirects_to_home(self):
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "existing", "password": "SuperSecret123!"},
        )
        self.assertRedirects(response, reverse("core:home"))

    def test_logout_redirects_to_login(self):
        self.client.login(username="existing", password="SuperSecret123!")
        response = self.client.post(reverse("accounts:logout"))
        self.assertRedirects(response, reverse("accounts:login"))


class HomePageAccessTests(TestCase):
    def test_home_requires_login(self):
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)

    def test_home_accessible_when_logged_in(self):
        User.objects.create_user(username="someone", password="SuperSecret123!")
        self.client.login(username="someone", password="SuperSecret123!")
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
