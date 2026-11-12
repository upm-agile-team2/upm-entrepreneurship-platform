from io import StringIO
import re

from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ValidationError
from django.core.management import CommandError, call_command
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .forms import IdeaForm
from .management.commands.seed_demo_ideas import (
    DEMO_AUTHOR_KEY_PREFIX,
    DEMO_IDEA_KEY_PREFIX,
    DEMO_IDEAS,
    DEMO_STUDENTS,
    demo_email,
)
from .models import Category, Feedback, Idea, Notification, Reply

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

    def test_idea_card_links_to_its_detail_page(self):
        idea = Idea.objects.create(
            title="Campus bike sharing",
            description="Share bikes between faculties.",
            owner=create_student(),
        )

        response = self.client.get(reverse("ideas:home"))

        self.assertContains(response, reverse("ideas:detail", args=[idea.pk]))

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


class IdeaDetailPageTests(TestCase):
    def setUp(self):
        self.owner = create_student()
        self.category = Category.objects.create(name="Detail test category")
        self.idea = Idea.objects.create(
            title="Campus bike sharing",
            description="Share bikes between faculties.\nInclude accessible options.",
            owner=self.owner,
            category=self.category,
        )
        self.url = reverse("ideas:detail", args=[self.idea.pk])

    def test_detail_page_shows_title_full_description_and_category(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ideas/idea_detail.html")
        self.assertContains(response, self.idea.title)
        self.assertContains(response, "Share bikes between faculties.")
        self.assertContains(response, "Include accessible options.")
        self.assertContains(response, self.category.name)

    def test_detail_page_handles_idea_without_category(self):
        idea_without_category = Idea.objects.create(
            title="Category-free idea",
            description="This idea has no category.",
            owner=self.owner,
        )

        response = self.client.get(
            reverse("ideas:detail", args=[idea_without_category.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, idea_without_category.title)
        self.assertNotContains(response, "Detail test category")

    def test_unknown_idea_returns_404(self):
        response = self.client.get(reverse("ideas:detail", args=[999999]))

        self.assertEqual(response.status_code, 404)

    def test_owner_sees_edit_link(self):
        self.client.force_login(self.owner)

        response = self.client.get(self.url)

        self.assertContains(response, reverse("ideas:edit", args=[self.idea.pk]))

    def test_unrelated_student_does_not_see_edit_link(self):
        self.client.force_login(create_student("other@example.com"))

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, reverse("ideas:edit", args=[self.idea.pk]))

    def test_investor_does_not_see_edit_link(self):
        investor = User.objects.create_user(
            email="detail-investor@example.com",
            password="A-valid-password-123!",
            name="Detail Investor",
            role=User.Role.INVESTOR,
        )
        self.client.force_login(investor)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, reverse("ideas:edit", args=[self.idea.pk]))

    def test_investor_can_follow_idea_author_to_profile(self):
        investor = User.objects.create_user(
            email="profile-link-investor@example.com",
            password="A-valid-password-123!",
            name="Profile Link Investor",
            role=User.Role.INVESTOR,
        )
        profile_url = reverse("accounts:investor_profile", args=[self.owner.pk])
        self.client.force_login(investor)

        response = self.client.get(self.url)

        self.assertContains(response, f'href="{profile_url}"')
        self.assertContains(response, self.owner.name)

    def test_student_and_anonymous_visitors_do_not_see_investor_profile_link(self):
        profile_url = reverse("accounts:investor_profile", args=[self.owner.pk])
        anonymous_response = self.client.get(self.url)
        self.assertNotContains(anonymous_response, profile_url)

        self.client.force_login(create_student("profile-link-student@example.com"))
        student_response = self.client.get(self.url)
        self.assertNotContains(student_response, profile_url)

    def test_anonymous_visitor_can_view_page_without_edit_link(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, reverse("ideas:edit", args=[self.idea.pk]))

    def test_detail_page_links_back_to_discovery(self):
        response = self.client.get(self.url)

        self.assertContains(response, reverse("ideas:home"))


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


class FeedbackModelTests(TestCase):
    def setUp(self):
        self.owner = create_student("feedback-idea-owner@example.com")
        self.author = User.objects.create_user(
            email="feedback-investor@example.com",
            password="A-valid-password-123!",
            name="Feedback Investor",
            role=User.Role.INVESTOR,
        )
        self.idea = Idea.objects.create(
            title="Campus bike sharing",
            description="Share bikes between faculties.",
            owner=self.owner,
        )

    def test_feedback_is_stored_with_idea_author_text_and_timestamp(self):
        before = timezone.now()

        feedback = Feedback.objects.create(
            idea=self.idea,
            author=self.author,
            text="Consider a low-cost student subscription.",
        )
        feedback.refresh_from_db()

        self.assertEqual(feedback.idea, self.idea)
        self.assertEqual(feedback.author, self.author)
        self.assertEqual(feedback.text, "Consider a low-cost student subscription.")
        self.assertGreaterEqual(feedback.timestamp, before)
        self.assertLessEqual(feedback.timestamp, timezone.now())

    def test_empty_text_fails_model_validation(self):
        feedback = Feedback(idea=self.idea, author=self.author, text="")

        with self.assertRaisesMessage(ValidationError, "This field cannot be blank."):
            feedback.full_clean()

    def test_deleting_author_preserves_feedback_and_clears_author(self):
        feedback = Feedback.objects.create(
            idea=self.idea,
            author=self.author,
            text="Useful feedback.",
        )

        self.author.delete()
        feedback.refresh_from_db()

        self.assertIsNone(feedback.author)
        self.assertEqual(feedback.text, "Useful feedback.")

    def test_deleting_idea_cascades_to_its_feedback(self):
        feedback = Feedback.objects.create(
            idea=self.idea,
            author=self.author,
            text="Useful feedback.",
        )

        self.idea.delete()

        self.assertFalse(Feedback.objects.filter(pk=feedback.pk).exists())

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

    def test_another_student_gets_403_for_direct_edit_url_request(self):
        other = create_student("other@example.com")
        self.client.force_login(other)
        self.assertEqual(self.client.get(self.url).status_code, 403)

    def test_another_student_gets_403_for_post_to_owner_edit_url(self):
        other = create_student("other@example.com")
        self.client.force_login(other)
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
            ({}, ("title", "description")),
            ({"title": "", "description": "New description"}, ("title",)),
            ({"title": "New title", "description": ""}, ("description",)),
            ({"title": "   ", "description": "New description"}, ("title",)),
            ({"title": "New title", "description": " \n "}, ("description",)),
        ]
        for payload, missing_fields in invalid_payloads:
            with self.subTest(payload=payload):
                response = self.client.post(self.url, payload)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(set(response.context["form"].errors), set(missing_fields))
                for field in missing_fields:
                    self.assertContains(response, f"Please enter a {field} for your idea.")
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
        # Check the page's form content independently of document metadata.
        html = html.split("<main", 1)[1].split("</main>", 1)[0]
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


