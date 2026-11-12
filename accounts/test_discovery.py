from html import unescape
import re

from django.test import TestCase
from django.urls import reverse

from .discovery import StudentProfileFilterForm, student_profiles
from .models import ProfileVisit, Skill, StudentProfile, User


class ProfileDiscoveryData:
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.python = Skill.objects.create(name="Python")
        cls.robotics = Skill.objects.create(name="Robotics")
        cls.unused = Skill.objects.create(name="Biotechnology")

        def user(email, name, role=User.Role.STUDENT, **kwargs):
            return User.objects.create_user(email=email, name=name, role=role, **kwargs)

        cls.alex = user("discovery-alex@example.com", "alex Rivera")
        cls.marta = user("discovery-marta@example.com", "Marta Lopez")
        cls.empty = user("discovery-empty@example.com", "ELENA Garcia")
        cls.without_profile = user("discovery-no-profile@example.com", "No profile")
        cls.inactive = user("discovery-inactive@example.com", "Inactive", is_active=False)
        cls.investor = user("discovery-investor@example.com", "Investor", User.Role.INVESTOR)
        cls.alex_profile = StudentProfile.objects.create(user=cls.alex, bio="Campus robotics projects.")
        cls.alex_profile.skills.set([cls.python, cls.robotics])
        cls.marta_profile = StudentProfile.objects.create(user=cls.marta, bio="Practical prototypes.")
        cls.marta_profile.skills.add(cls.robotics)
        cls.empty_profile = StudentProfile.objects.create(user=cls.empty)
        StudentProfile.objects.create(user=cls.inactive).skills.add(cls.python)
        # Historical or administrative writes can bypass StudentProfile.clean().
        StudentProfile.objects.create(user=cls.investor).skills.add(cls.python)


class ProfileDiscoveryBackendTests(ProfileDiscoveryData, TestCase):
    def test_directory_includes_only_saved_profiles_of_active_students(self):
        self.assertEqual(
            list(student_profiles()),
            [self.alex_profile, self.empty_profile, self.marta_profile],
        )

    def test_skill_filter_matches_profiles_and_preserves_all_their_skills(self):
        matches = list(student_profiles(self.python))
        self.assertEqual(matches, [self.alex_profile])
        self.assertEqual(list(matches[0].skills.all()), [self.python, self.robotics])
        self.assertEqual(list(student_profiles(self.robotics)), [self.alex_profile, self.marta_profile])

    def test_valid_skill_without_matching_profiles_has_no_results(self):
        self.assertFalse(student_profiles(self.unused).exists())

    def test_order_is_case_insensitive_and_stable_for_equal_names(self):
        self.marta.name = self.alex.name.upper()
        self.marta.save()
        self.assertEqual(
            list(student_profiles()),
            [self.alex_profile, self.marta_profile, self.empty_profile],
        )

    def test_empty_selection_means_all_skills(self):
        for data in ({}, {"skill": ""}):
            with self.subTest(data=data):
                form = StudentProfileFilterForm(data)
                self.assertTrue(form.is_valid())
                self.assertIsNone(form.cleaned_data["skill"])

    def test_selected_skill_is_validated_against_the_current_catalogue(self):
        form = StudentProfileFilterForm({"skill": str(self.python.pk)})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["skill"], self.python)
        added = Skill.objects.create(name="Accessibility")
        self.assertIn(added, StudentProfileFilterForm().fields["skill"].queryset)

    def test_invalid_identifiers_are_form_errors(self):
        for value in ("not-a-skill", "-1", "999999", "9" * 100):
            with self.subTest(value=value):
                form = StudentProfileFilterForm({"skill": value})
                self.assertFalse(form.is_valid())
                self.assertIn("skill", form.errors)

    def test_profiles_users_and_skills_are_fetched_in_two_queries(self):
        with self.assertNumQueries(2):
            cards = [(profile.user.name, list(profile.skills.all())) for profile in student_profiles()]
        self.assertEqual(len(cards), 3)
        self.assertFalse(ProfileVisit.objects.exists())


