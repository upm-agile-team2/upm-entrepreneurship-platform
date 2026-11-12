from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ideas.models import Idea

from .forms import StudentProfileForm
from .models import Skill, StudentProfile


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

    def test_editor_uses_shared_styled_form_and_explains_json_inputs(self):
        self.client.force_login(self.student)

        response = self.client.get(self.edit_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="form-surface"')
        self.assertContains(response, 'for="id_bio"')
        self.assertContains(response, "Items may be any JSON values")
        self.assertContains(response, "No skills are available to select yet.")
        self.assertContains(response, self.own_profile_url)

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
