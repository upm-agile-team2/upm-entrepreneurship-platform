from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.urls import reverse


class AnonymousAccessMiddleware:
    """Apply the optional authenticated-access policy in one place."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not settings.ALLOW_ANONYMOUS_ACCESS and not request.user.is_authenticated:
            public_paths = {
                reverse("accounts:login"),
                reverse("accounts:signup"),
                reverse("accounts:logout"),
            }
            if (
                request.path not in public_paths
                and not request.path.startswith("/admin/")
                and not request.path.startswith(
                    "/" + settings.STATIC_URL.strip("/") + "/"
                )
            ):
                return redirect_to_login(request.get_full_path(), reverse("accounts:login"))
        return self.get_response(request)
