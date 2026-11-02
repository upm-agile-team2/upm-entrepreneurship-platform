"""Load sample ideas for the demo and the Sprint 1 user experiments (T18, #25).

    python manage.py seed_demo_ideas           # create the sample ideas (safe to run again)
    python manage.py seed_demo_ideas --remove  # delete them and their demo authors
"""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from ideas.models import Category, Idea

DEMO_EMAIL_DOMAIN = "demo.upm-ideas.example"

# Fictional authors. They get an unusable password, so nobody can sign in as them.
DEMO_STUDENTS = [
    ("lucia.moreno", "Lucía Moreno"),
    ("daniel.ruiz", "Daniel Ruiz"),
    ("sara.ito", "Sara Ito"),
    ("marco.bianchi", "Marco Bianchi"),
]

# (author, category, title, description). Every category has several ideas so the
# category filter returns meaningful results during the investor experiment.
DEMO_IDEAS = [
    ("lucia.moreno", "Technology", "Campus lost & found app",
     "A mobile app where students report lost and found objects on campus with a photo and the "
     "building where they were found. Security desks confirm the hand-over in the app."),
    ("daniel.ruiz", "Technology", "Lab equipment booking",
     "An online calendar to book shared lab equipment (3D printers, oscilloscopes, soldering "
     "stations) across schools, with reminders and a waiting list."),
    ("sara.ito", "Technology", "AI study buddy for engineering maths",
     "A chatbot trained on UPM course materials that explains step by step how to solve "
     "calculus and algebra exercises, and links each answer to the related lecture."),
    ("marco.bianchi", "Technology", "Smart parking sensors for campus",
     "Low-cost sensors that show free parking spaces in real time on a map, reducing the time "
     "students and staff spend looking for a place every morning."),
    ("lucia.moreno", "Health", "Posture coach for long study sessions",
     "A small clip-on sensor and app that warns students when they slouch and suggests short "
     "stretching breaks during long study sessions."),
    ("daniel.ruiz", "Health", "Healthy menus near campus",
     "A guide to affordable healthy menus in cafés around each UPM campus, with nutritional "
     "information and student discounts negotiated with local businesses."),
    ("sara.ito", "Health", "Peer support for exam stress",
     "An anonymous platform where trained student volunteers offer short chat sessions to "
     "classmates who feel stressed during exam periods."),
    ("marco.bianchi", "Education", "Tutoring marketplace between students",
     "Senior students offer paid or volunteer tutoring sessions for first-year subjects; "
     "reviews help new students choose the right tutor."),
    ("lucia.moreno", "Education", "Flashcards generated from lecture notes",
     "Upload your lecture notes and get spaced-repetition flashcards automatically, shared "
     "with classmates of the same course."),
    ("daniel.ruiz", "Education", "Virtual lab simulations",
     "Browser-based simulations of electronics and chemistry labs so students can practise "
     "before the real session and repeat experiments at home."),
    ("sara.ito", "Sustainability", "Second-hand textbook exchange",
     "A platform to sell, swap or donate used textbooks and lab coats between students, "
     "organised by school and course."),
    ("marco.bianchi", "Sustainability", "Campus composting network",
     "Collect organic waste from cafeterias and turn it into compost for the university "
     "gardens, with a dashboard that shows the kilos diverted from landfill."),
    ("lucia.moreno", "Sustainability", "Shared electric scooters between campuses",
     "A scooter-sharing service reserved for the university community, connecting the "
     "Montegancedo, Moncloa and Vallecas campuses."),
    ("daniel.ruiz", "Finance", "Student budgeting app",
     "An app that helps students plan their monthly budget, track rent and transport costs, "
     "and alerts them about grants and scholarship deadlines."),
    ("sara.ito", "Finance", "Micro-investment club for students",
     "A guided platform where students learn to invest small amounts together, with "
     "simulated portfolios before using real money."),
    ("marco.bianchi", "Finance", "Crowdfunding for student projects",
     "A crowdfunding page for UPM student projects where alumni and companies can fund "
     "prototypes in exchange for early access or sponsorship."),
    ("lucia.moreno", "Social impact", "Volunteer matching for NGOs",
     "Matches students with local NGOs that need technical help (websites, data analysis, "
     "repairs) according to their skills and free hours."),
    ("daniel.ruiz", "Social impact", "Accessible campus map",
     "An interactive map with step-free routes, lifts and accessible toilets on every campus, "
     "updated by the community."),
    ("sara.ito", "Social impact", "Language exchange with refugees",
     "Weekly language exchange meetings between students and refugees living in Madrid, "
     "organised through a simple sign-up app."),
    ("marco.bianchi", "Other", "Student events calendar",
     "One calendar that gathers the events of every UPM student association, with filters by "
     "campus and topic and reminders before each event."),
]


def demo_email(username):
    return f"{username}@{DEMO_EMAIL_DOMAIN}"


class Command(BaseCommand):
    help = "Load sample ideas for the demo and the user experiments, or remove them with --remove."

    def add_arguments(self, parser):
        parser.add_argument(
            "--remove",
            action="store_true",
            help="Delete the sample ideas and their demo authors.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["remove"]:
            self.remove()
        else:
            self.seed()

    def seed(self):
        User = get_user_model()
        categories = {category.name: category for category in Category.objects.all()}
        missing = sorted({category for _, category, _, _ in DEMO_IDEAS} - set(categories))
        if missing:
            raise CommandError(f"Missing categories: {', '.join(missing)}. Run `python manage.py migrate` first.")

        authors = {}
        for username, name in DEMO_STUDENTS:
            author, created = User.objects.get_or_create(
                email=demo_email(username),
                defaults={"name": name, "role": User.Role.STUDENT},
            )
            if created:
                author.set_unusable_password()
                author.save(update_fields=["password"])
            authors[username] = author

        created_ideas = 0
        for username, category, title, description in DEMO_IDEAS:
            _, created = Idea.objects.get_or_create(
                owner=authors[username],
                title=title,
                defaults={"description": description, "category": categories[category]},
            )
            created_ideas += created

        self.stdout.write(self.style.SUCCESS(
            f"Created {created_ideas} sample ideas ({len(DEMO_IDEAS) - created_ideas} already existed)."
        ))

    def remove(self):
        User = get_user_model()
        authors = User.objects.filter(email__in=[demo_email(username) for username, _ in DEMO_STUDENTS])
        deleted_ideas, _ = Idea.objects.filter(owner__in=authors).delete()
        deleted_authors = authors.count()
        authors.delete()
        self.stdout.write(self.style.SUCCESS(
            f"Removed {deleted_ideas} sample ideas and {deleted_authors} demo authors."
        ))
