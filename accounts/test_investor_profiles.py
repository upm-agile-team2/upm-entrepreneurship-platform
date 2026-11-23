from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import Client, TestCase
from django.urls import reverse

from .models import InvestorInterest, InvestorProfile, User


class InvestorProfileModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.investor = User.objects.create_user(
            email="investor@example.com", name="Avery Investor", role=User.Role.INVESTOR
        )
        cls.student = User.objects.create_user(
            email="student@example.com", name="Blair Student", role=User.Role.STUDENT
        )

    def test_only_investors_pass_profile_validation(self):
        InvestorProfile(user=self.investor).full_clean()
        with self.assertRaises(ValidationError) as error:
            InvestorProfile(user=self.student).full_clean()
        self.assertIn("user", error.exception.message_dict)

    def test_database_enforces_one_profile_per_investor(self):
        InvestorProfile.objects.create(user=self.investor)
        with self.assertRaises(IntegrityError), transaction.atomic():
            InvestorProfile.objects.create(user=self.investor)


class InvestorProfileEditorTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.investor = User.objects.create_user(
            email="investor@example.com", name="Avery Investor", role=User.Role.INVESTOR
        )
        cls.student = User.objects.create_user(
            email="student@example.com", name="Blair Student", role=User.Role.STUDENT
        )
        cls.editor = reverse("accounts:edit_investor_profile")

    def test_editor_requires_an_investor_account(self):
        self.assertRedirects(
            self.client.get(self.editor),
            f"{reverse('accounts:login')}?next={self.editor}",
        )
        self.client.force_login(self.student)
        self.assertEqual(self.client.get(self.editor).status_code, 403)
        self.assertEqual(self.client.post(self.editor, {"bio": "Forbidden"}).status_code, 403)
        self.assertFalse(InvestorProfile.objects.exists())

    def test_get_does_not_create_profile_and_post_creates_for_session_user(self):
        self.client.force_login(self.investor)
        self.assertContains(self.client.get(self.editor), "Create your investor profile")
        self.assertFalse(InvestorProfile.objects.exists())
        response = self.client.post(
            self.editor,
            {
                "user": self.student.pk,
                "bio": "I support student ventures.",
                "experience": "Ten years advising startups.",
                "past_projects": "Campus microgrid.",
                "support_offers": "Mentoring",
                "interest_names": "Robotics, Clean   energy, robotics",
            },
        )
        self.assertEqual(response.status_code, 302)
        profile = InvestorProfile.objects.get(user=self.investor)
        self.assertEqual(profile.bio, "I support student ventures.")
        self.assertEqual(profile.experience, "Ten years advising startups.")
        self.assertEqual(profile.past_projects, "Campus microgrid.")
        self.assertEqual(profile.support_offers, "Mentoring")
        self.assertEqual(list(profile.interests.values_list("name", flat=True)), ["Clean energy", "Robotics"])
        self.assertFalse(InvestorProfile.objects.filter(user=self.student).exists())

    def test_update_replaces_interests_and_preserves_a_single_profile(self):
        profile = InvestorProfile.objects.create(user=self.investor, bio="Earlier bio")
        original = InvestorInterest.objects.create(name="Robotics", normalized_name="robotics")
        profile.interests.add(original)
        self.client.force_login(self.investor)
        self.assertContains(self.client.get(self.editor), 'value="Robotics"')

        self.client.post(
            self.editor, {"bio": "Updated bio", "interest_names": "Clean energy"}
        )
        profile.refresh_from_db()
        self.assertEqual(profile.bio, "Updated bio")
        self.assertEqual(list(profile.interests.values_list("name", flat=True)), ["Clean energy"])
        self.assertEqual(InvestorProfile.objects.filter(user=self.investor).count(), 1)

    def test_invalid_interests_leave_profile_and_tags_unchanged(self):
        profile = InvestorProfile.objects.create(user=self.investor, bio="Earlier bio")
        self.client.force_login(self.investor)
        for bad_value, error in (
            ("a" * 81, "Each interest must be 80 characters or fewer."),
            (",".join(f"Topic {n}" for n in range(11)), "Enter no more than 10 different interests."),
        ):
            with self.subTest(bad_value=bad_value):
                response = self.client.post(
                    self.editor, {"bio": "Unsaved bio", "interest_names": bad_value}
                )
                self.assertContains(response, error)
        profile.refresh_from_db()
        self.assertEqual(profile.bio, "Earlier bio")
        self.assertFalse(InvestorInterest.objects.exists())

    def test_save_requires_csrf_token(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.investor)
        self.assertEqual(client.post(self.editor, {"bio": "Blocked"}).status_code, 403)
        self.assertFalse(InvestorProfile.objects.exists())

    def test_navigate_to_profile_create_and_preview_saved_changes(self):
        self.client.force_login(self.investor)
        own_profile = reverse("accounts:my_investor_profile")
        home = self.client.get(reverse("ideas:home"))
        self.assertContains(home, f'href="{own_profile}">My profile</a>')
        self.assertContains(self.client.get(own_profile), f'href="{self.editor}">Create your profile</a>')

        response = self.client.post(
            self.editor,
            {
                "bio": "I advise student founders.",
                "experience": "Renewable energy consulting",
                "past_projects": "Campus microgrid",
                "interest_names": "Clean energy",
                "support_offers": "Mentoring",
            },
            follow=True,
        )
        self.assertRedirects(response, own_profile)
        for value in (
            "I advise student founders.",
            "Renewable energy consulting",
            "Campus microgrid",
            "Clean energy",
            "Mentoring",
        ):
            self.assertContains(response, value)
        self.assertContains(response, f'href="{self.editor}">Edit profile</a>')

        response = self.client.post(self.editor, {"experience": "New experience"}, follow=True)
        self.assertContains(response, "New experience")
        self.assertNotContains(response, "Renewable energy consulting")

    def test_student_cannot_open_investor_owner_preview(self):
        self.client.force_login(self.student)
        self.assertEqual(self.client.get(reverse("accounts:my_investor_profile")).status_code, 403)
