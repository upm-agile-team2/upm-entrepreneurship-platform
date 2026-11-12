# Student profile discovery - US012

T37 (#69) and T38 (#70) implement the three acceptance criteria of US012 (#50).

## T37: backend filtering

The directory population is saved StudentProfile records belonging to active student accounts. Empty or incomplete saved profiles are included; student accounts without a saved profile and profiles attached to inactive or investor accounts are excluded.

`accounts.discovery.StudentProfileFilterForm` validates one optional skill against the current catalogue. No selection means all skills. Invalid identifiers are field errors. A valid skill without matching eligible profiles produces an empty result.

`accounts.discovery.student_profiles` selects the related user, prefetches skills and sorts by case-insensitive student name, then user ID. Loading names and skills for all results uses two queries. The directory query does not record profile visits and needs no schema or data migration.

Database-backed coverage: `accounts.test_discovery.ProfileDiscoveryBackendTests`.
