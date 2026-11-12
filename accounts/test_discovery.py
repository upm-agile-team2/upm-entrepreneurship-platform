from django.test import TestCase

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
