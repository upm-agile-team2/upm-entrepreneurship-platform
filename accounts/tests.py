import re

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from ideas.forms import CollaboratorRequestForm
from ideas.models import Collaborator, CollaboratorRequest, Idea

from .forms import StudentProfileForm
from .models import Follow, ProfileVisit, Skill, StudentProfile
from .profile_display import collaborator_profile_context


User = get_user_model()


class AuthenticationFlowTests(TestCase):
    password = "A-valid-password-123!"

    def create_user(self, email="student@example.com", role=User.Role.STUDENT):
        return User.objects.create_user(
            email=email,
            password=self.password,
            name="Test User",
            role=role,
        )

    def test_home_is_public_and_shows_login(self):
        response = self.client.get(reverse("ideas:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Log in")
        self.assertNotContains(response, "Log out")

    def test_login_page_has_signup_link(self):
        response = self.client.get(reverse("accounts:login"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create an account")
        self.assertContains(response, 'name="username"')

    def test_valid_login_authenticates_and_redirects_home(self):
        self.create_user()
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "STUDENT@EXAMPLE.COM", "password": self.password},
        )
        self.assertRedirects(response, reverse("ideas:home"))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_invalid_login_is_generic_and_does_not_authenticate(self):
        self.create_user()
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "unknown@example.com", "password": "wrong-password"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please enter a correct email address and password.")
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_valid_signup_hashes_password_authenticates_and_redirects(self):
        response = self.client.post(
            reverse("accounts:signup"),
            {
                "name": "New Student",
                "email": "NEW@Example.com ",
                "role": User.Role.STUDENT,
                "password1": self.password,
                "password2": self.password,
            },
        )
        self.assertRedirects(response, reverse("ideas:home"))
        user = User.objects.get(email="new@example.com")
        self.assertEqual(user.name, "New Student")
        self.assertEqual(user.role, User.Role.STUDENT)
        self.assertTrue(user.check_password(self.password))
        self.assertNotEqual(user.password, self.password)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_duplicate_email_is_case_insensitive(self):
        self.create_user(email="existing@example.com")
        response = self.client.post(
            reverse("accounts:signup"),
            {
                "name": "Another User",
                "email": " Existing@Example.COM ",
                "role": User.Role.INVESTOR,
                "password1": self.password,
                "password2": self.password,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "This email is already registered. Please sign in or use another address.",
        )
        self.assertEqual(User.objects.filter(email__iexact="existing@example.com").count(), 1)

    def test_signup_rejects_mismatched_passwords_and_invalid_role(self):
        response = self.client.post(
            reverse("accounts:signup"),
            {
                "name": "New User",
                "email": "new@example.com",
                "role": "admin",
                "password1": self.password,
                "password2": "A-different-password-123!",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The two password fields didn’t match.")
        self.assertContains(response, "Select a valid choice")
        self.assertEqual(User.objects.count(), 0)

    def test_database_rejects_unknown_role(self):
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                email="invalid@example.com",
                password=self.password,
                name="Invalid Role",
                role="admin",
            )

    def test_authenticated_navigation_and_post_logout(self):
        self.create_user()
        self.client.login(username="student@example.com", password=self.password)
        response = self.client.get(reverse("ideas:home"))
        self.assertContains(response, "Log out")
        self.assertNotContains(response, ">Log in</a>")

        response = self.client.post(reverse("accounts:logout"))
        self.assertRedirects(response, reverse("ideas:home"))
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        response = self.client.get(reverse("ideas:home"))
        self.assertContains(response, "Log in")
        self.assertNotContains(response, "Log out")

    def test_logout_get_does_not_end_session(self):
        self.create_user()
        self.client.login(username="student@example.com", password=self.password)
        response = self.client.get(reverse("accounts:logout"))
        self.assertEqual(response.status_code, 405)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_logout_requires_csrf(self):
        client = Client(enforce_csrf_checks=True)
        self.create_user()
        client.login(username="student@example.com", password=self.password)
        response = client.post(reverse("accounts:logout"))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_external_next_is_not_used(self):
        self.create_user()
        response = self.client.post(
            reverse("accounts:login") + "?next=https://example.com",
            {"username": "student@example.com", "password": self.password},
        )
        self.assertRedirects(response, reverse("ideas:home"))


class RegistrationAcceptanceTests(TestCase):
    """US013: missing or invalid registration data produces visible errors."""

    def setUp(self):
        self.url = reverse("accounts:signup")
        self.valid_data = {
            "name": "New Student",
            "email": "new-student@example.com",
            "role": User.Role.STUDENT,
            "password1": "Registration-acceptance-123!",
            "password2": "Registration-acceptance-123!",
        }

    def assert_registration_rejected(self, response, field):
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertIn(field, form.errors)
        self.assertContains(response, form.errors[field][0])
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertFalse(User.objects.exists())

    def test_missing_required_registration_fields_show_errors(self):
        for field in self.valid_data:
            with self.subTest(field=field):
                data = self.valid_data.copy()
                del data[field]
                self.assert_registration_rejected(self.client.post(self.url, data), field)

    def test_invalid_registration_values_show_errors(self):
        invalid_values = [
            ({"name": "   "}, "name"),
            ({"email": "not-an-email"}, "email"),
            ({"password1": "short", "password2": "short"}, "password2"),
        ]
        for changes, field in invalid_values:
            with self.subTest(field=field):
                data = {**self.valid_data, **changes}
                self.assert_registration_rejected(self.client.post(self.url, data), field)

    def test_empty_registration_submission_shows_required_field_errors(self):
        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].is_bound)
        self.assertEqual(set(response.context["form"].errors), set(self.valid_data))
        self.assertContains(response, "This field is required.")
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertFalse(User.objects.exists())


@override_settings(ALLOW_ANONYMOUS_ACCESS=True)
class AuthenticatedFeatureJourneyTests(TestCase):
    """US014/US015: exercise the same session across real account and idea routes."""

    password = "Student-access-123!"

    @classmethod
    def setUpTestData(cls):
        cls.student = User.objects.create_user(
            email="journey-student@example.com",
            password=cls.password,
            name="Journey Student",
            role=User.Role.STUDENT,
        )

    def setUp(self):
        self.publish_url = reverse("ideas:publish")
        self.login_url = reverse("accounts:login")

    def test_login_prompt_allows_student_to_access_publish_form(self):
        prompt = self.client.get(self.publish_url)
        self.assertRedirects(
            prompt,
            f"{self.login_url}?next={self.publish_url}",
            fetch_redirect_response=False,
        )
        login_page = self.client.get(prompt.url)
        self.assertTemplateUsed(login_page, "registration/login.html")
        self.assertFalse(login_page.wsgi_request.user.is_authenticated)

        response = self.client.post(
            prompt.url,
            {"username": self.student.email, "password": self.password},
            follow=True,
        )

        self.assertRedirects(response, self.publish_url)
        self.assertTemplateUsed(response, "ideas/idea_form.html")
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertEqual(response.wsgi_request.user.pk, self.student.pk)

    def test_invalid_credentials_keep_publish_form_restricted(self):
        prompt = self.client.get(self.publish_url)
        self.assertRedirects(
            prompt,
            f"{self.login_url}?next={self.publish_url}",
            fetch_redirect_response=False,
        )
        self.assertTemplateUsed(self.client.get(prompt.url), "registration/login.html")

        response = self.client.post(
            prompt.url,
            {"username": self.student.email, "password": "wrong-password"},
        )

        self.assertContains(response, "Please enter a correct email address and password.")
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertRedirects(self.client.get(self.publish_url), prompt.url)
        self.assertEqual(Idea.objects.count(), 0)

    def test_logout_blocks_publish_get_and_post(self):
        login_response = self.client.post(
            self.login_url,
            {"username": self.student.email, "password": self.password},
        )
        self.assertRedirects(login_response, reverse("ideas:home"))
        self.assertTrue(login_response.wsgi_request.user.is_authenticated)
        self.assertTemplateUsed(
            self.client.get(self.publish_url), "ideas/idea_form.html"
        )

        publish_response = self.client.post(
            self.publish_url,
            {"title": "Campus bikes", "description": "Share bikes between faculties."},
        )
        self.assertRedirects(publish_response, reverse("ideas:home"))
        published_idea = Idea.objects.get()
        self.assertEqual(published_idea.owner, self.student)
        published_ideas = list(Idea.objects.values())

        logout_response = self.client.post(reverse("accounts:logout"))
        self.assertRedirects(logout_response, reverse("ideas:home"))
        self.assertFalse(logout_response.wsgi_request.user.is_authenticated)

        protected_urls = (
            self.publish_url,
            reverse("ideas:edit", args=[published_idea.pk]),
        )
        for url in protected_urls:
            for method in ("GET", "POST"):
                with self.subTest(url=url, method=method):
                    if method == "GET":
                        response = self.client.get(url)
                    else:
                        response = self.client.post(
                            url,
                            {"title": "Blocked idea", "description": "Must not be saved."},
                        )

                    self.assertRedirects(response, f"{self.login_url}?next={url}")
                    self.assertFalse(response.wsgi_request.user.is_authenticated)
                    self.assertEqual(list(Idea.objects.values()), published_ideas)


class AnonymousAccessPolicyTests(TestCase):
    @override_settings(ALLOW_ANONYMOUS_ACCESS=False)
    def test_home_requires_login_when_policy_is_disabled(self):
        response = self.client.get(reverse("ideas:home"))
        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('ideas:home')}",
        )

    @override_settings(ALLOW_ANONYMOUS_ACCESS=False)
    def test_authentication_routes_remain_available(self):
        self.assertEqual(self.client.get(reverse("accounts:login")).status_code, 200)
        self.assertEqual(self.client.get(reverse("accounts:signup")).status_code, 200)

    @override_settings(ALLOW_ANONYMOUS_ACCESS=False)
    def test_authenticated_user_can_access_home(self):
        user = User.objects.create_user(
            email="student@example.com",
            password=AuthenticationFlowTests.password,
            name="Test User",
            role=User.Role.STUDENT,
        )
        self.client.force_login(user)
        self.assertEqual(self.client.get(reverse("ideas:home")).status_code, 200)


