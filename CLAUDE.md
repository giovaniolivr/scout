# Scout — Development Rules

## Mocking Policy

**Never mock platform/software internals.** Authentication, sessions, form submission, database writes, URL routing logic, and backend views must always be implemented correctly with real Django code.

The previous pattern of routing users based on email containing "empresa", accepting hardcoded verification codes like `"1111"`, or passing state through URL parameters as a backend substitute is not acceptable going forward.

**Mocking is only allowed for business/domain data.** When a feature requires real data that doesn't exist yet (job listings, candidate profiles, company profiles, feedback entries, scores), it is acceptable to seed the database with fixture data or create objects directly in views temporarily. The infrastructure around that data — the models, views, forms, authentication, and URL routing — must be real.

Examples:
- OK: A job listing page that queries real `Job` objects seeded via fixtures
- NOT OK: A job listing page that renders a hardcoded list in the template or view
- OK: Skipping email sending during development by printing the token to the console
- NOT OK: An email verification step that accepts any code or skips validation entirely

## Django Conventions

- Use Django's built-in authentication system (`django.contrib.auth`) — do not build a custom auth from scratch.
- All user-facing forms must use Django Forms or ModelForms with server-side validation.
- Never trust client-side validation alone — JS validation is UX only.
- Use Django's ORM for all database access — no raw SQL unless absolutely necessary.
- Keep business logic in models or service functions, not in views.

## Code Quality

- No shortcuts that would need to be undone later — do it right the first time for platform code.
- Do not leave `TODO` comments as substitutes for actual implementation on core features.
- All views must handle both GET and POST correctly with proper redirects and error feedback.
