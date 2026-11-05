"""Load sample ideas for the demo and the Sprint 1 user experiments (T18, #25).

    python manage.py seed_demo_ideas           # create the sample ideas (safe to run again)
    python manage.py seed_demo_ideas --remove  # delete them and their demo authors
"""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from ideas.models import Category, Idea

DEMO_EMAIL_DOMAIN = "demo.upm-ideas.example"
DEMO_AUTHOR_KEY_PREFIX = "seed_demo_ideas:author:"
DEMO_IDEA_KEY_PREFIX = "seed_demo_ideas:idea:"

# Fictional authors. They get an unusable password, so nobody can sign in as them.
DEMO_STUDENTS = [
    ("lucia.moreno", "Lucía Moreno"),
    ("daniel.ruiz", "Daniel Ruiz"),
    ("sara.ito", "Sara Ito"),
    ("marco.bianchi", "Marco Bianchi"),
]

# (stable idea key, author, category, title, description). Each main category has
# several ideas for filtering; "Other" has one representative sample.
DEMO_IDEAS = [
    ("campus-lost-found-app", "lucia.moreno", "Technology", "Campus lost & found app",
     "A mobile app where students report lost and found objects on campus with a photo and the "
     "building where they were found. Security desks confirm the hand-over in the app."),
    ("lab-equipment-booking", "daniel.ruiz", "Technology", "Lab equipment booking",
     "An online calendar to book shared lab equipment (3D printers, oscilloscopes, soldering "
     "stations) across schools, with reminders and a waiting list."),
    ("ai-study-buddy", "sara.ito", "Technology", "AI study buddy for engineering maths",
     "A chatbot trained on UPM course materials that explains step by step how to solve "
     "calculus and algebra exercises, and links each answer to the related lecture."),
    ("smart-parking-sensors", "marco.bianchi", "Technology", "Smart parking sensors for campus",
     "Low-cost sensors that show free parking spaces in real time on a map, reducing the time "
     "students and staff spend looking for a place every morning."),
    ("posture-coach", "lucia.moreno", "Health", "Posture coach for long study sessions",
     "A small clip-on sensor and app that warns students when they slouch and suggests short "
     "stretching breaks during long study sessions."),
    ("healthy-menus", "daniel.ruiz", "Health", "Healthy menus near campus",
     "A guide to affordable healthy menus in cafés around each UPM campus, with nutritional "
     "information and student discounts negotiated with local businesses."),
    ("peer-exam-support", "sara.ito", "Health", "Peer support for exam stress",
     "An anonymous platform where trained student volunteers offer short chat sessions to "
     "classmates who feel stressed during exam periods."),
    ("student-tutoring-marketplace", "marco.bianchi", "Education", "Tutoring marketplace between students",
     "Senior students offer paid or volunteer tutoring sessions for first-year subjects; "
     "reviews help new students choose the right tutor."),
    ("lecture-flashcards", "lucia.moreno", "Education", "Flashcards generated from lecture notes",
     "Upload your lecture notes and get spaced-repetition flashcards automatically, shared "
     "with classmates of the same course."),
    ("virtual-lab-simulations", "daniel.ruiz", "Education", "Virtual lab simulations",
     "Browser-based simulations of electronics and chemistry labs so students can practise "
     "before the real session and repeat experiments at home."),
    ("textbook-exchange", "sara.ito", "Sustainability", "Second-hand textbook exchange",
     "A platform to sell, swap or donate used textbooks and lab coats between students, "
     "organised by school and course."),
    ("campus-composting", "marco.bianchi", "Sustainability", "Campus composting network",
     "Collect organic waste from cafeterias and turn it into compost for the university "
     "gardens, with a dashboard that shows the kilos diverted from landfill."),
    ("shared-electric-scooters", "lucia.moreno", "Sustainability", "Shared electric scooters between campuses",
     "A scooter-sharing service reserved for the university community, connecting the "
     "Montegancedo, Moncloa and Vallecas campuses."),
    ("student-budgeting-app", "daniel.ruiz", "Finance", "Student budgeting app",
     "An app that helps students plan their monthly budget, track rent and transport costs, "
     "and alerts them about grants and scholarship deadlines."),
    ("micro-investment-club", "sara.ito", "Finance", "Micro-investment club for students",
     "A guided platform where students learn to invest small amounts together, with "
     "simulated portfolios before using real money."),
    ("student-project-crowdfunding", "marco.bianchi", "Finance", "Crowdfunding for student projects",
     "A crowdfunding page for UPM student projects where alumni and companies can fund "
     "prototypes in exchange for early access or sponsorship."),
    ("ngo-volunteer-matching", "lucia.moreno", "Social impact", "Volunteer matching for NGOs",
     "Matches students with local NGOs that need technical help (websites, data analysis, "
     "repairs) according to their skills and free hours."),
    ("accessible-campus-map", "daniel.ruiz", "Social impact", "Accessible campus map",
     "An interactive map with step-free routes, lifts and accessible toilets on every campus, "
     "updated by the community."),
    ("language-exchange", "sara.ito", "Social impact", "Language exchange with refugees",
     "Weekly language exchange meetings between students and refugees living in Madrid, "
     "organised through a simple sign-up app."),
    ("student-events-calendar", "marco.bianchi", "Other", "Student events calendar",
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
        identity_conflicts = []
        for username, _ in DEMO_STUDENTS:
            email = demo_email(username)
            expected_demo_key = f"{DEMO_AUTHOR_KEY_PREFIX}{username}"
            account_for_email = User.objects.filter(email__iexact=email).first()
            account_for_key = User.objects.filter(demo_key=expected_demo_key).first()
            if account_for_email and account_for_email.demo_key != expected_demo_key:
                identity_conflicts.append(
                    f"reserved email {email} belongs to an account without its expected demo key"
                )
            if account_for_key and account_for_key.email.casefold() != email.casefold():
                identity_conflicts.append(
                    f"demo key {expected_demo_key} belongs to {account_for_key.email}, not {email}"
                )
        if identity_conflicts:
            raise CommandError(
                f"Demo author identity mismatch: {'; '.join(identity_conflicts)}. "
                "No data was changed."
            )

        expected_idea_keys = [
            f"{DEMO_IDEA_KEY_PREFIX}{idea_key}" for idea_key, *_ in DEMO_IDEAS
        ]
        expected_author_keys = {
            username: f"{DEMO_AUTHOR_KEY_PREFIX}{username}"
            for username, _ in DEMO_STUDENTS
        }
        ideas_by_key = {
            idea.demo_key: idea
            for idea in Idea.objects.filter(demo_key__in=expected_idea_keys).select_related("owner")
        }
        idea_owner_conflicts = []
        for idea_key, username, _, title, _ in DEMO_IDEAS:
            idea = ideas_by_key.get(f"{DEMO_IDEA_KEY_PREFIX}{idea_key}")
            expected_owner_key = expected_author_keys[username]
            if idea and idea.owner.demo_key != expected_owner_key:
                idea_owner_conflicts.append(
                    f"demo idea {idea.demo_key} ({title}) belongs to an unexpected author"
                )
        if idea_owner_conflicts:
            raise CommandError(
                f"Demo idea ownership mismatch: {'; '.join(idea_owner_conflicts)}. "
                "No data was changed."
            )

        categories = {category.name: category for category in Category.objects.all()}
        missing = sorted({category for _, _, category, _, _ in DEMO_IDEAS} - set(categories))
        if missing:
            raise CommandError(f"Missing categories: {', '.join(missing)}. Run `python manage.py migrate` first.")

        authors = {}
        for username, name in DEMO_STUDENTS:
            author, _ = User.objects.get_or_create(
                demo_key=f"{DEMO_AUTHOR_KEY_PREFIX}{username}",
                defaults={
                    "email": demo_email(username),
                    "name": name,
                    "role": User.Role.STUDENT,
                },
            )
            if author.has_usable_password():
                author.set_unusable_password()
                author.save(update_fields=["password"])
            authors[username] = author

        created_ideas = 0
        for idea_key, username, category, title, description in DEMO_IDEAS:
            _, created = Idea.objects.get_or_create(
                demo_key=f"{DEMO_IDEA_KEY_PREFIX}{idea_key}",
                defaults={
                    "owner": authors[username],
                    "title": title,
                    "description": description,
                    "category": categories[category],
                },
            )
            created_ideas += created

        self.stdout.write(self.style.SUCCESS(
            f"Created {created_ideas} sample ideas ({len(DEMO_IDEAS) - created_ideas} already existed)."
        ))

    def remove(self):
        User = get_user_model()
        demo_ideas = Idea.objects.filter(
            demo_key__in=[f"{DEMO_IDEA_KEY_PREFIX}{idea_key}" for idea_key, *_ in DEMO_IDEAS]
        )
        deleted_ideas = demo_ideas.count()
        demo_ideas.delete()

        demo_authors = User.objects.filter(
            demo_key__in=[
                f"{DEMO_AUTHOR_KEY_PREFIX}{username}" for username, _ in DEMO_STUDENTS
            ]
        )
        authors_with_unrelated_ideas = Idea.objects.filter(owner__in=demo_authors).values_list(
            "owner_id", flat=True
        ).distinct()
        authors_to_delete = demo_authors.exclude(pk__in=authors_with_unrelated_ideas)
        deleted_authors = authors_to_delete.count()
        preserved_authors = demo_authors.count() - deleted_authors
        authors_to_delete.delete()
        self.stdout.write(self.style.SUCCESS(
            f"Removed {deleted_ideas} sample ideas and {deleted_authors} demo authors; "
            f"kept {preserved_authors} demo authors with unrelated ideas."
        ))
