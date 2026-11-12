# Design

## Context

T31 provides `StudentProfile` and the admin-managed `Skill` catalogue. T32 provides `StudentProfileForm` and the authenticated, student-only `accounts:student_profile` GET/POST endpoint. The endpoint binds the form to the current student, validates through `ModelForm.is_valid()`, and supports complete-form updates. T33 must build on this behavior rather than duplicate persistence logic.

T33 (#65) maps to US009 (#47). T34 (#66) maps to US010 (#48). The latter's criteria require investors to open profiles from a student's name or project, see available skills/projects/experience, and handle incomplete profiles.

## Goals and Non-Goals

**Goals:**
- Give students a polished Bootstrap editor and a separate read-only view of their own profile.
- Let authenticated investors follow the student author's name from an idea detail page to a read-only profile view.
- Render missing profiles and empty individual fields without template errors or misleading content.
- Keep profile data limited to the existing profile fields and avoid exposing account credentials/contact data.

**Non-Goals:**
- Add or change models, migrations, settings, authentication, or role definitions.
- Define a schema for JSON project or experience entries.
- Add profile search/discovery, following, counters, notifications, feedback, or investor editing.

## Decisions

- Keep `accounts:student_profile` as the T32 student-only editor endpoint. Add a read-only `accounts:my_profile` route for a student to view their own profile, and an `accounts:investor_profile` route accepting a student user ID. This separates editing from viewing and avoids changing the established T32 form contract.
- Protect the editor and own-profile view with login and a student-role check. Protect the investor profile route with login and an investor-role check; look up only student accounts. Return 403 for a wrong role and 404 for a nonexistent/non-student account. The investor route displays only the student's name and StudentProfile data, never the email or editing action.
- Make the investor profile link visible to authenticated investors on the idea detail page beside the student author's name. Anonymous visitors and students continue to see the name without an investor-specific link.
- Use a shared read-only profile template for own and investor views. Give the own view an edit link; never show it on investor views. If the student has no `StudentProfile` row, show an incomplete-profile state. For an existing profile, show available values and concise empty messages for a missing bio, skills, projects, or experience.
- Render each JSON list entry as escaped, formatted JSON, without assuming keys or imposing an entry schema. Skills are rendered from the existing many-to-many relation. If the skill catalogue is empty, the editor explains that no skills are available to select.
- Upgrade the T32 scaffold to a Bootstrap editor using the shared base template and reusable form field partial. Preserve the form's existing validation and complete-submission semantics. Explain that JSON fields accept arrays, may contain arbitrary JSON values, and can be left blank when empty.

## Security and Privacy

- Route access is role-checked on the server; hiding links is only a presentation detail.
- The editor remains bound to the current user's profile and does not accept a user/profile ID.
- Investor-facing output contains only profile showcase data and student name. Do not include email, account controls, or an edit URL.
- Django template autoescaping remains enabled for names, skill labels, JSON entries, and bio text.

## Risks / Trade-offs

- JSON list entries have no agreed display schema. Displaying escaped JSON preserves all stored values without inventing fields, at the cost of a technical-looking representation.
- A student's profile can be absent entirely because T32 creates it only after a valid save. The investor page therefore supports a student account with no profile row.
- Existing base navigation is shared. Add a student-only own-profile link and leave investor profile access contextual to idea detail.

## Migration Plan

No migration is needed; T33/T34 use the existing T31 schema.
