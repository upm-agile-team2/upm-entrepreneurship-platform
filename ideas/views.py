from django.shortcuts import render


def home(request):
    # Placeholder start page; it becomes the discovery page in T15 (US003).
    return render(request, "ideas/home.html")
