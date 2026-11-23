from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from .models import InvestorProfile, User


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
