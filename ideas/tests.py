from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import IdeaForm
from .models import Category, Idea

User = get_user_model()


def create_student(email="student@example.com"):
    return User.objects.create_user(
        email=email,
        password="A-valid-password-123!",
        name="Test Student",
        role=User.Role.STUDENT,
    )


class HomePageTests(TestCase):
    def test_home_page_loads(self):
        response = self.client.get(reverse("ideas:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "base.html")

    def test_home_page_displays_published_ideas(self):
        idea = Idea.objects.create(
            title="Campus bike sharing",
            description="Share bikes between faculties.",
            owner=create_student(),
        )
        response = self.client.get(reverse("ideas:home"))
        self.assertIn(idea, response.context["ideas"])

    def test_category_filter_shows_only_ideas_in_selected_category(self):
        technology = Category.objects.create(name="Technology test")
        health = Category.objects.create(name="Health test")
        owner = create_student()
        matching = Idea.objects.create(
            title="Study planner",
            description="Plan exams.",
            owner=owner,
            category=technology,
        )
        Idea.objects.create(
            title="Clinic booking",
            description="Book visits.",
            owner=owner,
            category=health,
        )

        response = self.client.get(
            reverse("ideas:home"), {"category": technology.pk}
        )

        self.assertEqual(list(response.context["ideas"]), [matching])
        self.assertEqual(response.context["selected_category"], technology)

    def test_clearing_category_filter_restores_all_ideas(self):
        technology = Category.objects.create(name="Technology clear test")
        health = Category.objects.create(name="Health clear test")
        owner = create_student()
        ideas = [
            Idea.objects.create(
                title="Study planner",
                description="Plan exams.",
                owner=owner,
                category=technology,
            ),
            Idea.objects.create(
                title="Clinic booking",
                description="Book visits.",
                owner=owner,
                category=health,
            ),
        ]

        response = self.client.get(reverse("ideas:home"))

        self.assertCountEqual(response.context["ideas"], ideas)
        self.assertIsNone(response.context["selected_category"])

    def test_empty_category_filter_shows_no_match_message(self):
        category = Category.objects.create(name="Empty test category")

        response = self.client.get(reverse("ideas:home"), {"category": category.pk})

        self.assertEqual(list(response.context["ideas"]), [])
        self.assertContains(response, "No ideas were found in this category.")

    def test_discovery_page_renders_idea_and_category_filter_controls(self):
        category = Category.objects.create(name="Design test category")
        idea = Idea.objects.create(
            title="Accessible campus map",
            description="Map accessible routes.",
            owner=create_student(),
            category=category,
        )

        response = self.client.get(
            reverse("ideas:home"), {"category": category.pk}
        )

        self.assertContains(response, idea.title)
        self.assertContains(response, category.name)
        self.assertContains(response, 'name="category"')
        self.assertContains(response, 'value=""')
        self.assertContains(response, 'href="/"')

    def test_empty_discovery_page_explains_that_no_ideas_are_published(self):
        response = self.client.get(reverse("ideas:home"))

        self.assertContains(response, "No published ideas yet.")


class CategoryModelTests(TestCase):
    def test_initial_categories_are_loaded(self):
        self.assertTrue(Category.objects.filter(name="Technology").exists())
        self.assertGreater(Category.objects.count(), 1)

    def test_names_are_unique_ignoring_case(self):
        Category.objects.create(name="Robotics")
        with self.assertRaises(IntegrityError), transaction.atomic():
            Category.objects.create(name="robotics")


class IdeaModelTests(TestCase):
    def setUp(self):
        self.owner = create_student()

    def test_idea_is_stored_with_owner_and_publication_date(self):
        before = timezone.now()
        idea = Idea.objects.create(
            title="Campus bike sharing",
            description="Share bikes between faculties.",
            owner=self.owner,
        )
        idea.refresh_from_db()
        self.assertEqual(idea.owner, self.owner)
        self.assertIsNone(idea.category)
        self.assertGreaterEqual(idea.published_at, before)
        self.assertEqual(str(idea), "Campus bike sharing")

    def test_idea_can_have_a_category(self):
        category = Category.objects.get(name="Technology")
        idea = Idea.objects.create(
            title="Study planner",
            description="An app to plan exams.",
            owner=self.owner,
            category=category,
        )
        self.assertEqual(idea.category, category)

    def test_category_in_use_cannot_be_deleted(self):
        category = Category.objects.create(name="Robotics")
        Idea.objects.create(
            title="Robot tutor",
            description="A tutoring robot.",
            owner=self.owner,
            category=category,
        )
        with self.assertRaises(ProtectedError):
            category.delete()


class IdeaFormTests(TestCase):
    def test_valid_form_without_category(self):
        form = IdeaForm({"title": "My idea", "description": "Something useful."})
        self.assertTrue(form.is_valid(), form.errors)

    def test_title_is_required(self):
        form = IdeaForm({"title": "", "description": "Something useful."})
        self.assertFalse(form.is_valid())
        self.assertEqual(list(form.errors), ["title"])

    def test_description_is_required(self):
        form = IdeaForm({"title": "My idea", "description": ""})
        self.assertFalse(form.is_valid())
        self.assertEqual(list(form.errors), ["description"])

    def test_whitespace_only_values_count_as_missing(self):
        form = IdeaForm({"title": "   ", "description": "\n  "})
        self.assertFalse(form.is_valid())
        self.assertEqual(set(form.errors), {"title", "description"})

    def test_fields_follow_the_wireframe_order(self):
        self.assertEqual(list(IdeaForm().fields), ["title", "description", "category"])


class PublishIdeaAccessTests(TestCase):
    def setUp(self):
        self.url = reverse("ideas:publish")

    def test_anonymous_visitor_is_redirected_to_login(self):
        response = self.client.get(self.url)
        self.assertRedirects(
            response, f"{reverse('accounts:login')}?next={self.url}"
        )

    def test_anonymous_post_does_not_create_an_idea(self):
        self.client.post(self.url, {"title": "T", "description": "D"})
        self.assertEqual(Idea.objects.count(), 0)

    def test_investor_gets_403(self):
        investor = User.objects.create_user(
            email="investor@example.com",
            password="A-valid-password-123!",
            name="Test Investor",
            role=User.Role.INVESTOR,
        )
        self.client.force_login(investor)
        self.assertEqual(self.client.get(self.url).status_code, 403)
        response = self.client.post(self.url, {"title": "T", "description": "D"})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Idea.objects.count(), 0)

    def test_student_sees_the_form(self):
        self.client.force_login(create_student())
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ideas/idea_form.html")


class SubmitIdeaTests(TestCase):
    """Criterion: Submit an idea (US001, #4)."""

    def setUp(self):
        self.student = create_student()
        self.client.force_login(self.student)
        self.url = reverse("ideas:publish")

    def test_valid_idea_is_published_and_visible_to_other_users(self):
        response = self.client.post(
            self.url, {"title": "Campus bikes", "description": "Share bikes."}
        )
        self.assertRedirects(response, reverse("ideas:home"))
        idea = Idea.objects.get()
        self.assertEqual(idea.owner, self.student)
        self.assertEqual(idea.title, "Campus bikes")
        # Available to other users: another account can read it.
        other = create_student("other@example.com")
        self.assertIn(idea, Idea.objects.exclude(owner=other))

    def test_idea_is_published_with_the_selected_category(self):
        category = Category.objects.get(name="Health")
        self.client.post(
            self.url,
            {"title": "Clinic app", "description": "Book visits.", "category": category.pk},
        )
        self.assertEqual(Idea.objects.get().category, category)

    def test_success_message_is_shown_after_publishing(self):
        response = self.client.post(
            self.url,
            {"title": "Campus bikes", "description": "Share bikes."},
            follow=True,
        )
        self.assertContains(response, "Your idea has been published.")

    def test_owner_cannot_be_set_from_the_form(self):
        other = create_student("other@example.com")
        self.client.post(
            self.url,
            {"title": "Mine", "description": "Mine.", "owner": other.pk},
        )
        self.assertEqual(Idea.objects.get().owner, self.student)


class EditIdeaTests(TestCase):
    def setUp(self):
        self.owner = create_student()
        self.category = Category.objects.get(name="Technology")
        self.idea = Idea.objects.create(
            title="Original title",
            description="Original description",
            owner=self.owner,
        )
        self.url = reverse("ideas:edit", args=[self.idea.pk])
        self.client.force_login(self.owner)

    def test_owner_can_update_title_description_and_category(self):
        response = self.client.post(
            self.url,
            {
                "title": "Updated title",
                "description": "Updated description",
                "category": self.category.pk,
            },
        )
        self.assertRedirects(response, reverse("ideas:home"))
        self.idea.refresh_from_db()
        self.assertEqual(self.idea.title, "Updated title")
        self.assertEqual(self.idea.description, "Updated description")
        self.assertEqual(self.idea.category, self.category)

    def test_owner_sees_edit_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit idea")
        self.assertContains(response, "Save changes")

    def test_another_student_gets_403_for_get_and_post(self):
        other = create_student("other@example.com")
        self.client.force_login(other)
        self.assertEqual(self.client.get(self.url).status_code, 403)
        response = self.client.post(
            self.url, {"title": "Hijacked", "description": "Changed"}
        )
        self.assertEqual(response.status_code, 403)
        self.idea.refresh_from_db()
        self.assertEqual(self.idea.title, "Original title")

    def test_investor_gets_403(self):
        investor = User.objects.create_user(
            email="investor@example.com",
            password="A-valid-password-123!",
            name="Test Investor",
            role=User.Role.INVESTOR,
        )
        self.client.force_login(investor)
        self.assertEqual(self.client.get(self.url).status_code, 403)
        self.assertEqual(
            self.client.post(
                self.url, {"title": "Changed", "description": "Changed"}
            ).status_code,
            403,
        )

    def test_missing_or_whitespace_required_fields_are_not_saved(self):
        invalid_payloads = [
            {},
            {"title": "", "description": "New description"},
            {"title": "New title", "description": ""},
            {"title": "   ", "description": "New description"},
            {"title": "New title", "description": " \n "},
        ]
        for payload in invalid_payloads:
            with self.subTest(payload=payload):
                response = self.client.post(self.url, payload)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "Please enter a ")
                self.idea.refresh_from_db()
                self.assertEqual(self.idea.title, "Original title")
                self.assertEqual(self.idea.description, "Original description")


