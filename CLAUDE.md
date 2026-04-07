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

## Visual Identity

Every new page must follow the visual language already established in the project. The reference points are `style.css`, `candidate.css`, and `company.css`. New pages do not need to be identical, but must feel like they belong to the same product — same font (Poppins), same color tokens, same button styles (`btn-black`, `btn-gray`), same card pattern (dark background, subtle border, `border-radius: 12px`), same input style (`.email-input`).

Do not introduce new color palettes, font families, or layout patterns without a clear reason. Variation is allowed within the established system, not outside it.

## Responsiveness

Every page must work correctly at all screen sizes — desktop, tablet, and mobile. Use Bootstrap's grid (`col-*`) and utility classes for layout. Never use fixed pixel widths on containers that hold content. Test mentally at 375px (mobile), 768px (tablet), and 1280px+ (desktop) before considering a layout done.

Specific rules:
- Dashboards and multi-column layouts must collapse gracefully to a single column on small screens.
- Forms must not overflow or require horizontal scrolling on any screen width.
- Navigation must remain usable on mobile.

## Dark and Light Mode

The project uses **explicit light-mode styles only**. Dark mode is handled by the Dark Reader browser extension, which transforms page colors dynamically. Do NOT use `@media (prefers-color-scheme: dark)` overrides — they conflict with Dark Reader and cause the toggle to have no effect.

Rules:
- All CSS must use explicit light-mode colors (e.g., `background-color: #f7f7f7; color: #111`). No CSS variables needed for theming.
- Never leave a background-color unset on major layout elements (`html`, `body`, `main`, cards, inputs). Dark Reader needs explicit colors to detect and transform them.
- The navbar and footer are intentionally always dark (`background-color: #000`) — this is correct and expected.

## Scout Score System

There are two distinct scores. They must never be confused or merged.

### External Score (visible to the candidate)
- Shown on the candidate home page as the "Scout Score"
- Range: 0–100, not cumulative
- Represents a snapshot of the candidate's current standing — what they are doing well and where they can improve
- Calculated from quality signals: feedback received from companies, application outcomes, profile completeness, engagement
- A candidate who does everything right for a short period can score higher than one who uses the app passively for a long time

### Internal Score (hidden — system use only)
- Never displayed to candidates or companies
- Cumulative and absolute — grows over time
- Rewards sustained correct behavior: consistent applications, receiving positive feedback, completing rating cycles, keeping profile up to date
- Used internally for ranking, recommendations, and detecting low-quality or inactive accounts
- Time in the platform matters, but quality matters more: a short-term high-quality user will outrank a long-term low-quality user

## Code Quality

- No shortcuts that would need to be undone later — do it right the first time for platform code.
- Do not leave `TODO` comments as substitutes for actual implementation on core features.
- All views must handle both GET and POST correctly with proper redirects and error feedback.