class StudentProfileModelTests(TestCase):
    def create_user(self, email, role=User.Role.STUDENT):
        return User.objects.create_user(
            email=email,
            password="A-valid-password-123!",
            name="Profile Test User",
            role=role,
        )

    def test_profile_is_one_to_one_with_user_and_bio_is_optional(self):
        student = self.create_user("profile-student@example.com")
        profile = StudentProfile(user=student, bio="")

        profile.full_clean()
        profile.save()

        self.assertEqual(student.student_profile, profile)
        self.assertEqual(profile.bio, "")
        with self.assertRaises(IntegrityError), transaction.atomic():
            StudentProfile.objects.create(user=student)

    def test_social_media_urls_are_saved_and_can_be_cleared(self):
        urls = {
            "instagram_url": "https://www.instagram.com/example/",
            "twitter_url": "http://twitter.com/example",
            "youtube_url": "https://www.youtube.com/@example",
            "github_url": "https://github.com/example",
        }
        profile = StudentProfile(
            user=self.create_user("social-links@example.com"), **urls
        )

        profile.full_clean()
        profile.save()
        profile.refresh_from_db()

        for field, url in urls.items():
            with self.subTest(field=field):
                self.assertEqual(getattr(profile, field), url)
            setattr(profile, field, "")

        profile.full_clean()
        profile.save()
        profile.refresh_from_db()

        for field in urls:
            with self.subTest(cleared_field=field):
                self.assertEqual(getattr(profile, field), "")

    def test_social_media_urls_are_optional(self):
        profile = StudentProfile(
            user=self.create_user("no-social-links@example.com")
        )

        profile.full_clean()
        profile.save()
        profile.refresh_from_db()

        for field in ("instagram_url", "twitter_url", "youtube_url", "github_url"):
            with self.subTest(field=field):
                self.assertEqual(getattr(profile, field), "")

    def test_social_media_urls_reject_invalid_values(self):
        student = self.create_user("invalid-social-links@example.com")
        for field in ("instagram_url", "twitter_url", "youtube_url", "github_url"):
            for value in (
                "not-a-url",
                "ftp://github.com/example",
                "javascript:alert(1)",
                "https://github.com/" + "a" * 501,
            ):
                with self.subTest(field=field, value=value):
                    profile = StudentProfile(user=student, **{field: value})
                    with self.assertRaises(ValidationError) as context:
                        profile.full_clean()
                    self.assertIn(field, context.exception.message_dict)

    def test_portfolio_and_experience_defaults_are_independent_empty_lists(self):
        first = StudentProfile.objects.create(
            user=self.create_user("profile-first@example.com")
        )
        second = StudentProfile.objects.create(
            user=self.create_user("profile-second@example.com")
        )

        first.portfolio_projects.append({"title": "First project"})
        first.experience.append({"role": "Volunteer"})
        first.save(update_fields=["portfolio_projects", "experience"])
        second.refresh_from_db()

        self.assertEqual(first.portfolio_projects, [{"title": "First project"}])
        self.assertEqual(first.experience, [{"role": "Volunteer"}])
        self.assertEqual(second.portfolio_projects, [])
        self.assertEqual(second.experience, [])

    def test_profile_can_be_associated_with_multiple_skills(self):
        profile = StudentProfile.objects.create(
            user=self.create_user("profile-skills@example.com")
        )
        python = Skill.objects.create(name="Python")
        design = Skill.objects.create(name="Design")

        profile.skills.add(python, design)

        self.assertCountEqual(profile.skills.all(), [python, design])
        self.assertIn(profile, python.profiles.all())

    def test_skill_names_are_unique_ignoring_case(self):
        Skill.objects.create(name="Data Science")

        with self.assertRaises(IntegrityError), transaction.atomic():
            Skill.objects.create(name="data science")

    def test_full_clean_accepts_student_and_rejects_investor_profiles(self):
        student_profile = StudentProfile(
            user=self.create_user("profile-valid-student@example.com")
        )
        student_profile.full_clean()

        investor_profile = StudentProfile(
            user=self.create_user(
                "profile-investor@example.com", role=User.Role.INVESTOR
            )
        )
        # save() does not call full_clean(); role validation is explicit.
        with self.assertRaises(ValidationError) as context:
            investor_profile.full_clean()

        self.assertIn("user", context.exception.error_dict)

    def test_deleting_user_cascades_to_student_profile(self):
        student = self.create_user("profile-delete@example.com")
        profile = StudentProfile.objects.create(user=student)

        student.delete()

        self.assertFalse(StudentProfile.objects.filter(pk=profile.pk).exists())


class StudentProfileFormTests(TestCase):
    def create_user(self, email, role=User.Role.STUDENT):
        return User.objects.create_user(
            email=email,
            password="A-valid-password-123!",
            name="Profile Form User",
            role=role,
        )

    def form_data(self, **overrides):
        data = {
            "bio": "Profile bio",
            "portfolio_projects": '[{"title": "Project"}]',
            "experience": '[{"role": "Volunteer"}]',
        }
        data.update(overrides)
        return data

    def test_form_saves_updates_and_clears_social_media_urls(self):
        urls = {
            "instagram_url": "https://www.instagram.com/example/",
            "twitter_url": "https://twitter.com/example",
            "youtube_url": "https://www.youtube.com/@example",
            "github_url": "https://github.com/example",
        }
        profile = StudentProfile(
            user=self.create_user("form-social-links@example.com")
        )
        for action, values in (
            ("create", urls),
            ("update", {field: url.replace("example", "updated") for field, url in urls.items()}),
            ("clear", {field: "" for field in urls}),
        ):
            with self.subTest(action=action):
                form = StudentProfileForm(self.form_data(**values), instance=profile)
                self.assertTrue(form.is_valid(), form.errors)
                profile = form.save()
                profile.refresh_from_db()
                for field, expected in values.items():
                    self.assertEqual(getattr(profile, field), expected)

    def test_form_accepts_omitted_social_media_urls_for_new_profile(self):
        form = StudentProfileForm(
            self.form_data(),
            instance=StudentProfile(
                user=self.create_user("form-no-social-links@example.com")
            ),
        )
        self.assertTrue(form.is_valid(), form.errors)
        profile = form.save()
        profile.refresh_from_db()

        for field in ("instagram_url", "twitter_url", "youtube_url", "github_url"):
            with self.subTest(field=field):
                self.assertEqual(getattr(profile, field), "")

    def test_form_preserves_existing_social_media_urls_when_omitted(self):
        urls = {
            "instagram_url": "https://www.instagram.com/example/",
            "twitter_url": "https://twitter.com/example",
            "youtube_url": "https://www.youtube.com/@example",
            "github_url": "https://github.com/example",
        }
        profile = StudentProfile.objects.create(
            user=self.create_user("form-keep-social-links@example.com"), **urls
        )
        form = StudentProfileForm(self.form_data(bio="Updated bio"), instance=profile)
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        profile.refresh_from_db()

        self.assertEqual(profile.bio, "Updated bio")
        for field, expected in urls.items():
            with self.subTest(field=field):
                self.assertEqual(getattr(profile, field), expected)

    def test_form_reports_invalid_social_media_urls_on_each_field(self):
        student = self.create_user("form-invalid-social-links@example.com")
        for field in ("instagram_url", "twitter_url", "youtube_url", "github_url"):
            for value in (
                "not-a-url",
                "ftp://github.com/example",
                "javascript:alert(1)",
                "https://github.com/" + "a" * 501,
            ):
                with self.subTest(field=field, value=value):
                    form = StudentProfileForm(
                        self.form_data(**{field: value}),
                        instance=StudentProfile(user=student),
                    )
                    self.assertFalse(form.is_valid())
                    self.assertIn(field, form.errors)

    def test_form_selects_existing_skills_and_excludes_ownership(self):
        student = self.create_user("form-student@example.com")
        skill = Skill.objects.create(name="Python")
        form = StudentProfileForm(
            self.form_data(skills=[str(skill.pk)]),
            instance=StudentProfile(user=student),
        )

        self.assertNotIn("user", form.fields)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(list(form.cleaned_data["skills"]), [skill])

    def test_empty_skill_catalogue_has_no_selectable_skills(self):
        form = StudentProfileForm()

        self.assertEqual(form.fields["skills"].queryset.count(), 0)
        self.assertFalse(form.fields["skills"].required)

    def test_free_text_skill_value_is_rejected(self):
        student = self.create_user("free-text-student@example.com")
        form = StudentProfileForm(
            self.form_data(skills=["Create a new skill"]),
            instance=StudentProfile(user=student),
        )

        self.assertFalse(form.is_valid())
        self.assertIn("skills", form.errors)

    def test_json_fields_normalize_blank_and_omitted_values_to_empty_lists(self):
        student = self.create_user("json-empty-student@example.com")
        for field_name in ("portfolio_projects", "experience"):
            for input_value in ("", None):
                with self.subTest(field=field_name, value=input_value):
                    data = self.form_data()
                    if input_value is None:
                        data.pop(field_name)
                    else:
                        data[field_name] = input_value
                    form = StudentProfileForm(
                        data,
                        instance=StudentProfile(user=student),
                    )
                    self.assertTrue(form.is_valid(), form.errors)
                    self.assertEqual(form.cleaned_data[field_name], [])

    def test_json_fields_accept_empty_arrays_and_arbitrary_list_items(self):
        student = self.create_user("json-list-student@example.com")
        for field_name in ("portfolio_projects", "experience"):
            for raw, expected in (
                ("[]", []),
                ('["text", 3, {"nested": true}, null]', ["text", 3, {"nested": True}, None]),
            ):
                with self.subTest(field=field_name, value=raw):
                    form = StudentProfileForm(
                        self.form_data(**{field_name: raw}),
                        instance=StudentProfile(user=student),
                    )
                    self.assertTrue(form.is_valid(), form.errors)
                    self.assertEqual(form.cleaned_data[field_name], expected)

    def test_json_fields_reject_malformed_and_non_list_values(self):
        student = self.create_user("json-invalid-student@example.com")
        for field_name in ("portfolio_projects", "experience"):
            for raw in ("{broken", "{}", '"text"', "null", "3"):
                with self.subTest(field=field_name, value=raw):
                    form = StudentProfileForm(
                        self.form_data(**{field_name: raw}),
                        instance=StudentProfile(user=student),
                    )
                    self.assertFalse(form.is_valid())
                    self.assertIn(field_name, form.errors)

    def test_form_invokes_student_role_validation(self):
        student = self.create_user("form-role-student@example.com")
        student_form = StudentProfileForm(
            self.form_data(), instance=StudentProfile(user=student)
        )
        self.assertTrue(student_form.is_valid(), student_form.errors)

        investor = self.create_user("form-role-investor@example.com", User.Role.INVESTOR)
        investor_form = StudentProfileForm(
            self.form_data(), instance=StudentProfile(user=investor)
        )
        self.assertFalse(investor_form.is_valid())
        self.assertIn("__all__", investor_form.errors)