class DiscoveryPageTemplateTests(TestCase):
    def test_discovery_controls_and_empty_state_render(self):
        response = self.client.get(reverse("ideas:home"))

        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertContains(response, 'method="get"')
        self.assertContains(response, 'name="category"')
        self.assertContains(response, 'role="status"')
        self.assertContains(response, "No published ideas yet.")
        self.assertContains(
            response,
            '<a href="/" class="btn btn-outline-secondary">Clear filter</a>',
        )

    def test_invalid_category_shows_no_match_message(self):
        response = self.client.get(reverse("ideas:home"), {"category": "climate"})

        self.assertContains(response, "No ideas were found in this category.")

    def test_unknown_category_id_shows_no_match_message(self):
        response = self.client.get(reverse("ideas:home"), {"category": "999999"})

        self.assertEqual(list(response.context["ideas"]), [])
        self.assertContains(response, "No ideas were found in this category.")

    def test_every_category_is_offered_as_a_filter_option(self):
        category = Category.objects.create(name="Climate test")

        response = self.client.get(reverse("ideas:home"))

        self.assertContains(
            response,
            f'<option value="{category.pk}">{category.name}</option>',
            html=True,
        )

    def test_selected_category_is_marked_in_the_filter(self):
        climate = Category.objects.create(name="Climate test")
        health = Category.objects.create(name="Health test")

        response = self.client.get(reverse("ideas:home"), {"category": climate.pk})

        self.assertContains(
            response,
            f'<option value="{climate.pk}" selected>{climate.name}</option>',
            html=True,
        )
        self.assertContains(
            response,
            f'<option value="{health.pk}">{health.name}</option>',
            html=True,
        )

    def test_card_shows_category_badge(self):
        category = Category.objects.create(name="Climate test")
        Idea.objects.create(
            title="Solar co-op",
            description="Share solar panels.",
            owner=create_student(),
            category=category,
        )

        response = self.client.get(reverse("ideas:home"))

        self.assertContains(
            response,
            '<span class="badge text-bg-secondary">Climate test</span>',
            html=True,
        )

    def test_card_truncates_long_descriptions(self):
        description = " ".join(f"word{i}" for i in range(40))
        Idea.objects.create(
            title="Long idea",
            description=description,
            owner=create_student(),
        )

        response = self.client.get(reverse("ideas:home"))

        self.assertContains(response, "word29 …")
        self.assertNotContains(response, "word30")