class ProfileDiscoveryViewTests(ProfileDiscoveryData, TestCase):
    def setUp(self):
        self.url = reverse("accounts:student_discovery")

    def test_anonymous_visitor_is_asked_to_sign_in(self):
        self.assertRedirects(
            self.client.get(self.url), f"{reverse('accounts:login')}?next={self.url}"
        )

    def test_student_cannot_open_the_investor_directory(self):
        self.client.force_login(self.alex)
        self.assertEqual(self.client.get(self.url).status_code, 403)

    def test_only_get_requests_are_accepted(self):
        self.client.force_login(self.investor)
        for method in ("POST", "PUT", "DELETE"):
            with self.subTest(method=method):
                self.assertEqual(self.client.generic(method, self.url).status_code, 405)

    def test_browsing_filtering_and_invalid_filters_do_not_record_visits(self):
        self.client.force_login(self.investor)
        for data in ({}, {"skill": self.python.pk}, {"skill": self.unused.pk}, {"skill": "invalid"}):
            with self.subTest(data=data):
                self.assertEqual(self.client.get(self.url, data).status_code, 200)
        self.assertFalse(ProfileVisit.objects.exists())

    def test_invalid_filter_shows_an_error_without_returning_unfiltered_profiles(self):
        self.client.force_login(self.investor)
        for value in ("invalid", "-1", "999999", "9" * 100):
            with self.subTest(value=value):
                response = self.client.get(self.url, {"skill": value})
                self.assertContains(response, "Choose a skill from the list.")
                self.assertContains(response, 'aria-invalid="true"')
                self.assertEqual(response.context["profiles"], [])
                self.assertNotContains(response, self.alex.name)

    def test_profile_skill_edits_are_reflected_on_the_next_request(self):
        self.client.force_login(self.investor)
        first = self.client.get(self.url, {"skill": self.robotics.pk})
        self.assertEqual(first.context["profile_count"], 2)
        self.marta_profile.skills.clear()
        refreshed = self.client.get(self.url, {"skill": self.robotics.pk})
        self.assertEqual(refreshed.context["profiles"], [self.alex_profile])