class StudentProfileWorkflowTests(TestCase):
    password = "Profile-workflow-123!"

    def create_user(self, email, role=User.Role.STUDENT):
        return User.objects.create_user(
            email=email,
            password=self.password,
            name="Profile Workflow User",
            role=role,
        )

    def valid_data(self, **overrides):
        data = {
            "bio": "A student profile",
            "portfolio_projects": '[{"name": "Prototype"}]',
            "experience": '[{"position": "Volunteer"}]',
        }
        data.update(overrides)
        return data

    def setUp(self):
        self.url = reverse("accounts:student_profile")
        self.student = self.create_user("workflow-student@example.com")
        self.client.force_login(self.student)

    def test_get_does_not_create_profile_and_binds_current_student(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(StudentProfile.objects.count(), 0)
        self.assertEqual(response.context["form"].instance.user, self.student)
        self.assertTemplateUsed(response, "accounts/student_profile_form.html")

    def test_get_retrieves_existing_profile_values_and_skills(self):
        skill = Skill.objects.create(name="Research")
        profile = StudentProfile.objects.create(
            user=self.student,
            bio="Saved bio",
            portfolio_projects=[{"name": "Saved project"}],
            experience=[{"role": "Saved role"}],
        )
        profile.skills.add(skill)

        response = self.client.get(self.url)

        self.assertEqual(response.context["form"].instance.pk, profile.pk)
        self.assertEqual(response.context["form"].initial["bio"], "Saved bio")
        self.assertEqual(
            response.context["form"].initial["portfolio_projects"],
            [{"name": "Saved project"}],
        )
        self.assertEqual(list(response.context["form"].initial["skills"]), [skill])

    def test_post_creates_profile_with_skills_and_json_values(self):
        skill = Skill.objects.create(name="Research")
        response = self.client.post(
            self.url,
            self.valid_data(skills=[str(skill.pk)]),
        )

        self.assertRedirects(response, self.url)
        profile = StudentProfile.objects.get(user=self.student)
        self.assertEqual(profile.portfolio_projects, [{"name": "Prototype"}])
        self.assertEqual(profile.experience, [{"position": "Volunteer"}])
        self.assertCountEqual(profile.skills.all(), [skill])

    def test_editor_post_creates_updates_and_clears_social_media_urls(self):
        urls = {
            "instagram_url": "https://www.instagram.com/example/",
            "twitter_url": "https://twitter.com/example",
            "youtube_url": "https://www.youtube.com/@example",
            "github_url": "https://github.com/example",
        }
        editor_data = {
            "profile_entries_editor": "1",
            "projects-TOTAL_FORMS": "0",
            "projects-INITIAL_FORMS": "0",
            "experience-TOTAL_FORMS": "0",
            "experience-INITIAL_FORMS": "0",
        }
        for action, values in (
            ("create", urls),
            ("update", {field: url.replace("example", "updated") for field, url in urls.items()}),
            ("clear", {field: "" for field in urls}),
        ):
            with self.subTest(action=action):
                response = self.client.post(
                    self.url, self.valid_data(**editor_data, **values)
                )
                self.assertRedirects(response, self.url)
                profile = StudentProfile.objects.get(user=self.student)
                for field, expected in values.items():
                    self.assertEqual(getattr(profile, field), expected)
                self.assertEqual(StudentProfile.objects.filter(user=self.student).count(), 1)

    def test_invalid_social_media_post_preserves_existing_profile(self):
        profile = StudentProfile.objects.create(
            user=self.student,
            bio="Keep this bio",
            github_url="https://github.com/original",
            portfolio_projects=[{"name": "Keep this project"}],
            experience=[{"role": "Keep this role"}],
        )
        for field in ("instagram_url", "twitter_url", "youtube_url", "github_url"):
            with self.subTest(field=field):
                response = self.client.post(
                    self.url,
                    self.valid_data(bio="Should not save", **{field: "not-a-url"}),
                )

                self.assertEqual(response.status_code, 200)
                self.assertIn(field, response.context["form"].errors)
                profile.refresh_from_db()
                self.assertEqual(profile.bio, "Keep this bio")
                self.assertEqual(profile.github_url, "https://github.com/original")
                self.assertEqual(profile.instagram_url, "")
                self.assertEqual(profile.twitter_url, "")
                self.assertEqual(profile.youtube_url, "")
                self.assertEqual(profile.portfolio_projects, [{"name": "Keep this project"}])
                self.assertEqual(profile.experience, [{"role": "Keep this role"}])

    def test_post_updates_existing_profile_in_place(self):
        previous_skill = Skill.objects.create(name="Python")
        updated_skill = Skill.objects.create(name="Research")
        profile = StudentProfile.objects.create(
            user=self.student,
            bio="Old bio",
            portfolio_projects=[{"name": "Old project"}],
            experience=[{"role": "Old role"}],
        )
        profile.skills.add(previous_skill)

        response = self.client.post(
            self.url,
            self.valid_data(
                bio="Updated bio",
                skills=[str(updated_skill.pk)],
                portfolio_projects='[{"name": "Updated project"}]',
                experience='[{"position": "Updated role"}]',
            ),
        )

        self.assertRedirects(response, self.url)
        profile.refresh_from_db()
        self.assertEqual(profile.bio, "Updated bio")
        self.assertEqual(profile.portfolio_projects, [{"name": "Updated project"}])
        self.assertEqual(profile.experience, [{"position": "Updated role"}])
        self.assertCountEqual(profile.skills.all(), [updated_skill])
        self.assertEqual(StudentProfile.objects.filter(user=self.student).count(), 1)

    def test_omitted_optional_fields_clear_existing_values_on_complete_submission(self):
        skill = Skill.objects.create(name="Research")
        profile = StudentProfile.objects.create(
            user=self.student,
            bio="Existing bio",
            portfolio_projects=[{"name": "Existing project"}],
            experience=[{"role": "Existing role"}],
        )
        profile.skills.add(skill)

        response = self.client.post(self.url, {})

        self.assertRedirects(response, self.url)
        profile.refresh_from_db()
        self.assertEqual(profile.bio, "")
        self.assertEqual(profile.portfolio_projects, [])
        self.assertEqual(profile.experience, [])
        self.assertFalse(profile.skills.exists())

    def test_explicit_empty_skill_selection_clears_existing_skills(self):
        skill = Skill.objects.create(name="Research")
        profile = StudentProfile.objects.create(user=self.student)
        profile.skills.add(skill)

        response = self.client.post(self.url, self.valid_data(skills=""))

        self.assertRedirects(response, self.url)
        profile.refresh_from_db()
        self.assertFalse(profile.skills.exists())

    def test_invalid_json_does_not_persist_profile_changes(self):
        original_skill = Skill.objects.create(name="Python")
        different_skill = Skill.objects.create(name="Research")
        profile = StudentProfile.objects.create(
            user=self.student,
            bio="Keep this bio",
            portfolio_projects=[{"name": "Keep this project"}],
            experience=[{"role": "Keep this role"}],
        )
        profile.skills.add(original_skill)

        response = self.client.post(
            self.url,
            self.valid_data(
                bio="Should not save",
                skills=[str(different_skill.pk)],
                portfolio_projects="{}",
            ),
        )

        self.assertEqual(response.status_code, 200)
        profile.refresh_from_db()
        self.assertEqual(profile.bio, "Keep this bio")
        self.assertEqual(profile.portfolio_projects, [{"name": "Keep this project"}])
        self.assertCountEqual(profile.skills.all(), [original_skill])

    def test_other_http_methods_are_rejected(self):
        self.assertEqual(self.client.put(self.url).status_code, 405)

    def test_anonymous_user_is_redirected_to_login(self):
        self.client.logout()

        response = self.client.get(self.url)

        self.assertRedirects(response, f"{reverse('accounts:login')}?next={self.url}")

    def test_investor_is_denied(self):
        investor = self.create_user("workflow-investor@example.com", User.Role.INVESTOR)
        self.client.force_login(investor)

        self.assertEqual(self.client.get(self.url).status_code, 403)
        self.assertEqual(self.client.post(self.url, {}).status_code, 403)

    def test_submitted_owner_or_profile_identifiers_cannot_target_another_student(self):
        other_student = self.create_user("workflow-other@example.com")
        other_profile = StudentProfile.objects.create(
            user=other_student,
            bio="Other student's data",
            portfolio_projects=[{"name": "Other project"}],
            experience=[],
        )

        response = self.client.post(
            self.url,
            self.valid_data(
                user=str(other_student.pk),
                profile=str(other_profile.pk),
                bio="My own data",
            ),
        )

        self.assertRedirects(response, self.url)
        other_profile.refresh_from_db()
        self.assertEqual(other_profile.bio, "Other student's data")
        self.assertEqual(StudentProfile.objects.count(), 2)
        self.assertEqual(StudentProfile.objects.get(user=self.student).bio, "My own data")


class CollaboratorProfileTestData:
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.owner = User.objects.create_user(
            email="collaborator-profile-owner@example.com",
            name="Project Owner",
            role=User.Role.STUDENT,
        )
        cls.student = User.objects.create_user(
            email="collaborator-profile-student@example.com",
            name="Potential Collaborator",
            role=User.Role.STUDENT,
        )
        cls.investor = User.objects.create_user(
            email="collaborator-profile-investor@example.com",
            name="Test Investor",
            role=User.Role.INVESTOR,
        )
        cls.idea = Idea.objects.create(
            title="Owner's campus project",
            description="A project seeking collaborators.",
            owner=cls.owner,
        )
        cls.foreign_idea = Idea.objects.create(
            title="Another student's project",
            description="A project belonging to the profile owner.",
            owner=cls.student,
        )
        cls.profile = StudentProfile.objects.create(
            user=cls.student,
            bio="I build accessible student tools.",
            portfolio_projects=[{"title": "Campus route planner"}],
            experience=[{"role": "Volunteer developer"}],
        )
        cls.profile.skills.add(Skill.objects.create(name="Collaboration Python"))

    def setUp(self):
        super().setUp()
        self.url = reverse("accounts:collaborator_profile", args=[self.student.pk])
        self.client.force_login(self.owner)


class CollaboratorProfileAccessTests(CollaboratorProfileTestData, TestCase):
    def test_student_can_read_another_profile_with_owner_scoped_request_context(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/student_profile_detail.html")
        for value in (
            self.student.name, self.profile.bio, "Collaboration Python",
            "Campus route planner", "Volunteer developer",
        ):
            self.assertContains(response, value)
        self.assertNotContains(response, self.student.email)
        self.assertNotContains(response, "Edit profile")
        self.assertNotContains(response, "Profile visits")
        self.assertFalse(response.context["is_own_profile"])
        self.assertTrue(response.context["has_owned_ideas"])
        self.assertEqual(
            list(response.context["collaborator_request_form"].fields["idea"].queryset),
            [self.idea],
        )
        self.assertFalse(ProfileVisit.objects.exists())
        self.assertFalse(Follow.objects.exists())
        self.assertFalse(CollaboratorRequest.objects.exists())
        self.assertFalse(Collaborator.objects.exists())

    def test_anonymous_visitor_is_asked_to_sign_in(self):
        self.client.logout()

        self.assertRedirects(
            self.client.get(self.url), f"{reverse('accounts:login')}?next={self.url}"
        )
        self.assertFalse(ProfileVisit.objects.exists())

    def test_investor_cannot_open_the_student_collaboration_route(self):
        self.client.force_login(self.investor)

        self.assertEqual(self.client.get(self.url).status_code, 403)
        self.assertFalse(ProfileVisit.objects.exists())

    def test_own_profile_redirects_to_the_existing_owner_view(self):
        own_url = reverse("accounts:collaborator_profile", args=[self.owner.pk])

        self.assertRedirects(self.client.get(own_url), reverse("accounts:my_profile"))
        self.assertFalse(ProfileVisit.objects.exists())

    def test_nonstudent_inactive_and_missing_targets_are_not_found(self):
        inactive = User.objects.create_user(
            email="collaborator-profile-inactive@example.com",
            name="Inactive Student",
            role=User.Role.STUDENT,
            is_active=False,
        )
        for student_id in (self.investor.pk, inactive.pk, inactive.pk + 100):
            with self.subTest(student_id=student_id):
                url = reverse("accounts:collaborator_profile", args=[student_id])
                self.assertEqual(self.client.get(url).status_code, 404)
        self.assertFalse(ProfileVisit.objects.exists())

    def test_student_without_saved_profile_uses_the_existing_empty_state(self):
        self.profile.delete()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This student has not added profile information yet.")
        self.assertIsNone(response.context["profile"])
        self.assertFalse(StudentProfile.objects.filter(user=self.student).exists())

    def test_viewer_without_projects_has_empty_request_choices(self):
        viewer = User.objects.create_user(
            email="collaborator-profile-no-projects@example.com",
            name="Student Without Projects",
            role=User.Role.STUDENT,
        )
        self.client.force_login(viewer)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["has_owned_ideas"])
        self.assertFalse(
            response.context["collaborator_request_form"].fields["idea"].queryset.exists()
        )

    def test_non_get_requests_cannot_edit_the_other_students_profile(self):
        for method in ("POST", "PUT", "PATCH", "DELETE"):
            with self.subTest(method=method):
                response = self.client.generic(method, self.url, data="bio=Changed")
                self.assertEqual(response.status_code, 405)

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.bio, "I build accessible student tools.")
        self.assertFalse(ProfileVisit.objects.exists())
        self.assertFalse(CollaboratorRequest.objects.exists())

    def test_shared_context_keeps_a_bound_request_form_and_its_error(self):
        form = CollaboratorRequestForm({"idea": self.idea.pk}, owner=self.owner)
        self.assertTrue(form.is_valid(), form.errors)
        form.add_error(None, "A request already exists.")

        context = collaborator_profile_context(self.owner, self.student, form=form)

        self.assertIs(context["collaborator_request_form"], form)
        self.assertEqual(form.cleaned_data["idea"], self.idea)
        self.assertIn("A request already exists.", form.non_field_errors())
        self.assertEqual(context["profile"], self.profile)
        self.assertTrue(context["has_owned_ideas"])