class SeedDemoIdeasCommandTests(TestCase):
    def run_command(self, *args):
        out = StringIO()
        call_command("seed_demo_ideas", *args, stdout=out)
        return out.getvalue()

    def test_creates_the_sample_ideas_in_every_category(self):
        self.run_command()

        self.assertEqual(Idea.objects.count(), len(DEMO_IDEAS))
        used = set(Idea.objects.values_list("category__name", flat=True))
        self.assertTrue(
            {
                "Technology",
                "Health",
                "Education",
                "Sustainability",
                "Finance",
                "Social impact",
                "Other",
            }
            <= used
        )

    def test_demo_authors_are_students_who_cannot_sign_in(self):
        self.run_command()

        authors = User.objects.filter(demo_key__startswith=DEMO_AUTHOR_KEY_PREFIX)
        self.assertEqual(authors.count(), 4)
        for author in authors:
            self.assertTrue(author.is_student)
            self.assertFalse(author.has_usable_password())
            self.assertIsNone(authenticate(email=author.email, password="any-password"))

    def test_rerun_restores_unusable_password_for_an_existing_demo_author(self):
        self.run_command()
        author = User.objects.get(demo_key=f"{DEMO_AUTHOR_KEY_PREFIX}lucia.moreno")
        author.set_password("Temporary-password-123!")
        author.save(update_fields=["password"])

        self.run_command()

        author.refresh_from_db()
        self.assertFalse(author.has_usable_password())
        self.assertIsNone(authenticate(email=author.email, password="Temporary-password-123!"))

    def test_running_twice_does_not_duplicate_ideas(self):
        self.run_command()
        output = self.run_command()

        self.assertEqual(
            Idea.objects.filter(demo_key__startswith=DEMO_IDEA_KEY_PREFIX).count(),
            len(DEMO_IDEAS),
        )
        self.assertEqual(
            User.objects.filter(demo_key__startswith=DEMO_AUTHOR_KEY_PREFIX).count(), 4
        )
        self.assertIn("Created 0 sample ideas", output)

    def test_rerun_after_idea_is_renamed_preserves_it_without_a_duplicate(self):
        self.run_command()
        idea = Idea.objects.get(demo_key=f"{DEMO_IDEA_KEY_PREFIX}campus-lost-found-app")
        idea.title = "Community lost property board"
        idea.description = "A revised description that a rerun should preserve."
        idea.save(update_fields=["title", "description"])

        self.run_command()

        self.assertEqual(
            Idea.objects.filter(demo_key=f"{DEMO_IDEA_KEY_PREFIX}campus-lost-found-app").count(),
            1,
        )
        idea.refresh_from_db()
        self.assertEqual(idea.title, "Community lost property board")
        self.assertEqual(idea.description, "A revised description that a rerun should preserve.")
        self.assertFalse(Idea.objects.filter(title="Campus lost & found app").exists())

    def test_sample_ideas_appear_on_the_discovery_page(self):
        self.run_command()

        response = self.client.get(reverse("ideas:home"))

        self.assertContains(response, "Campus lost &amp; found app")

    def test_remove_deletes_marked_demo_ideas_and_unreferenced_demo_authors(self):
        real_idea = Idea.objects.create(
            title="Real idea",
            description="Published by a real student.",
            owner=create_student(),
        )
        self.run_command()
        self.assertEqual(
            Idea.objects.filter(demo_key__startswith=DEMO_IDEA_KEY_PREFIX).count(),
            len(DEMO_IDEAS),
        )
        renamed_idea = Idea.objects.get(demo_key=f"{DEMO_IDEA_KEY_PREFIX}campus-lost-found-app")
        renamed_idea.title = "Community lost property board"
        renamed_idea.save(update_fields=["title"])

        output = self.run_command("--remove")

        self.assertEqual(list(Idea.objects.all()), [real_idea])
        self.assertFalse(User.objects.filter(demo_key__startswith=DEMO_AUTHOR_KEY_PREFIX).exists())
        self.assertIn("Removed 20 sample ideas and 4 demo authors", output)

    def test_reserved_email_collision_aborts_without_creating_demo_records(self):
        collision = User.objects.create_user(
            email=demo_email(DEMO_STUDENTS[0][0]),
            password="Real-account-password-123!",
            name="Real Account",
            role=User.Role.INVESTOR,
        )

        with self.assertRaisesMessage(CommandError, "identity mismatch"):
            self.run_command()

        collision.refresh_from_db()
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Idea.objects.count(), 0)
        self.assertFalse(User.objects.filter(demo_key__startswith=DEMO_AUTHOR_KEY_PREFIX).exists())

    def test_reserved_email_collision_preserves_account_password_role_and_name(self):
        collision = User.objects.create_user(
            email=demo_email(DEMO_STUDENTS[0][0]),
            password="Real-account-password-123!",
            name="Real Account",
            role=User.Role.INVESTOR,
        )
        real_idea = Idea.objects.create(
            title="Account owner's existing idea",
            description="This must survive a failed seed attempt.",
            owner=collision,
        )
        original = (collision.password, collision.name, collision.role, collision.email)

        with self.assertRaises(CommandError):
            self.run_command()

        collision.refresh_from_db()
        self.assertEqual(
            (collision.password, collision.name, collision.role, collision.email), original
        )
        self.assertTrue(collision.check_password("Real-account-password-123!"))
        self.assertTrue(Idea.objects.filter(pk=real_idea.pk, owner=collision).exists())

    def test_collision_late_in_author_list_does_not_partially_seed_earlier_authors(self):
        User.objects.create_user(
            email=demo_email(DEMO_STUDENTS[-1][0]),
            password="Real-account-password-123!",
            name="Existing Account",
            role=User.Role.STUDENT,
        )

        with self.assertRaises(CommandError):
            self.run_command()

        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Idea.objects.count(), 0)

    def test_reserved_email_with_another_demo_key_is_rejected_without_changes(self):
        account = User.objects.create_user(
            email=demo_email(DEMO_STUDENTS[0][0]),
            password="Existing-password-123!",
            name="Mismatched Account",
            role=User.Role.STUDENT,
            demo_key=f"{DEMO_AUTHOR_KEY_PREFIX}not-lucia",
        )
        original = (account.email, account.name, account.password, account.demo_key)

        with self.assertRaisesMessage(CommandError, "identity mismatch"):
            self.run_command()

        account.refresh_from_db()
        self.assertEqual(
            (account.email, account.name, account.password, account.demo_key), original
        )
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Idea.objects.count(), 0)

    def test_demo_author_key_with_another_email_is_rejected_without_changes(self):
        account = User.objects.create_user(
            email="someone-else@example.com",
            password="Existing-password-123!",
            name="Mismatched Account",
            role=User.Role.STUDENT,
            demo_key=f"{DEMO_AUTHOR_KEY_PREFIX}{DEMO_STUDENTS[0][0]}",
        )
        original = (account.email, account.name, account.password, account.demo_key)

        with self.assertRaisesMessage(CommandError, "identity mismatch"):
            self.run_command()

        account.refresh_from_db()
        self.assertEqual(
            (account.email, account.name, account.password, account.demo_key), original
        )
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Idea.objects.count(), 0)

    def test_existing_demo_idea_key_with_unexpected_owner_is_rejected(self):
        self.run_command()
        idea = Idea.objects.get(demo_key=f"{DEMO_IDEA_KEY_PREFIX}campus-lost-found-app")
        wrong_owner = User.objects.get(demo_key=f"{DEMO_AUTHOR_KEY_PREFIX}daniel.ruiz")
        idea.owner = wrong_owner
        idea.save(update_fields=["owner"])
        original_idea_count = Idea.objects.count()
        original_user_count = User.objects.count()

        with self.assertRaisesMessage(CommandError, "ownership mismatch"):
            self.run_command()

        idea.refresh_from_db()
        self.assertEqual(idea.owner, wrong_owner)
        self.assertEqual(Idea.objects.count(), original_idea_count)
        self.assertEqual(User.objects.count(), original_user_count)

    def test_remove_ignores_an_unmarked_account_with_reserved_demo_email(self):
        real_author = User.objects.create_user(
            email=demo_email(DEMO_STUDENTS[0][0]),
            password="Real-account-password-123!",
            name="Real Account",
            role=User.Role.STUDENT,
        )
        real_idea = Idea.objects.create(
            title="Existing real idea",
            description="This record predates the demo command.",
            owner=real_author,
        )

        self.run_command("--remove")

        self.assertTrue(User.objects.filter(pk=real_author.pk).exists())
        self.assertTrue(Idea.objects.filter(pk=real_idea.pk).exists())

    def test_remove_preserves_unrelated_ideas_owned_by_demo_authors(self):
        self.run_command()
        demo_author = User.objects.get(demo_key=f"{DEMO_AUTHOR_KEY_PREFIX}lucia.moreno")
        unrelated_idea = Idea.objects.create(
            title="Admin-created follow-up",
            description="This is not a seeded sample idea.",
            owner=demo_author,
        )

        self.run_command("--remove")

        self.assertTrue(Idea.objects.filter(pk=unrelated_idea.pk).exists())
        self.assertTrue(User.objects.filter(pk=demo_author.pk).exists())
        self.assertFalse(
            Idea.objects.filter(demo_key__startswith=DEMO_IDEA_KEY_PREFIX).exists()
        )
        self.assertEqual(
            User.objects.filter(demo_key__startswith=DEMO_AUTHOR_KEY_PREFIX).count(), 1
        )

    def test_remove_preserves_unlisted_records_sharing_demo_key_prefixes(self):
        self.run_command()
        extra_author_key = f"{DEMO_AUTHOR_KEY_PREFIX}archived-contributor"
        extra_idea_key = f"{DEMO_IDEA_KEY_PREFIX}archived-proposal"
        extra_author = User.objects.create_user(
            email="archived-contributor@example.com",
            password=None,
            name="Archived Contributor",
            role=User.Role.STUDENT,
            demo_key=extra_author_key,
        )
        extra_idea = Idea.objects.create(
            title="Archived proposal",
            description="Not part of this command's current fixture.",
            owner=extra_author,
            demo_key=extra_idea_key,
        )
        expected_author_keys = [
            f"{DEMO_AUTHOR_KEY_PREFIX}{username}" for username, _ in DEMO_STUDENTS
        ]
        expected_idea_keys = [
            f"{DEMO_IDEA_KEY_PREFIX}{idea_key}" for idea_key, *_ in DEMO_IDEAS
        ]

        self.run_command("--remove")

        self.assertFalse(User.objects.filter(demo_key__in=expected_author_keys).exists())
        self.assertFalse(Idea.objects.filter(demo_key__in=expected_idea_keys).exists())
        self.assertTrue(User.objects.filter(pk=extra_author.pk, demo_key=extra_author_key).exists())
        self.assertTrue(Idea.objects.filter(pk=extra_idea.pk, demo_key=extra_idea_key).exists())

    def test_missing_categories_stop_the_command(self):
        Category.objects.filter(name="Finance").delete()

        with self.assertRaisesMessage(CommandError, "Missing categories: Finance"):
            self.run_command()
        self.assertEqual(Idea.objects.count(), 0)


