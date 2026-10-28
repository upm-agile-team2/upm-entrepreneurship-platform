from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Platform user (student or investor).

    Kept identical to Django's default user for now; the role and the
    remaining fields are added in T02 (US013).
    """
