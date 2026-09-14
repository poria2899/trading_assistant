from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class PlaceholderPagesTests(TestCase):
    """Journal/backtesting are placeholders until their real phases land."""

    def setUp(self):
        User.objects.create_user(username="someone", password="SuperSecret123!")
        self.client.login(username="someone", password="SuperSecret123!")

    def test_journal_placeholder(self):
        response = self.client.get(reverse("journal:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Coming in Phase 2")

    def test_backtesting_placeholder(self):
        response = self.client.get(reverse("backtesting:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Coming in Phase 5")