@override_settings(ALLOW_ANONYMOUS_ACCESS=True)
class IdeaAcceptanceJourneyTests(TestCase):
    """US001-US004: stored publications and edits are visible to another account."""

    password = "Idea-acceptance-123!"

    @classmethod
    def setUpTestData(cls):
        cls.student = User.objects.create_user(
            email="idea-owner@example.com",
            password=cls.password,
            name="Idea Owner",
            role=User.Role.STUDENT,
        )
        cls.investor = User.objects.create_user(
            email="idea-reader@example.com",
            password=cls.password,
            name="Idea Reader",
            role=User.Role.INVESTOR,
        )
        cls.technology = Category.objects.create(name="Acceptance technology")
        cls.health = Category.objects.create(name="Acceptance health")
        cls.empty_category = Category.objects.create(name="Acceptance empty")

    def setUp(self):
        self.home_url = reverse("ideas:home")
        self.investor_client = Client()
        for client, user in ((self.client, self.student), (self.investor_client, self.investor)):
            response = client.post(
                reverse("accounts:login"),
                {"username": user.email, "password": self.password},
            )
            self.assertRedirects(response, self.home_url)
            self.assertEqual(response.wsgi_request.user.pk, user.pk)

    def publish_idea(self, title, description, category):
        response = self.client.post(
            reverse("ideas:publish"),
            {"title": title, "description": description, "category": category.pk},
        )
        self.assertRedirects(response, self.home_url)
        idea = Idea.objects.get(title=title)
        self.assertEqual(idea.owner, self.student)
        return idea

    def test_investor_can_discover_filter_and_open_published_ideas(self):
        description = (
            "Students share solar panels and exchange practical advice about clean energy. "
            "Each faculty can contribute spare equipment and organise activities with local partners. "
            "The detail page explains the full proposal, including maintenance and fair access."
        )
        idea = self.publish_idea("Campus energy network", description, self.technology)
        other = self.publish_idea("Shared clinic booking", "Book student health visits.", self.health)

        discovery = self.investor_client.get(self.home_url)
        self.assertContains(discovery, idea.title)
        self.assertContains(discovery, other.title)

        filtered = self.investor_client.get(self.home_url, {"category": self.technology.pk})
        self.assertContains(filtered, idea.title)
        self.assertNotContains(filtered, other.title)

        empty = self.investor_client.get(self.home_url, {"category": self.empty_category.pk})
        self.assertContains(empty, "No ideas were found in this category.")
        self.assertNotContains(empty, idea.title)
        self.assertNotContains(empty, other.title)
        self.assertRegex(
            empty.content.decode(),
            rf'<a\b[^>]*href="{re.escape(self.home_url)}"[^>]*>\s*Clear filter\s*</a>',
        )

        cleared = self.investor_client.get(self.home_url)
        self.assertContains(cleared, idea.title)
        self.assertContains(cleared, other.title)
        detail_url = reverse("ideas:detail", args=[idea.pk])
        self.assertContains(cleared, f'href="{detail_url}"')

        detail = self.investor_client.get(detail_url)
        self.assertContains(detail, idea.title)
        self.assertContains(detail, description)
        self.assertContains(detail, self.technology.name)
        self.assertRegex(
            detail.content.decode(),
            rf'<a\b[^>]*href="{re.escape(self.home_url)}"[^>]*>\s*Back to ideas\s*</a>',
        )
        returned = self.investor_client.get(self.home_url)
        self.assertContains(returned, idea.title)
        self.assertContains(returned, other.title)

    def test_owner_edits_are_visible_to_another_user(self):
        idea = self.publish_idea(
            "Solar sharing club", "Students share solar panels.", self.technology
        )
        detail_url = reverse("ideas:detail", args=[idea.pk])
        edit_url = reverse("ideas:edit", args=[idea.pk])
        owner_detail = self.client.get(detail_url)
        self.assertContains(owner_detail, f'href="{edit_url}"')
        self.assertContains(owner_detail, "Edit idea")

        edit_form = self.client.get(edit_url)
        self.assertTemplateUsed(edit_form, "ideas/idea_form.html")
        self.assertContains(edit_form, idea.title)
        self.assertContains(edit_form, idea.description)

        edited_data = {
            "title": "Shared campus energy",
            "description": "Organise shared batteries between faculties.",
            "category": self.health.pk,
        }
        response = self.client.post(edit_url, edited_data)
        self.assertRedirects(response, self.home_url)
        idea.refresh_from_db()
        self.assertEqual(idea.title, edited_data["title"])
        self.assertEqual(idea.description, edited_data["description"])
        self.assertEqual(idea.category, self.health)
        self.assertEqual(idea.owner, self.student)

        discovery = self.investor_client.get(self.home_url)
        self.assertContains(discovery, edited_data["title"])
        self.assertContains(discovery, edited_data["description"])
        self.assertNotContains(discovery, "Solar sharing club")
        detail = self.investor_client.get(detail_url)
        self.assertContains(detail, edited_data["title"])
        self.assertContains(detail, edited_data["description"])
        self.assertContains(detail, self.health.name)
        self.assertNotContains(detail, self.technology.name)


