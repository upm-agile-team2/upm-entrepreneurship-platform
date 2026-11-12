# Student following - US011

T35 (#67) adds the Follow model and investor-only POST actions for US011 (#49).

Relationships link investor and student accounts, including students without a StudentProfile. Database constraints prevent duplicate pairs and self-following. Model validation checks roles; request handlers enforce session ownership and student-only targets explicitly.

Follow and unfollow are idempotent, require authentication and CSRF protection, and redirect to the student's existing investor-facing profile. Submitted account identifiers and arbitrary redirect URLs do not control ownership or navigation.

Run `python manage.py migrate` to apply the additive `accounts.0007_follow` migration.

Routes: `accounts:follow_student` and `accounts:unfollow_student`.

Verification: `accounts.tests.FollowModelTests` and `accounts.tests.FollowActionTests` (13 tests).

Profile controls, the Following list and remaining acceptance coverage are tracked by the same OpenSpec change for T36 (#68).
