from django.test import TestCase
from django.urls import reverse

from ideas.models import Feedback, Idea

from .models import InvestorInterest, InvestorProfile, User


class InvestorProfileDetailTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.student = User.objects.create_user(
            email="student@example.com", name="Blair Student", role=User.Role.STUDENT
        )
        cls.investor = User.objects.create_user(
            email="investor@example.com", name="Avery Investor", role=User.Role.INVESTOR
        )
        cls.other_investor = User.objects.create_user(
            email="other@example.com", name="Casey Investor", role=User.Role.INVESTOR
        )
        cls.profile = InvestorProfile.objects.create(
            user=cls.investor,
            experience="Experience with energy startups",
            past_projects="Campus microgrid",
        )
        cls.clean_energy = InvestorInterest.objects.create(
            name="Clean energy", normalized_name="clean energy"
        )
        cls.profile.interests.add(cls.clean_energy)
        cls.url = reverse("accounts:investor_profile_detail", args=[cls.investor.pk])
        cls.idea = Idea.objects.create(
            owner=cls.student, title="Solar dashboard", description="Energy data for the campus."
        )
        cls.old_feedback = Feedback.objects.create(
            author=cls.investor, idea=cls.idea, text="Public feedback on the first design."
        )
        cls.new_feedback = Feedback.objects.create(
            author=cls.investor, idea=cls.idea, text="Public feedback on the second design."
        )
        cls.private = Feedback.objects.create(
            author=cls.investor, idea=cls.idea, text="Private details for the owner.", is_private=True
        )
        cls.other_feedback = Feedback.objects.create(
            author=cls.other_investor, idea=cls.idea, text="Another investor's public feedback."
        )

    def test_profile_requires_a_signed_in_student(self):
        self.assertRedirects(
            self.client.get(self.url),
            f"{reverse('accounts:login')}?next={self.url}",
        )
        self.client.force_login(self.other_investor)
        self.assertEqual(self.client.get(self.url).status_code, 403)

    def test_detail_loads_only_active_investors_with_a_saved_profile(self):
        self.client.force_login(self.student)
        for user_id in (self.student.pk, self.other_investor.pk):
            with self.subTest(user_id=user_id):
                url = reverse("accounts:investor_profile_detail", args=[user_id])
                self.assertEqual(self.client.get(url).status_code, 404)
        User.objects.filter(pk=self.investor.pk).update(is_active=False)
        self.assertEqual(self.client.get(self.url).status_code, 404)

    def test_profile_loads_only_its_public_feedback_even_for_an_idea_owner(self):
        self.client.force_login(self.student)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["profile"], self.profile)
        self.assertEqual(
            list(response.context["public_feedback"]),
            [self.new_feedback, self.old_feedback],
        )

    def test_student_can_open_a_profile_from_feedback_and_read_available_details(self):
        self.client.force_login(self.student)
        idea_url = reverse("ideas:detail", args=[self.idea.pk])
        idea_response = self.client.get(idea_url)
        self.assertContains(idea_response, f'href="{self.url}">{self.investor.name}</a>')
        no_profile_url = reverse("accounts:investor_profile_detail", args=[self.other_investor.pk])
        self.assertNotContains(idea_response, f'href="{no_profile_url}"')

        response = self.client.get(self.url)
        for value in (
            "Experience with energy startups",
            "Campus microgrid",
            "Clean energy",
            self.old_feedback.text,
            self.new_feedback.text,
        ):
            self.assertContains(response, value)
        self.assertContains(response, f'href="{idea_url}#feedback-{self.new_feedback.pk}"')
        self.assertNotContains(response, self.private.text)
        self.assertNotContains(response, self.other_feedback.text)
        self.assertNotContains(response, self.investor.email)
        self.assertNotContains(response, reverse("accounts:edit_investor_profile"))

    def test_incomplete_profile_shows_its_available_information(self):
        InvestorProfile.objects.create(user=self.other_investor, bio="Ready to mentor.")
        self.other_feedback.delete()
        self.client.force_login(self.student)
        response = self.client.get(
            reverse("accounts:investor_profile_detail", args=[self.other_investor.pk])
        )
        self.assertContains(response, "Ready to mentor.")
        self.assertContains(response, "No experience added yet.")
        self.assertContains(response, "No public feedback yet.")