class FeedbackFeatureTests(TestCase):
    def setUp(self):
        self.owner = create_student("feedback-owner@example.com")
        self.investor = User.objects.create_user(
            email="feedback-investor@example.com",
            password="Feedback-123!",
            name="Feedback Investor",
            role=User.Role.INVESTOR,
        )
        self.other_investor = User.objects.create_user(
            email="feedback-other@example.com",
            password="Feedback-123!",
            name="Other Investor",
            role=User.Role.INVESTOR,
        )
        self.idea = Idea.objects.create(
            title="Feedback idea",
            description="An idea that needs feedback.",
            owner=self.owner,
        )
        self.detail_url = reverse("ideas:detail", args=[self.idea.pk])

    def test_investor_can_submit_feedback_and_author_is_displayed(self):
        self.client.force_login(self.investor)
        response = self.client.post(
            reverse("ideas:feedback", args=[self.idea.pk]),
            {"text": "Consider validating the target audience."},
        )

        self.assertRedirects(response, self.detail_url)
        feedback = Feedback.objects.get()
        self.assertEqual(feedback.author, self.investor)
        self.assertContains(self.client.get(self.detail_url), "Feedback Investor")
        notification = Notification.objects.get()
        self.assertEqual(notification.recipient, self.owner)
        self.assertEqual(notification.feedback, feedback)
        self.assertFalse(notification.is_read)

    def test_invalid_feedback_does_not_create_notification(self):
        self.client.force_login(self.investor)
        self.client.post(
            reverse("ideas:feedback", args=[self.idea.pk]),
            {"text": "   "},
        )

        self.assertFalse(Notification.objects.exists())

    def test_notifications_are_only_created_for_the_idea_owner(self):
        other_owner = create_student("other-feedback-owner@example.com")
        other_idea = Idea.objects.create(
            title="Other feedback idea",
            description="Another idea.",
            owner=other_owner,
        )
        self.client.force_login(self.investor)
        self.client.post(
            reverse("ideas:feedback", args=[other_idea.pk]),
            {"text": "A suggestion for this idea."},
        )

        self.assertFalse(Notification.objects.filter(recipient=self.owner).exists())
        notification = Notification.objects.get()
        self.assertEqual(notification.recipient, other_owner)
        self.assertFalse(Notification.objects.filter(recipient=self.investor).exists())

    def test_owner_can_open_notification_and_mark_it_read(self):
        feedback = Feedback.objects.create(
            idea=self.idea,
            author=self.investor,
            text="A useful suggestion.",
        )
        notification = Notification.objects.create(
            recipient=self.owner,
            feedback=feedback,
        )
        self.client.force_login(self.owner)

        response = self.client.get(
            reverse("ideas:open-notification", args=[notification.pk])
        )

        self.assertRedirects(
            response,
            f"{self.detail_url}#feedback-{feedback.pk}",
        )
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)

    def test_user_cannot_open_another_users_notification(self):
        feedback = Feedback.objects.create(
            idea=self.idea,
            author=self.investor,
            text="A useful suggestion.",
        )
        notification = Notification.objects.create(
            recipient=self.owner,
            feedback=feedback,
        )
        self.client.force_login(self.other_investor)

        response = self.client.get(
            reverse("ideas:open-notification", args=[notification.pk])
        )

        self.assertEqual(response.status_code, 404)
        notification.refresh_from_db()
        self.assertFalse(notification.is_read)

    def test_notifications_page_requires_authentication(self):
        response = self.client.get(reverse("ideas:notifications"))

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('ideas:notifications')}",
        )

    def test_empty_feedback_is_rejected(self):
        self.client.force_login(self.investor)
        response = self.client.post(
            reverse("ideas:feedback", args=[self.idea.pk]),
            {"text": "   "},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please enter feedback.")
        self.assertFalse(Feedback.objects.exists())

    def test_private_feedback_is_visible_only_to_owner_and_author(self):
        feedback = Feedback.objects.create(
            idea=self.idea,
            author=self.investor,
            text="This contains a sensitive question.",
            is_private=True,
        )

        self.assertNotContains(self.client.get(self.detail_url), feedback.text)

        self.client.force_login(self.other_investor)
        self.assertNotContains(self.client.get(self.detail_url), feedback.text)

        self.client.force_login(self.investor)
        self.assertContains(self.client.get(self.detail_url), feedback.text)

        self.client.force_login(self.owner)
        owner_response = self.client.get(self.detail_url)
        self.assertContains(owner_response, feedback.text)
        self.assertContains(owner_response, "Private")

    def test_owner_can_reply_to_feedback_and_toggle_status(self):
        feedback = Feedback.objects.create(
            idea=self.idea,
            author=self.investor,
            text="The pricing needs more detail.",
        )
        self.client.force_login(self.owner)

        reply_response = self.client.post(
            reverse("ideas:reply", args=[feedback.pk]),
            {"text": "We will add a pricing estimate."},
        )
        self.assertRedirects(reply_response, self.detail_url)
        reply = Reply.objects.get()
        self.assertEqual(reply.feedback, feedback)
        self.assertEqual(reply.author, self.owner)
        self.assertContains(self.client.get(self.detail_url), reply.text)

        status_response = self.client.post(
            reverse("ideas:feedback-status", args=[feedback.pk])
        )
        self.assertRedirects(status_response, self.detail_url)
        feedback.refresh_from_db()
        self.assertEqual(feedback.status, Feedback.Status.RESOLVED)
        self.assertContains(self.client.get(self.detail_url), "Resolved")

        self.client.post(reverse("ideas:feedback-status", args=[feedback.pk]))
        feedback.refresh_from_db()
        self.assertEqual(feedback.status, Feedback.Status.NORMAL)

    def test_empty_reply_is_rejected(self):
        feedback = Feedback.objects.create(
            idea=self.idea,
            author=self.investor,
            text="Please test this with students.",
        )
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse("ideas:reply", args=[feedback.pk]),
            {"text": "  "},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please enter a reply.")
        self.assertFalse(Reply.objects.exists())

    def test_non_owner_cannot_reply_or_change_status(self):
        feedback = Feedback.objects.create(
            idea=self.idea,
            author=self.investor,
            text="A suggestion.",
        )
        self.client.force_login(self.other_investor)

        reply_response = self.client.post(
            reverse("ideas:reply", args=[feedback.pk]),
            {"text": "Not allowed."},
        )
        self.assertEqual(reply_response.status_code, 403)
        status_response = self.client.post(
            reverse("ideas:feedback-status", args=[feedback.pk])
        )
        self.assertEqual(status_response.status_code, 403)
