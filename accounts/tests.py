from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ideas.models import Idea


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