class CollaboratorProfilePresentationTests(CollaboratorProfileTestData, TestCase):
    def request_form_html(self, response):
        match = re.search(
            r'<form\b[^>]*id="collaborator-request-form"[^>]*>.*?</form>',
            response.content.decode(),
            re.DOTALL,
        )
        self.assertIsNotNone(match)
        return match.group(0)

    def test_form_has_own_project_choices_label_help_csrf_and_post_action(self):
        response = self.client.get(self.url)
        form_html = self.request_form_html(response)
        action = reverse("ideas:send_collaborator_request", args=[self.student.pk])

        self.assertIn(f'action="{action}"', form_html)
        self.assertIn('method="post"', form_html)
        self.assertRegex(form_html, r'name="csrfmiddlewaretoken" value="[^"]+"')
        self.assertInHTML(
            '<label class="form-label" for="id_idea">Your project</label>', form_html
        )
        self.assertIn('id="id_idea_helptext"', form_html)
        self.assertIn('aria-describedby="id_idea_helptext"', form_html)
        self.assertInHTML(
            f'<option value="{self.idea.pk}">{self.idea.title}</option>', form_html
        )
        self.assertNotIn(f'value="{self.foreign_idea.pk}"', form_html)
        self.assertInHTML(
            '<button type="submit" class="btn btn-primary">Request Collaborator</button>',
            form_html,
        )
        for field in ("sender", "receiver", "status"):
            self.assertNotIn(f'name="{field}"', form_html)

    def test_missing_selection_error_is_visible_and_associated_with_the_selector(self):
        action = reverse("ideas:send_collaborator_request", args=[self.student.pk])
        response = self.client.post(action, {"idea": ""})
        form_html = self.request_form_html(response)
        select = re.search(r'<select\b[^>]*>', form_html).group(0)

        self.assertContains(response, "Please select one of your published projects.")
        self.assertIn('aria-invalid="true"', select)
        self.assertIn("id_idea_helptext", select)
        self.assertIn("id_idea_error", select)
        self.assertIn('id="id_idea_error"', form_html)
        self.assertIn('role="alert"', form_html)
        self.assertFalse(CollaboratorRequest.objects.exists())

    def test_duplicate_error_is_visible_and_keeps_the_selected_project(self):
        original = CollaboratorRequest.objects.create(
            idea=self.idea,
            sender=self.owner,
            receiver=self.student,
            status=CollaboratorRequest.Status.REJECTED,
        )
        action = reverse("ideas:send_collaborator_request", args=[self.student.pk])

        response = self.client.post(action, {"idea": self.idea.pk})

        self.assertContains(
            response,
            "You have already sent a collaborator request to this student for this project.",
        )
        self.assertIn(
            f'value="{self.idea.pk}" selected', self.request_form_html(response)
        )
        original.refresh_from_db()
        self.assertEqual(original.status, CollaboratorRequest.Status.REJECTED)
        self.assertEqual(CollaboratorRequest.objects.count(), 1)

    def test_student_without_projects_sees_publish_prompt_without_request_form(self):
        self.idea.delete()

        response = self.client.get(self.url)

        self.assertContains(response, "Publish an idea before sending a collaborator request.")
        self.assertContains(response, f'href="{reverse("ideas:publish")}"')
        self.assertNotContains(response, 'id="collaborator-request-form"')
        self.assertNotContains(response, 'name="idea"')

    def test_own_profile_has_no_invitation_controls(self):
        response = self.client.get(reverse("accounts:my_profile"))

        self.assertNotContains(response, "Request Collaborator")
        self.assertNotContains(response, 'id="collaborator-request-form"')

    def test_investor_profile_keeps_follow_action_without_invitation_controls(self):
        self.client.force_login(self.investor)

        response = self.client.get(
            reverse("accounts:investor_profile", args=[self.student.pk])
        )

        self.assertNotContains(response, "Request Collaborator")
        self.assertNotContains(response, 'id="collaborator-request-form"')
        self.assertContains(
            response,
            f'action="{reverse("accounts:follow_student", args=[self.student.pk])}"',
        )

    def test_incomplete_target_profile_still_allows_a_project_invitation(self):
        self.profile.delete()

        response = self.client.get(self.url)

        self.assertContains(response, "This student has not added profile information yet.")
        self.assertIn('name="idea"', self.request_form_html(response))
        self.assertContains(response, "Request Collaborator")