class RequireEssentialInformationTests(TestCase):
    """Criterion: Require essential information (US001, #4)."""

    def setUp(self):
        self.client.force_login(create_student())
        self.url = reverse("ideas:publish")

    def assertNotPublished(self, response, *messages):
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Idea.objects.count(), 0)
        for message in messages:
            self.assertContains(response, message)

    def test_missing_title_asks_for_the_title(self):
        response = self.client.post(self.url, {"title": "", "description": "Text."})
        self.assertNotPublished(response, "Please enter a title for your idea.")
        self.assertNotContains(response, "Please enter a description for your idea.")

    def test_missing_description_asks_for_the_description(self):
        response = self.client.post(self.url, {"title": "Title", "description": ""})
        self.assertNotPublished(response, "Please enter a description for your idea.")
        self.assertNotContains(response, "Please enter a title for your idea.")

    def test_missing_both_asks_for_both(self):
        response = self.client.post(self.url, {"title": "", "description": ""})
        self.assertNotPublished(
            response,
            "Please enter a title for your idea.",
            "Please enter a description for your idea.",
        )

    def test_entered_values_are_kept_when_validation_fails(self):
        response = self.client.post(self.url, {"title": "Keep me", "description": ""})
        self.assertContains(response, "Keep me")


class IdeaFormPageTests(TestCase):
    def test_form_follows_the_wireframe(self):
        self.client.force_login(create_student())
        html = self.client.get(reverse("ideas:publish")).content.decode()
        positions = [
            html.index('name="title"'),
            html.index('name="description"'),
            html.index('name="category"'),
            html.index(">Publish</button>"),
        ]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("Technology", html)

    def test_students_see_the_publish_link(self):
        self.client.force_login(create_student())
        response = self.client.get(reverse("ideas:home"))
        self.assertContains(response, reverse("ideas:publish"))

    def test_anonymous_visitors_do_not_see_the_publish_link(self):
        response = self.client.get(reverse("ideas:home"))
        self.assertNotContains(response, reverse("ideas:publish"))

    def test_investors_do_not_see_the_publish_link(self):
        investor = User.objects.create_user(
            email="investor@example.com",
            password="A-valid-password-123!",
            name="Test Investor",
            role=User.Role.INVESTOR,
        )
        self.client.force_login(investor)
        response = self.client.get(reverse("ideas:home"))
        self.assertNotContains(response, reverse("ideas:publish"))