class ProfileDiscoveryPresentationTests(ProfileDiscoveryData, TestCase):
    def setUp(self):
        self.url = reverse("accounts:student_discovery")
        self.client.force_login(self.investor)

    def test_filter_has_a_label_preserved_selection_count_and_clear_control(self):
        response = self.client.get(self.url, {"skill": self.python.pk})
        self.assertContains(response, 'for="id_skill"')
        self.assertContains(response, 'aria-describedby="id_skill_helptext"')
        self.assertContains(response, f'value="{self.python.pk}" selected')
        self.assertContains(response, "1 profile")
        self.assertContains(response, "Clear filter")
        self.assertContains(response, 'aria-current="page"')

    def test_cards_show_showcase_fields_without_emails_or_edit_links(self):
        response = self.client.get(self.url)
        for content in (self.alex.name, self.marta.name, self.empty.name, self.alex_profile.bio, "Python", "Robotics"):
            self.assertContains(response, content)
        self.assertContains(response, "This student is still building their profile.")
        self.assertContains(response, "No skills added yet.")
        self.assertContains(response, "3 profiles")
        self.assertContains(response, reverse("accounts:investor_profile", args=[self.alex.pk]))
        self.assertContains(response, 'col-12 col-md-6 col-xl-4')
        for user in (self.alex, self.marta, self.empty):
            self.assertNotContains(response, user.email)
        self.assertNotContains(response, reverse("accounts:student_profile"))
        self.assertNotContains(response, self.without_profile.name)
        self.assertNotContains(response, self.inactive.name)

    def test_profile_and_skill_content_is_escaped(self):
        self.alex.name = '<script>alert("student")</script>'
        self.alex.save()
        self.alex_profile.bio = '<img src=x onerror="alert(1)">'
        self.alex_profile.save()
        self.python.name = "<script>skill</script>"
        self.python.save()
        response = self.client.get(self.url)
        self.assertContains(response, "&lt;script&gt;")
        self.assertContains(response, "&lt;img")
        self.assertNotContains(response, self.alex.name)
        self.assertNotContains(response, self.alex_profile.bio)
        self.assertNotContains(response, self.python.name)

    def test_valid_filter_without_results_has_a_clear_explanation(self):
        response = self.client.get(self.url, {"skill": self.unused.pk})
        self.assertContains(response, "No matching profiles")
        self.assertContains(response, self.unused.name)
        self.assertContains(response, "Clear filter")
        self.assertEqual(response.context["profile_count"], 0)

    def test_empty_directory_has_a_distinct_message_and_idea_browsing_link(self):
        StudentProfile.objects.all().delete()
        response = self.client.get(self.url)
        self.assertContains(response, "No student profiles yet")
        self.assertContains(response, "Explore ideas")
        self.assertNotContains(response, "No matching profiles")

    def test_empty_skill_catalogue_keeps_saved_profiles_available(self):
        Skill.objects.all().delete()
        response = self.client.get(self.url)
        self.assertContains(response, "No skills are available to filter yet.")
        self.assertContains(response, "All skills")
        self.assertEqual(response.context["profile_count"], 3)

    def test_students_navigation_is_visible_only_to_investors(self):
        for user in (self.investor, self.alex, None):
            with self.subTest(user=user.pk if user else None):
                self.client.logout()
                if user:
                    self.client.force_login(user)
                response = self.client.get(reverse("ideas:home"))
                link = f'href="{self.url}"'
                if user == self.investor:
                    self.assertContains(response, link)
                else:
                    self.assertNotContains(response, link)


class ProfileDiscoveryAcceptanceTests(ProfileDiscoveryData, TestCase):
    def setUp(self):
        self.url = reverse("accounts:student_discovery")
        self.client.force_login(self.investor)

    def test_investor_filters_sees_no_matches_and_clears_the_filter(self):
        full_list = self.client.get(self.url)
        self.assertEqual(full_list.context["profile_count"], 3)
        filtered = self.client.get(self.url, {"skill": self.python.pk})
        self.assertEqual(filtered.context["profiles"], [self.alex_profile])
        no_matches = self.client.get(self.url, {"skill": self.unused.pk})
        self.assertContains(no_matches, "No matching profiles")
        clear_link = re.search(
            r'<a[^>]*href="([^"]+)"[^>]*>\s*Clear filter\s*</a>',
            no_matches.content.decode(),
        )
        self.assertIsNotNone(clear_link)
        cleared = self.client.get(unescape(clear_link.group(1)))
        self.assertEqual(cleared.context["profiles"], full_list.context["profiles"])
        self.assertIsNone(cleared.context["selected_skill"])
        self.assertNotContains(cleared, "Clear filter")
        self.assertFalse(ProfileVisit.objects.exists())

    def test_opening_a_discovered_profile_records_a_visit_for_its_owner(self):
        directory = self.client.get(self.url, {"skill": self.python.pk})
        profile_url = reverse("accounts:investor_profile", args=[self.alex.pk])
        self.assertContains(directory, f'href="{profile_url}"')
        self.assertFalse(ProfileVisit.objects.exists())
        self.assertEqual(self.client.get(profile_url).status_code, 200)
        visit = ProfileVisit.objects.get()
        self.assertEqual((visit.student, visit.visitor), (self.alex, self.investor))
        self.client.force_login(self.alex)
        own_profile = self.client.get(reverse("accounts:my_profile"))
        self.assertContains(own_profile, "Investors have visited your profile 1 time.")