class StudentProfilePresentationTests(TestCase):
    password = "Profile-presentation-123!"

    def create_user(self, email, role):
        return User.objects.create_user(
            email=email,
            password=self.password,
            name=f"{role.title()} Profile User",
            role=role,
        )

    def setUp(self):
        self.student = self.create_user("presentation-student@example.com", User.Role.STUDENT)
        self.investor = self.create_user("presentation-investor@example.com", User.Role.INVESTOR)
        self.own_profile_url = reverse("accounts:my_profile")
        self.edit_url = reverse("accounts:student_profile")
        self.investor_profile_url = reverse(
            "accounts:investor_profile", args=[self.student.pk]
        )

    def test_student_can_view_own_profile_and_follow_edit_link(self):
        skill = Skill.objects.create(name="Visual design")
        profile = StudentProfile.objects.create(
            user=self.student,
            bio="I design accessible tools.",
            portfolio_projects=[{"title": "Route planner"}],
            experience=[{"role": "Volunteer designer"}],
        )
        profile.skills.add(skill)
        self.client.force_login(self.student)

        response = self.client.get(self.own_profile_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/student_profile_detail.html")
        self.assertContains(response, "I design accessible tools.")
        self.assertContains(response, "Visual design")
        self.assertContains(response, "Route planner")
        self.assertContains(response, "Volunteer designer")
        self.assertContains(response, self.edit_url)
        self.assertNotContains(response, self.student.email)

    def test_student_without_profile_sees_state_and_creation_link(self):
        self.client.force_login(self.student)

        response = self.client.get(self.own_profile_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You have not added profile information yet.")
        self.assertContains(response, "Create your profile")

    def test_editor_uses_styled_project_and_experience_fields(self):
        self.client.force_login(self.student)

        response = self.client.get(self.edit_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="form-surface"')
        self.assertContains(response, 'for="id_bio"')
        self.assertContains(response, "Project title")
        self.assertContains(response, "Role")
        self.assertNotContains(response, "Enter a JSON array")
        self.assertNotContains(response, 'name="portfolio_projects"')
        self.assertNotContains(response, 'name="experience"')
        self.assertContains(response, "No skills are available to select yet.")
        self.assertContains(response, self.own_profile_url)
        for platform in ("instagram", "twitter", "youtube", "github"):
            with self.subTest(platform=platform):
                self.assertContains(response, f'name="{platform}_url"')
                self.assertContains(response, f'for="id_{platform}_url"')

    def test_editor_displays_social_url_errors_and_preserves_entered_values(self):
        self.client.force_login(self.student)
        response = self.client.post(
            self.edit_url,
            {
                "profile_entries_editor": "1",
                "projects-TOTAL_FORMS": "0",
                "projects-INITIAL_FORMS": "0",
                "experience-TOTAL_FORMS": "0",
                "experience-INITIAL_FORMS": "0",
                "github_url": "not-a-url",
                "instagram_url": "https://www.instagram.com/example/",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="id_github_url_error"')
        self.assertContains(response, "Enter a valid URL.")
        self.assertContains(response, 'value="not-a-url"')
        self.assertContains(response, 'value="https://www.instagram.com/example/"')
        self.assertFalse(StudentProfile.objects.filter(user=self.student).exists())

    def test_owner_and_investor_see_clickable_social_icons(self):
        urls = {
            "instagram": "https://www.instagram.com/example/",
            "twitter": "https://twitter.com/example",
            "youtube": "https://www.youtube.com/@example",
            "github": "https://github.com/example",
        }
        StudentProfile.objects.create(
            user=self.student,
            **{f"{platform}_url": url for platform, url in urls.items()},
        )

        for viewer, page in (
            (self.student, self.own_profile_url),
            (self.investor, self.investor_profile_url),
        ):
            with self.subTest(viewer=viewer.role):
                self.client.force_login(viewer)
                response = self.client.get(page)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'id="profile-social-title"')
                self.assertContains(response, 'target="_blank" rel="noopener noreferrer"', count=4)
                for platform, url in urls.items():
                    self.assertContains(response, f'href="{url}"')
                    self.assertContains(response, f'data-social-icon="{platform}"')

    def test_profile_only_displays_filled_social_icons_and_hides_empty_section(self):
        profile = StudentProfile.objects.create(
            user=self.student, github_url="https://github.com/example"
        )
        self.client.force_login(self.investor)

        response = self.client.get(self.investor_profile_url)
        self.assertContains(response, 'data-social-icon="github"')
        for platform in ("instagram", "twitter", "youtube"):
            self.assertNotContains(response, f'data-social-icon="{platform}"')

        profile.github_url = ""
        profile.save()
        response = self.client.get(self.investor_profile_url)
        self.assertNotContains(response, 'id="profile-social-title"')
        self.assertNotContains(response, "data-social-icon=")

    def test_profile_does_not_render_invalid_urls_stored_outside_the_form(self):
        StudentProfile.objects.create(
            user=self.student,
            bio="A visible bio",
            instagram_url="not-a-url",
            twitter_url="javascript:alert(1)",
            youtube_url="data:text/html,test",
            github_url="ftp://github.com/example",
        )
        self.client.force_login(self.investor)

        response = self.client.get(self.investor_profile_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A visible bio")
        self.assertNotContains(response, 'id="profile-social-title"')
        self.assertNotContains(response, "data-social-icon=")
        self.assertNotContains(response, "javascript:")

    def test_my_profile_navigation_is_student_only(self):
        home_url = reverse("ideas:home")
        self.client.force_login(self.student)
        student_response = self.client.get(home_url)
        self.assertContains(student_response, self.own_profile_url)

        self.client.force_login(self.investor)
        investor_response = self.client.get(home_url)
        self.assertNotContains(investor_response, self.own_profile_url)

        self.client.logout()
        anonymous_response = self.client.get(home_url)
        self.assertNotContains(anonymous_response, self.own_profile_url)

    def test_invalid_editor_submission_shows_validation_errors(self):
        self.client.force_login(self.student)

        response = self.client.post(
            self.edit_url,
            {
                "bio": "Updated bio",
                "skills": [],
                "portfolio_projects": "{invalid",
                "experience": "[]",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Enter a valid JSON.")
        self.assertFalse(StudentProfile.objects.filter(user=self.student).exists())

    def test_investor_can_view_student_profile_without_private_or_edit_controls(self):
        skill = Skill.objects.create(name="User research")
        profile = StudentProfile.objects.create(
            user=self.student,
            bio="Profile for investors.",
            portfolio_projects=[{"title": "Research prototype"}],
            experience=[{"role": "Lab assistant"}],
        )
        profile.skills.add(skill)
        self.client.force_login(self.investor)

        response = self.client.get(self.investor_profile_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.student.name)
        self.assertContains(response, "Profile for investors.")
        self.assertContains(response, "User research")
        self.assertContains(response, "Research prototype")
        self.assertContains(response, "Lab assistant")
        self.assertNotContains(response, self.student.email)
        self.assertNotContains(response, self.edit_url)

    def test_incomplete_and_absent_profiles_render_empty_states(self):
        self.client.force_login(self.investor)

        no_profile_response = self.client.get(self.investor_profile_url)
        self.assertEqual(no_profile_response.status_code, 200)
        self.assertContains(
            no_profile_response,
            "This student has not added profile information yet.",
        )

        empty_profile = StudentProfile.objects.create(user=self.student)
        empty_profile_response = self.client.get(self.investor_profile_url)
        self.assertEqual(empty_profile_response.status_code, 200)
        self.assertContains(empty_profile_response, "No bio added yet.")
        self.assertContains(empty_profile_response, "No skills added yet.")
        self.assertContains(empty_profile_response, "No projects added yet.")
        self.assertContains(empty_profile_response, "No experience added yet.")

    def test_anonymous_users_are_redirected_from_both_profile_views(self):
        for url in (self.own_profile_url, self.investor_profile_url):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(
                    response,
                    f"{reverse('accounts:login')}?next={url}",
                )

    def test_investors_cannot_open_student_edit_or_own_profile_views(self):
        self.client.force_login(self.investor)

        self.assertEqual(self.client.get(self.edit_url).status_code, 403)
        self.assertEqual(self.client.get(self.own_profile_url).status_code, 403)

    def test_students_cannot_open_investor_profile_route(self):
        self.client.force_login(self.student)

        self.assertEqual(self.client.get(self.investor_profile_url).status_code, 403)

    def test_investor_route_does_not_resolve_investors_or_unknown_users(self):
        self.client.force_login(self.investor)

        investor_url = reverse("accounts:investor_profile", args=[self.investor.pk])
        missing_url = reverse("accounts:investor_profile", args=[999999])
        self.assertEqual(self.client.get(investor_url).status_code, 404)
        self.assertEqual(self.client.get(missing_url).status_code, 404)


class FollowingTestDataMixin:
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.student = User.objects.create_user(
            email="follow-student@example.com", name="Student One", role=User.Role.STUDENT
        )
        cls.other_student = User.objects.create_user(
            email="follow-other-student@example.com", name="Student Two", role=User.Role.STUDENT
        )
        cls.investor = User.objects.create_user(
            email="follow-investor@example.com", name="Investor One", role=User.Role.INVESTOR
        )
        cls.other_investor = User.objects.create_user(
            email="follow-other-investor@example.com", name="Investor Two", role=User.Role.INVESTOR
        )


class FollowModelTests(FollowingTestDataMixin, TestCase):
    def test_follow_accepts_valid_roles_without_requiring_profile_details(self):
        follow = Follow(investor=self.investor, student=self.student)
        follow.full_clean()
        follow.save()

        self.assertIsNotNone(follow.created_at)
        self.assertFalse(StudentProfile.objects.filter(user=self.student).exists())

    def test_database_rejects_duplicate_pairs_and_self_following(self):
        Follow.objects.create(investor=self.investor, student=self.student)

        for student in (self.student, self.investor):
            with self.subTest(student=student.pk):
                with self.assertRaises(IntegrityError), transaction.atomic():
                    Follow.objects.create(investor=self.investor, student=student)

    def test_validation_rejects_wrong_investor_and_student_roles(self):
        for investor, student, field in (
            (self.student, self.other_student, "investor"),
            (self.investor, self.other_investor, "student"),
        ):
            with self.subTest(field=field):
                with self.assertRaises(ValidationError) as error:
                    Follow(investor=investor, student=student).full_clean()
                self.assertIn(field, error.exception.message_dict)

    def test_deleting_accounts_removes_only_their_relationships(self):
        for investor in (self.investor, self.other_investor):
            for student in (self.student, self.other_student):
                Follow.objects.create(investor=investor, student=student)

        self.student.delete()
        self.assertEqual(Follow.objects.count(), 2)
        self.investor.delete()
        remaining = Follow.objects.get()
        self.assertEqual(remaining.investor, self.other_investor)
        self.assertEqual(remaining.student, self.other_student)


class FollowActionTests(FollowingTestDataMixin, TestCase):
    def setUp(self):
        self.profile_url = reverse("accounts:investor_profile", args=[self.student.pk])
        self.follow_url = reverse("accounts:follow_student", args=[self.student.pk])
        self.unfollow_url = reverse("accounts:unfollow_student", args=[self.student.pk])

    def test_follow_uses_session_investor_and_route_student(self):
        self.client.force_login(self.investor)
        response = self.client.post(
            self.follow_url,
            {"investor_id": self.other_investor.pk, "student_id": self.other_student.pk},
        )

        self.assertRedirects(response, self.profile_url)
        follow = Follow.objects.get()
        self.assertEqual(follow.investor, self.investor)
        self.assertEqual(follow.student, self.student)

    def test_repeated_follow_keeps_one_relationship(self):
        self.client.force_login(self.investor)
        for _ in range(2):
            self.assertRedirects(self.client.post(self.follow_url), self.profile_url)
        self.assertEqual(Follow.objects.count(), 1)

    def test_repeated_unfollow_removes_only_current_investors_relationship(self):
        Follow.objects.create(investor=self.investor, student=self.student)
        other_follow = Follow.objects.create(investor=self.other_investor, student=self.student)
        self.client.force_login(self.investor)

        for _ in range(2):
            response = self.client.post(self.unfollow_url, {"investor_id": self.other_investor.pk})
            self.assertRedirects(response, self.profile_url)
        self.assertEqual(list(Follow.objects.all()), [other_follow])

    def test_investor_and_missing_targets_are_rejected(self):
        self.client.force_login(self.investor)
        for action in ("follow_student", "unfollow_student"):
            for target in (self.other_investor.pk, 999999):
                with self.subTest(action=action, target=target):
                    response = self.client.post(reverse(f"accounts:{action}", args=[target]))
                    self.assertEqual(response.status_code, 404)
        self.assertFalse(Follow.objects.exists())

    def test_anonymous_users_are_asked_to_sign_in(self):
        for url in (self.follow_url, self.unfollow_url):
            with self.subTest(url=url):
                response = self.client.post(url)
                self.assertRedirects(response, f"{reverse('accounts:login')}?next={url}")
        self.assertFalse(Follow.objects.exists())

    def test_students_cannot_follow_or_unfollow(self):
        existing = Follow.objects.create(investor=self.investor, student=self.other_student)
        self.client.force_login(self.student)
        for url in (self.follow_url, self.unfollow_url):
            with self.subTest(url=url):
                self.assertEqual(self.client.post(url).status_code, 403)
        self.assertEqual(list(Follow.objects.all()), [existing])

    def test_actions_reject_non_post_methods_without_changing_data(self):
        existing = Follow.objects.create(investor=self.investor, student=self.student)
        self.client.force_login(self.investor)
        for url in (self.follow_url, self.unfollow_url):
            for method in ("GET", "PUT", "DELETE"):
                with self.subTest(url=url, method=method):
                    self.assertEqual(self.client.generic(method, url).status_code, 405)
        self.assertEqual(list(Follow.objects.all()), [existing])

    def test_actions_require_csrf_tokens(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.investor)
        for url in (self.follow_url, self.unfollow_url):
            with self.subTest(url=url):
                self.assertEqual(client.post(url).status_code, 403)
        self.assertFalse(Follow.objects.exists())

    def test_submitted_redirect_urls_are_ignored(self):
        self.client.force_login(self.investor)
        for url in (self.follow_url, self.unfollow_url):
            with self.subTest(url=url):
                response = self.client.post(url, {"next": "https://example.com/", "source": "//example.com/"})
                self.assertRedirects(response, self.profile_url)


class FollowProfilePresentationTests(FollowingTestDataMixin, TestCase):
    def setUp(self):
        self.profile_url = reverse("accounts:investor_profile", args=[self.student.pk])
        self.follow_url = reverse("accounts:follow_student", args=[self.student.pk])
        self.unfollow_url = reverse("accounts:unfollow_student", args=[self.student.pk])

    def test_incomplete_profile_offers_follow_without_creating_data(self):
        self.client.force_login(self.investor)
        response = self.client.get(self.profile_url)

        self.assertContains(response, f'action="{self.follow_url}"')
        self.assertContains(response, "csrfmiddlewaretoken")
        self.assertNotContains(response, f'action="{self.unfollow_url}"')
        self.assertContains(response, "This student has not added profile information yet.")
        self.assertFalse(Follow.objects.exists())
        self.assertFalse(StudentProfile.objects.exists())

    def test_follow_control_reflects_only_the_current_investors_state(self):
        Follow.objects.create(investor=self.investor, student=self.student)
        self.client.force_login(self.investor)
        response = self.client.get(self.profile_url)
        self.assertContains(response, f'action="{self.unfollow_url}"')
        self.assertNotContains(response, f'action="{self.follow_url}"')

        self.client.force_login(self.other_investor)
        other_response = self.client.get(self.profile_url)
        self.assertContains(other_response, f'action="{self.follow_url}"')
        self.assertNotContains(other_response, f'action="{self.unfollow_url}"')

    def test_students_own_profiles_have_no_follow_controls(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse("accounts:my_profile"))
        self.assertNotContains(response, self.follow_url)
        self.assertNotContains(response, self.unfollow_url)

    def test_profile_forms_support_follow_and_unfollow_with_csrf_enforced(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.investor)
        client.get(self.profile_url)
        token = client.cookies["csrftoken"].value

        followed = client.post(self.follow_url, {"csrfmiddlewaretoken": token})
        self.assertRedirects(followed, self.profile_url)
        self.assertTrue(Follow.objects.filter(investor=self.investor, student=self.student).exists())

        unfollowed = client.post(self.unfollow_url, {"csrfmiddlewaretoken": token})
        self.assertRedirects(unfollowed, self.profile_url)
        self.assertFalse(Follow.objects.exists())


class FollowingListTests(FollowingTestDataMixin, TestCase):
    def setUp(self):
        self.list_url = reverse("accounts:following")

    def test_list_shows_only_current_investors_followed_students_and_profile_links(self):
        Follow.objects.create(investor=self.investor, student=self.student)
        Follow.objects.create(investor=self.other_investor, student=self.other_student)
        self.client.force_login(self.investor)

        response = self.client.get(self.list_url)

        self.assertContains(response, self.student.name)
        self.assertNotContains(response, self.other_student.name)
        self.assertContains(response, reverse("accounts:investor_profile", args=[self.student.pk]))
        self.assertNotContains(response, self.student.email)

    def test_list_displays_available_bio_and_skills_and_escapes_profile_content(self):
        profile = StudentProfile.objects.create(user=self.student, bio="<script>unsafe()</script> Robotics researcher.")
        profile.skills.add(Skill.objects.create(name="Robotics"))
        Follow.objects.create(investor=self.investor, student=self.student)
        self.client.force_login(self.investor)

        response = self.client.get(self.list_url)

        self.assertContains(response, "Robotics researcher.")
        self.assertContains(response, "Robotics")
        self.assertContains(response, "&lt;script&gt;")
        self.assertNotContains(response, "<script>unsafe()")

    def test_list_handles_missing_and_empty_profiles(self):
        StudentProfile.objects.create(user=self.other_student)
        for student in (self.student, self.other_student):
            Follow.objects.create(investor=self.investor, student=student)
        self.client.force_login(self.investor)

        response = self.client.get(self.list_url)

        self.assertContains(response, "This student is still building their profile.", count=2)
        self.assertContains(response, self.student.name)
        self.assertContains(response, self.other_student.name)

    def test_empty_list_explains_how_to_follow_and_links_to_ideas(self):
        self.client.force_login(self.investor)
        response = self.client.get(self.list_url)
        self.assertContains(response, "You're not following any students yet.")
        self.assertContains(response, 'href="' + reverse("ideas:home") + '"')
        self.assertFalse(Follow.objects.exists())

    def test_list_order_is_latest_follow_first_with_stable_ties(self):
        first = Follow.objects.create(investor=self.investor, student=self.student)
        second = Follow.objects.create(investor=self.investor, student=self.other_student)
        Follow.objects.update(created_at=timezone.now())
        self.client.force_login(self.investor)

        response = self.client.get(self.list_url)

        self.assertEqual(list(response.context["follows"]), [second, first])

    def test_following_page_requires_an_investor_session_and_get(self):
        self.assertRedirects(
            self.client.get(self.list_url), f"{reverse('accounts:login')}?next={self.list_url}"
        )
        self.client.force_login(self.student)
        self.assertEqual(self.client.get(self.list_url).status_code, 403)
        self.client.force_login(self.investor)
        self.assertEqual(self.client.post(self.list_url).status_code, 405)

    def test_following_navigation_is_investor_only(self):
        home_url = reverse("ideas:home")
        self.assertNotContains(self.client.get(home_url), self.list_url)
        self.client.force_login(self.student)
        self.assertNotContains(self.client.get(home_url), self.list_url)
        self.client.force_login(self.investor)
        self.assertContains(self.client.get(home_url), self.list_url)

    def test_accounts_that_are_no_longer_students_are_not_listed(self):
        Follow.objects.create(investor=self.investor, student=self.student)
        self.student.role = User.Role.INVESTOR
        self.student.save(update_fields=["role"])
        self.client.force_login(self.investor)

        response = self.client.get(self.list_url)

        self.assertContains(response, "You're not following any students yet.")
        self.assertNotContains(response, reverse("accounts:investor_profile", args=[self.student.pk]))


class FollowingAcceptanceTests(FollowingTestDataMixin, TestCase):
    def test_investor_follows_lists_and_unfollows_from_student_profile(self):
        idea = Idea.objects.create(owner=self.student, title="A student project", description="A project to explore.")
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.investor)
        profile_url = reverse("accounts:investor_profile", args=[self.student.pk])
        follow_url = reverse("accounts:follow_student", args=[self.student.pk])
        unfollow_url = reverse("accounts:unfollow_student", args=[self.student.pk])
        list_url = reverse("accounts:following")

        detail = client.get(reverse("ideas:detail", args=[idea.pk]))
        self.assertContains(detail, profile_url)
        profile = client.get(profile_url)
        self.assertContains(profile, f'action="{follow_url}"')
        token = client.cookies["csrftoken"].value

        followed = client.post(follow_url, {"csrfmiddlewaretoken": token}, follow=True)
        self.assertContains(followed, f'action="{unfollow_url}"')
        listed = client.get(list_url)
        self.assertContains(listed, self.student.name)
        self.assertContains(listed, profile_url)

        unfollowed = client.post(unfollow_url, {"csrfmiddlewaretoken": token}, follow=True)
        self.assertContains(unfollowed, f'action="{follow_url}"')
        self.assertContains(client.get(list_url), "You're not following any students yet.")
        self.assertFalse(Follow.objects.exists())

    def test_unfollow_from_list_updates_collection_and_preserves_other_investors(self):
        for student in (self.student, self.other_student):
            Follow.objects.create(investor=self.investor, student=student)
        other_follow = Follow.objects.create(investor=self.other_investor, student=self.student)
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.investor)
        list_url = reverse("accounts:following")
        client.get(list_url)
        token = client.cookies["csrftoken"].value

        response = client.post(
            reverse("accounts:unfollow_student", args=[self.student.pk]),
            {"source": "following", "csrfmiddlewaretoken": token},
            follow=True,
        )
        self.assertRedirects(response, list_url)
        self.assertEqual([follow.student for follow in response.context["follows"]], [self.other_student])
        self.assertNotContains(response, reverse("accounts:investor_profile", args=[self.student.pk]))
        self.assertTrue(Follow.objects.filter(pk=other_follow.pk).exists())

        empty = client.post(
            reverse("accounts:unfollow_student", args=[self.other_student.pk]),
            {"source": "following", "csrfmiddlewaretoken": token},
            follow=True,
        )
        self.assertRedirects(empty, list_url)
        self.assertContains(empty, "You're not following any students yet.")
        self.assertEqual(list(Follow.objects.all()), [other_follow])

    def test_following_and_profile_visits_work_together(self):
        StudentProfile.objects.create(
            user=self.student,
            portfolio_projects=[{"title": "Campus energy dashboard"}],
        )
        self.client.force_login(self.investor)
        profile_url = reverse("accounts:investor_profile", args=[self.student.pk])
        follow_url = reverse("accounts:follow_student", args=[self.student.pk])
        unfollow_url = reverse("accounts:unfollow_student", args=[self.student.pk])

        profile = self.client.get(profile_url)
        self.assertContains(profile, "Campus energy dashboard")
        self.assertContains(profile, f'action="{follow_url}"')

        self.assertRedirects(
            self.client.post(follow_url), profile_url, fetch_redirect_response=False
        )
        self.assertContains(self.client.get(reverse("accounts:following")), profile_url)
        self.assertEqual(self.student.profile_visits.count(), 1)

        followed_profile = self.client.get(profile_url)
        self.assertContains(followed_profile, f'action="{unfollow_url}"')
        self.assertNotContains(followed_profile, "Profile visits")
        self.assertEqual(self.student.profile_visits.count(), 2)
        self.assertTrue(Follow.objects.filter(investor=self.investor, student=self.student).exists())

        self.client.post(unfollow_url, {"source": "following"})
        self.assertFalse(Follow.objects.filter(investor=self.investor, student=self.student).exists())
        self.assertEqual(self.student.profile_visits.count(), 2)

        self.client.force_login(self.student)
        own_profile = self.client.get(reverse("accounts:my_profile"))
        self.assertContains(own_profile, "Investors have visited your profile 2 times.")
        self.assertContains(own_profile, "Campus energy dashboard")


class ReadableProfileEntryTests(FollowingTestDataMixin, TestCase):
    def test_project_and_experience_are_readable_for_owner_and_investor(self):
        StudentProfile.objects.create(
            user=self.student,
            portfolio_projects=[{"title": "Campus energy dashboard", "description": "Measure campus energy use."}],
            experience=[{"role": "Student researcher", "company": "UPM", "period": "2025–2026"}],
        )
        for user, url in (
            (self.student, reverse("accounts:my_profile")),
            (self.investor, reverse("accounts:investor_profile", args=[self.student.pk])),
        ):
            with self.subTest(user=user.pk):
                self.client.force_login(user)
                response = self.client.get(url)
                for content in ("Campus energy dashboard", "Measure campus energy use.", "Student researcher", "UPM", "2025–2026"):
                    self.assertContains(response, content)
                self.assertNotContains(response, "<pre")
                self.assertNotContains(response, '&quot;title&quot;')
                self.assertNotContains(response, '&quot;role&quot;')

    def test_legacy_aliases_metadata_and_mixed_entries_remain_visible(self):
        StudentProfile.objects.create(
            user=self.student,
            portfolio_projects=[{"name": "Legacy prototype", "tech_stack": ["Python", "Django"]}, "Community project", 3, None],
            experience=[{"position": "Volunteer", "details": {"team": "Campus team"}}, True],
        )
        self.client.force_login(self.investor)
        response = self.client.get(reverse("accounts:investor_profile", args=[self.student.pk]))
        for content in ("Legacy prototype", "Tech stack", "Python", "Django", "Community project", "Not specified", "Volunteer", "Campus team", "Yes"):
            self.assertContains(response, content)
        self.assertNotContains(response, "<pre")

    def test_untrusted_content_is_escaped_and_only_web_urls_are_links(self):
        StudentProfile.objects.create(
            user=self.student,
            portfolio_projects=[
                {"title": "<script>alert(1)</script>", "url": "javascript:alert(1)"},
                {"title": "Safe project", "url": "https://example.com/project"},
            ],
            experience=[{"role": "<img src=x onerror=alert(1)>"}],
        )
        self.client.force_login(self.investor)
        response = self.client.get(reverse("accounts:investor_profile", args=[self.student.pk]))
        self.assertContains(response, '&lt;script&gt;')
        self.assertNotContains(response, '<script>alert(1)')
        self.assertNotContains(response, '<img src=x')
        self.assertNotContains(response, 'href="javascript:')
        self.assertContains(response, 'href="https://example.com/project"')


class ProfileEntryEditorTests(FollowingTestDataMixin, TestCase):
    def setUp(self):
        self.url = reverse("accounts:student_profile")
        self.client.force_login(self.student)

    def editor_data(self):
        response = self.client.get(self.url)
        data = {"profile_entries_editor": "1", "bio": response.context["form"]["bio"].value() or ""}
        skills = response.context["form"]["skills"].value()
        data["skills"] = skills or []
        for key in ("projects_formset", "experience_formset"):
            formset = response.context[key]
            for field in formset.management_form:
                data[field.html_name] = field.value()
            for form in formset:
                for field in form:
                    if field.name != "DELETE":
                        data[field.html_name] = field.value() or ""
        return data

    def test_create_projects_and_experience_using_ordinary_fields(self):
        data = self.editor_data()
        data.update({
            "bio": "A readable profile",
            "projects-0-heading": "Campus energy dashboard",
            "projects-0-description": "A useful dashboard.",
            "projects-0-url": "https://example.com/dashboard",
            "experience-0-heading": "Student researcher",
            "experience-0-organization": "UPM",
            "experience-0-period": "2025–2026",
            "experience-0-description": "Built research prototypes.",
        })

        response = self.client.post(self.url, data)

        self.assertRedirects(response, self.url)
        profile = StudentProfile.objects.get(user=self.student)
        self.assertEqual(profile.portfolio_projects, [{"title": "Campus energy dashboard", "description": "A useful dashboard.", "url": "https://example.com/dashboard"}])
        self.assertEqual(profile.experience, [{"role": "Student researcher", "organization": "UPM", "period": "2025–2026", "description": "Built research prototypes."}])

    def test_edited_fields_preserve_aliases_and_additional_metadata(self):
        profile = StudentProfile.objects.create(
            user=self.student,
            portfolio_projects=[{"name": "Old project", "metadata": {"tags": ["campus"]}}],
            experience=[{"position": "Researcher", "company": "Old lab", "year": 2024, "extra": [1, 2]}],
        )
        data = self.editor_data()
        data.update({"projects-0-heading": "Updated project", "experience-0-organization": "New lab"})

        self.assertRedirects(self.client.post(self.url, data), self.url)

        profile.refresh_from_db()
        self.assertEqual(profile.portfolio_projects, [{"name": "Updated project", "metadata": {"tags": ["campus"]}}])
        self.assertEqual(profile.experience, [{"position": "Researcher", "company": "New lab", "year": 2024, "extra": [1, 2]}])

    def test_untouched_mixed_legacy_values_are_preserved_exactly(self):
        projects = [{"title": "Legacy", "custom": {"values": [True, None]}}, {"title": "Old link", "url": "javascript:example"}, "Plain project", 3, True, None, ["Nested", 2]]
        experience = [{"position": "Volunteer", "link": "javascript:example"}, "Plain role", False, {"custom": ["Other"]}]
        profile = StudentProfile.objects.create(user=self.student, portfolio_projects=projects, experience=experience)
        data = self.editor_data()
        data["bio"] = "Only the bio changes."

        self.assertRedirects(self.client.post(self.url, data), self.url)

        profile.refresh_from_db()
        self.assertEqual(profile.portfolio_projects, projects)
        self.assertEqual(profile.experience, experience)

    def test_explicit_removal_preserves_the_other_entries(self):
        profile = StudentProfile.objects.create(
            user=self.student,
            portfolio_projects=[{"title": "Remove me"}, {"title": "Keep me", "extra": [3]}],
            experience=[{"role": "Keep this role"}],
        )
        data = self.editor_data()
        data["projects-0-DELETE"] = "on"

        self.assertRedirects(self.client.post(self.url, data), self.url)

        profile.refresh_from_db()
        self.assertEqual(profile.portfolio_projects, [{"title": "Keep me", "extra": [3]}])
        self.assertEqual(profile.experience, [{"role": "Keep this role"}])

    def test_invalid_entry_shows_errors_and_values_without_partial_save(self):
        profile = StudentProfile.objects.create(user=self.student, bio="Keep bio", portfolio_projects=[{"title": "Keep project"}])
        data = self.editor_data()
        data.update({"bio": "Do not save", "projects-0-heading": "", "projects-0-description": "Keep my typed description", "experience-0-heading": "Do not save this role"})

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Enter a project title or remove this entry.")
        self.assertContains(response, "Keep my typed description")
        self.assertContains(response, "Do not save this role")
        profile.refresh_from_db()
        self.assertEqual(profile.bio, "Keep bio")
        self.assertEqual(profile.portfolio_projects, [{"title": "Keep project"}])
        self.assertEqual(profile.experience, [])

    def test_new_project_rejects_unsafe_links(self):
        data = self.editor_data()
        data.update({"projects-0-heading": "Project", "projects-0-url": "javascript:alert(1)"})

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Enter a full link starting with https:// or http://.")
        self.assertFalse(StudentProfile.objects.exists())

    def test_missing_or_shortened_management_data_cannot_erase_saved_entries(self):
        profile = StudentProfile.objects.create(user=self.student, portfolio_projects=[{"title": "Keep project"}])
        for field, value in (("projects-TOTAL_FORMS", "0"), ("projects-INITIAL_FORMS", "0"), ("projects-TOTAL_FORMS", None)):
            with self.subTest(field=field, value=value):
                data = self.editor_data()
                if value is None:
                    data.pop(field)
                else:
                    data[field] = value
                response = self.client.post(self.url, data)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "Reload the page and try again.")
                profile.refresh_from_db()
                self.assertEqual(profile.portfolio_projects, [{"title": "Keep project"}])

    def test_empty_extra_entries_are_optional_and_do_not_create_empty_objects(self):
        data = self.editor_data()
        data["bio"] = "My bio"

        self.assertRedirects(self.client.post(self.url, data), self.url)

        profile = StudentProfile.objects.get(user=self.student)
        self.assertEqual(profile.portfolio_projects, [])
        self.assertEqual(profile.experience, [])

    def test_new_editor_keeps_existing_ownership_and_role_restrictions(self):
        other_profile = StudentProfile.objects.create(user=self.other_student, bio="Other student")
        data = self.editor_data()
        data.update({"user": self.other_student.pk, "profile": other_profile.pk, "projects-0-heading": "My project"})
        self.assertRedirects(self.client.post(self.url, data), self.url)
        other_profile.refresh_from_db()
        self.assertEqual(other_profile.bio, "Other student")
        self.assertEqual(other_profile.portfolio_projects, [])
        self.assertEqual(StudentProfile.objects.get(user=self.student).portfolio_projects, [{"title": "My project"}])
        self.client.force_login(self.investor)
        self.assertEqual(self.client.post(self.url, data).status_code, 403)


class ProfileVisitStatisticsTests(TestCase):
    """US019 (#52): students see how many times investors visited their profile."""

    password = "Profile-visits-123!"

    def create_user(self, email, role):
        return User.objects.create_user(
            email=email,
            password=self.password,
            name=f"{role.title()} Visits User",
            role=role,
        )

    def setUp(self):
        self.student = self.create_user("visits-student@example.com", User.Role.STUDENT)
        self.investor = self.create_user("visits-investor@example.com", User.Role.INVESTOR)
        self.own_profile_url = reverse("accounts:my_profile")
        self.investor_profile_url = reverse(
            "accounts:investor_profile", args=[self.student.pk]
        )

    def test_investor_visit_is_recorded(self):
        self.client.force_login(self.investor)

        self.client.get(self.investor_profile_url)
        self.client.get(self.investor_profile_url)

        self.assertEqual(ProfileVisit.objects.filter(student=self.student).count(), 2)
        self.assertEqual(ProfileVisit.objects.first().visitor, self.investor)

    def test_visits_are_recorded_for_students_without_a_profile(self):
        self.assertFalse(StudentProfile.objects.filter(user=self.student).exists())
        self.client.force_login(self.investor)

        self.client.get(self.investor_profile_url)

        self.assertEqual(self.student.profile_visits.count(), 1)

    def test_student_viewing_own_profile_is_not_a_visit(self):
        self.client.force_login(self.student)

        self.client.get(self.own_profile_url)

        self.assertFalse(ProfileVisit.objects.exists())

    def test_forbidden_or_anonymous_requests_are_not_visits(self):
        other_student = self.create_user("visits-other@example.com", User.Role.STUDENT)

        self.client.get(self.investor_profile_url)
        self.client.force_login(other_student)
        self.client.get(self.investor_profile_url)

        self.assertFalse(ProfileVisit.objects.exists())

    def test_student_sees_total_number_of_visits(self):
        ProfileVisit.objects.create(student=self.student, visitor=self.investor)
        ProfileVisit.objects.create(student=self.student, visitor=self.investor)
        ProfileVisit.objects.create(student=self.student, visitor=self.investor)
        self.client.force_login(self.student)

        response = self.client.get(self.own_profile_url)

        self.assertEqual(response.context["profile_visit_count"], 3)
        self.assertContains(response, "Investors have visited your profile 3 times.")

    def test_single_visit_uses_singular(self):
        ProfileVisit.objects.create(student=self.student, visitor=self.investor)
        self.client.force_login(self.student)

        response = self.client.get(self.own_profile_url)

        self.assertContains(response, "Investors have visited your profile 1 time.")

    def test_new_profile_shows_zero_visits_state(self):
        self.client.force_login(self.student)

        response = self.client.get(self.own_profile_url)

        self.assertEqual(response.context["profile_visit_count"], 0)
        self.assertContains(response, "No visits have been recorded yet.")

    def test_only_visits_to_own_profile_are_counted(self):
        other_student = self.create_user("visits-counted@example.com", User.Role.STUDENT)
        ProfileVisit.objects.create(student=other_student, visitor=self.investor)
        self.client.force_login(self.student)

        response = self.client.get(self.own_profile_url)

        self.assertEqual(response.context["profile_visit_count"], 0)

    def test_investors_do_not_see_the_visit_statistics(self):
        ProfileVisit.objects.create(student=self.student, visitor=self.investor)
        self.client.force_login(self.investor)

        response = self.client.get(self.investor_profile_url)

        self.assertNotContains(response, "Profile visits")
        self.assertNotContains(response, "No visits have been recorded yet.")
