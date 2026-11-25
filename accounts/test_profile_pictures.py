from io import BytesIO
from tempfile import TemporaryDirectory

from PIL import Image

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.templatetags.static import static
from django.urls import reverse

from .forms import MAX_AVATAR_SIZE
from .models import Follow, StudentProfile, User


def image_upload(name="profile.png", size=(8, 8)):
    image_data = BytesIO()
    Image.new("RGB", size, color="royalblue").save(
        image_data, format="PNG", compress_level=0
    )
    return SimpleUploadedFile(name, image_data.getvalue(), content_type="image/png")


class TemporaryMediaTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.media_directory = TemporaryDirectory()
        self.settings_override = override_settings(MEDIA_ROOT=self.media_directory.name)
        self.settings_override.enable()
        self.addCleanup(self.media_directory.cleanup)
        self.addCleanup(self.settings_override.disable)

    def create_user(self, email, role, name):
        return User.objects.create_user(
            email=email,
            password="A-valid-password-123!",
            name=name,
            role=role,
        )


class AvatarUploadTests(TemporaryMediaTestCase):
    def setUp(self):
        super().setUp()
        self.student = self.create_user(
            "avatar-student@example.com", User.Role.STUDENT, "Avatar Student"
        )
        self.investor = self.create_user(
            "avatar-investor@example.com", User.Role.INVESTOR, "Avatar Investor"
        )
        self.url = reverse("accounts:upload_avatar")

    def test_student_and_investor_can_upload_valid_images(self):
        for user in (self.student, self.investor):
            with self.subTest(role=user.role):
                self.client.force_login(user)
                response = self.client.post(
                    self.url, {"avatar": image_upload(f"{user.role}.png")}
                )

                if user.is_student:
                    self.assertRedirects(response, reverse("accounts:student_profile"))
                else:
                    self.assertRedirects(response, reverse("ideas:home"))
                user.refresh_from_db()
                self.assertTrue(user.avatar.name.startswith("avatars/"))
                self.assertTrue(user.avatar.storage.exists(user.avatar.name))

    def test_anonymous_user_cannot_upload_and_get_is_not_allowed(self):
        response = self.client.post(self.url, {"avatar": image_upload()})
        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={self.url}",
        )

        self.client.force_login(self.student)
        self.assertEqual(self.client.get(self.url).status_code, 405)
        self.assertFalse(User.objects.exclude(avatar="").exists())

    def test_invalid_image_does_not_replace_existing_avatar(self):
        self.student.avatar.save("original.png", image_upload(), save=True)
        original_name = self.student.avatar.name
        self.client.force_login(self.student)

        response = self.client.post(
            self.url,
            {
                "avatar": SimpleUploadedFile(
                    "invalid.png", b"not image data", content_type="image/png"
                )
            },
            follow=True,
        )

        self.assertContains(response, "Choose a valid image file.")
        self.student.refresh_from_db()
        self.assertEqual(self.student.avatar.name, original_name)
        self.assertTrue(self.student.avatar.storage.exists(original_name))

    def test_oversized_image_does_not_replace_existing_avatar(self):
        self.student.avatar.save("original.png", image_upload(), save=True)
        original_name = self.student.avatar.name
        oversized = image_upload(size=(1350, 1350))
        self.assertGreater(oversized.size, MAX_AVATAR_SIZE)
        self.client.force_login(self.student)

        response = self.client.post(self.url, {"avatar": oversized}, follow=True)

        self.assertContains(response, "The image must be no larger than 5 MB.")
        self.student.refresh_from_db()
        self.assertEqual(self.student.avatar.name, original_name)
        self.assertTrue(self.student.avatar.storage.exists(original_name))

    def test_oversized_dimensions_do_not_replace_existing_avatar(self):
        self.student.avatar.save("original.png", image_upload(), save=True)
        original_name = self.student.avatar.name
        self.client.force_login(self.student)

        for dimensions in ((4097, 1), (1, 4097)):
            with self.subTest(dimensions=dimensions):
                oversized = image_upload("oversized.png", size=dimensions)
                self.assertLess(oversized.size, MAX_AVATAR_SIZE)

                response = self.client.post(self.url, {"avatar": oversized}, follow=True)

                self.assertContains(
                    response,
                    "The image must not exceed 4096 pixels in width or height.",
                )
                self.student.refresh_from_db()
                self.assertEqual(self.student.avatar.name, original_name)
                self.assertTrue(self.student.avatar.storage.exists(original_name))

    def test_posted_user_id_cannot_change_another_accounts_avatar(self):
        target = self.create_user(
            "avatar-target@example.com", User.Role.STUDENT, "Target Student"
        )
        target.avatar.save("target.png", image_upload(), save=True)
        target_name = target.avatar.name
        self.client.force_login(self.investor)

        response = self.client.post(
            self.url,
            {"avatar": image_upload("attacker.png"), "user_id": target.pk},
        )

        self.assertRedirects(response, reverse("ideas:home"))
        self.investor.refresh_from_db()
        target.refresh_from_db()
        self.assertTrue(self.investor.avatar.name.startswith("avatars/"))
        self.assertEqual(target.avatar.name, target_name)


class AvatarDisplayTests(TemporaryMediaTestCase):
    def setUp(self):
        super().setUp()
        self.student = User.objects.create_user(
            email="avatar-display-student@example.com",
            password="A-valid-password-123!",
            name="Display Student",
            role=User.Role.STUDENT,
        )
        self.investor = User.objects.create_user(
            email="avatar-display-investor@example.com",
            password="A-valid-password-123!",
            name="Display Investor",
            role=User.Role.INVESTOR,
        )
        StudentProfile.objects.create(user=self.student)
        Follow.objects.create(investor=self.investor, student=self.student)
        self.default_url = static("accounts/default-avatar.svg")

    def test_default_avatar_is_returned_and_displayed_on_student_views(self):
        self.assertEqual(self.student.avatar_url, self.default_url)

        self.client.force_login(self.student)
        own_profile = self.client.get(reverse("accounts:my_profile"))
        self.assertContains(own_profile, f'src="{self.default_url}"')

        self.client.force_login(self.investor)
        for url in (
            reverse("accounts:investor_profile", args=[self.student.pk]),
            reverse("accounts:student_discovery"),
            reverse("accounts:following"),
        ):
            with self.subTest(url=url):
                self.assertContains(self.client.get(url), f'src="{self.default_url}"')

    def test_saved_avatar_is_displayed_on_student_profile_and_cards(self):
        self.student.avatar.save("display.png", image_upload(), save=True)
        avatar_url = self.student.avatar.url

        self.client.force_login(self.student)
        self.assertContains(
            self.client.get(reverse("accounts:my_profile")),
            f'src="{avatar_url}"',
        )

        self.client.force_login(self.investor)
        for url in (
            reverse("accounts:investor_profile", args=[self.student.pk]),
            reverse("accounts:student_discovery"),
            reverse("accounts:following"),
        ):
            with self.subTest(url=url):
                self.assertContains(self.client.get(url), f'src="{avatar_url}"')

    def test_student_editor_embeds_the_multipart_uploader(self):
        self.client.force_login(self.student)

        response = self.client.get(reverse("accounts:student_profile"))

        self.assertContains(response, 'action="/accounts/profile/avatar/"')
        self.assertContains(response, 'enctype="multipart/form-data"')
        self.assertContains(response, "Upload a new picture")
