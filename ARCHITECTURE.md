# Architecture — Phase 0

This document explains the structural decisions made in Phase 0 and why.
It is not a description of features (there are none yet) — it's a
description of the skeleton those features will be built into.

## 1. Project layout: `config/` + `apps/`

The Django *project* package is named `config` rather than
`trade_assistant`, and it only holds settings, root URLs, and WSGI/ASGI
entrypoints. All product code lives under `apps/`, one directory per
Django app.

Why:
- Separates "project plumbing" (settings, routing config) from "product
  code" (apps) at a glance.
- `apps/` is added to `sys.path` in `config/settings/base.py`, so each app
  is importable as `journal`, `backtesting`, etc. instead of
  `apps.journal`. This keeps `INSTALLED_APPS`, imports, and
  `app_name`/`name` values short throughout the codebase as more apps are
  added in later phases.
- A flat `apps/` directory scales fine for the ~5 apps this project plans
  to have. If that ever grows much larger, it can be revisited — but
  doing so now would be premature.

## 2. Settings: `base.py` / `dev.py` / `prod.py`

`config/settings/` is a package, not a single `settings.py`:

- `base.py` — everything that's the same in every environment
  (`INSTALLED_APPS`, `MIDDLEWARE`, templates, static/media config, password
  validators, etc.). Deliberately does **not** define `DEBUG`,
  `ALLOWED_HOSTS`, or `DATABASES` — those differ per environment and
  defining them here would invite accidentally using dev-only values in
  production later.
- `dev.py` — imports `base`, sets `DEBUG = True`, SQLite database, console
  email backend. This is what `manage.py`, `wsgi.py`, and `asgi.py` point
  to by default (`DJANGO_SETTINGS_MODULE=config.settings.dev`), so the
  project runs locally with zero configuration.
- `prod.py` — a scaffold only, not currently used or exercised. Reads
  database credentials, allowed hosts, and the secret key from environment
  variables, and points `DATABASES` at PostgreSQL. Kept here now so the
  eventual production/PostgreSQL move (task 10 in the roadmap) is a matter
  of filling in environment variables and switching
  `DJANGO_SETTINGS_MODULE`, not restructuring settings from scratch.

A tiny `env()` helper in `base.py` reads `os.environ` with a default. It
is intentionally not a third-party `.env` library (like `django-environ`
or `python-dotenv`) — Phase 0 doesn't need one, and adding a dependency
for something four lines of stdlib code can do would go against "avoid
unnecessary third-party dependencies." `.env.example` documents what
`prod.py` will eventually read; it can be swapped for a real loader later
if that becomes worth it.

## 3. Environment variables

`.env.example` lists the variables `prod.py` expects
(`DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, `DATABASE_*`). `dev.py`
needs none of them. `.env` itself is gitignored so real secrets never get
committed; `.env.example` is the checked-in template.

## 4. Apps created in Phase 0

Five apps exist as empty shells (default `startapp` output, plus a
minimal `views.py`/`urls.py` in `core` to prove the project is runnable):

- **core** — shared/cross-cutting concerns that don't obviously belong to
  one domain app (currently: the placeholder home route). Expect small
  shared utilities here later (base templates context, common template
  tags, etc.), not business logic.
- **accounts** — users and authentication. Will own the ownership
  relationships described below.
- **journal** — Journal Trades (Phase 2+).
- **backtesting** — Backtests and Backtest Trades (Phase 5+).
- **analytics** — derives statistics from journal/backtesting/forward-test
  data (Phase 9, though a lighter dashboard-stats version may land in
  Phase 4). Deliberately has no models of its own beyond what it needs to
  cache/derive — it is a consumer of other apps' data, not a source of
  trading data.

No **forward testing** app was created yet. Forward Testing (Phase 6)
will very likely reuse most of the Journal's trade-shaped data model, so
whether it becomes its own app, lives inside `journal`, or becomes a mode
of an existing model is a decision deferred to when that phase actually
starts — creating an empty `forward_testing` app now would be guessing at
a structure before the requirements are known.

No **strategies** app was created yet either, for the same reason —
Strategies are explicitly out of scope until Phase 7 unless clean
architecture in an earlier phase requires a minimal version sooner.

## 5. URLs

`config/urls.py` is a thin router: currently just `admin/` and an include
of `core.urls`. The comment in that file documents the intended pattern
for future phases — each app gets its own `urls.py`, included with a URL
prefix from the root. No journal/backtesting/etc. URLs exist yet because
those apps have no views yet.

## 6. Templates and static/media files

- `templates/` (project root) — shared/base templates (site layout,
  navigation) that don't belong to one app. Registered in
  `TEMPLATES[0]["DIRS"]`.
- Each app can additionally keep `apps/<app>/templates/<app>/...` via
  Django's `APP_DIRS = True` for templates specific to that app. Standard
  Django convention, kept so app-specific templates don't have to live in
  the shared directory.
- `static/` (project root) — shared static assets (site-wide CSS/JS).
  `STATICFILES_DIRS` points here. `STATIC_ROOT` for `collectstatic` is
  intentionally not set yet — it's a production concern and doesn't need
  to exist for `runserver`.
- `media/` — user uploads. Configured (`MEDIA_URL`/`MEDIA_ROOT`) even
  though nothing uploads files yet, since Journal/Backtest Trades will
  need screenshot storage starting Phase 3, and getting the path right
  now costs nothing.

## 7. Database

SQLite for development, per the tech stack decision. `prod.py`'s
PostgreSQL config is unused scaffolding — `psycopg` is **not** in
`requirements.txt` yet, since installing a driver for a database
that isn't in use yet would be an unnecessary dependency. It should be
added when `prod.py` is actually put into use.

No models exist yet, so there's nothing to migrate beyond Django's own
built-in apps (`admin`, `auth`, `contenttypes`, `sessions`) — already
applied.

## 8. Ownership / multi-user privacy (design note, not implemented)

The roadmap requires that a user's journal trades, backtests, backtest
trades, forward tests, screenshots, notes, and analytics never be visible
to another user. Nothing enforces this yet since no data-holding models
exist. The intended approach for later phases:

- Every trading-data model (Journal Trade, Backtest, Backtest Trade,
  Forward Test, Strategy, and anything Analytics stores) gets a
  `ForeignKey` to the user (`accounts`/`django.contrib.auth.User`) that
  owns it, set at creation and never exposed for editing.
- Querysets in views/managers must always filter by the requesting user.
  This is a discipline to apply consistently once real views exist, not
  something Phase 0 can enforce structurally — noted here so it isn't
  forgotten when Phase 2 starts.

## 9. What was deliberately NOT decided yet

Per the roadmap's Phase 0 scope, the following are postponed:

- Journal Trade / Backtest / Backtest Trade / Forward Test / Strategy
  models and their fields.
- Exact ownership/`ForeignKey` implementation (design noted above, not
  built).
- Analytics calculations, dashboard statistics, charts.
- Screenshot storage details beyond having a `media/` directory
  configured (validation, thumbnailing, storage backend).
- Whether Forward Testing becomes its own app or lives inside `journal`.
- Django REST Framework / API layer — nothing in the roadmap has asked
  for one yet.
- Authentication flow details (signup, password reset, etc.) beyond the
  `accounts` app existing as a placeholder.
- `collectstatic`/`STATIC_ROOT`, deployment target, WSGI server choice,
  containerization — all production concerns for when `prod.py` is
  actually used.

## 10. Django/Python versions

- Python 3.12.3
- Django 6.1.1 (latest available at time of setup)

`requirements.txt` pins `Django==6.1.1`.

---

# Phase 1 additions — Django foundation

Phase 0's architecture was kept as-is. Everything below is additive.

## 11. Authentication: built-in, no custom User model

Registration/login/logout all use `django.contrib.auth`:

- Login/logout are Django's built-in `LoginView`/`LogoutView`, wired
  directly in `accounts/urls.py`. No custom view code needed for these —
  they already do exactly what Phase 1 requires.
- Registration is a small custom view (`accounts.views.register`) because
  Django has no built-in registration view, but it delegates all the real
  work to `UserCreationForm` (subclassed as `accounts.forms.RegisterForm`
  only to add an optional email field). On success it logs the new user in
  and redirects home, so registering doesn't require a separate login
  step.
- No custom `User` model. Phase 0 didn't establish one, and the default
  `auth.User` is sufficient for everything Phase 1 needs. Introducing a
  custom user model now, before any requirement demands it (e.g. extra
  profile fields), would be exactly the kind of premature architecture
  the project's principles warn against. If a real need shows up later
  (e.g. broker connection metadata per user), a `Profile` model with a
  `OneToOneField` to `User` is the lower-risk path — swapping
  `AUTH_USER_MODEL` after the project has real data is painful and best
  avoided unless truly necessary.
- `LOGIN_URL`, `LOGIN_REDIRECT_URL`, and `LOGOUT_REDIRECT_URL` are set in
  `config/settings/base.py` (not dev/prod-specific) since they're
  structural, not environment-specific.

## 12. URL structure: `/accounts/...` prefix

The task brief's example URLs were unprefixed (`/login/`, `/register/`,
`/logout/`). This implementation instead uses Django's common convention
of prefixing auth URLs under `/accounts/` (`/accounts/login/`, etc.),
matching the `accounts` app name and Django's own `LOGIN_URL` default.
This is a deliberate, minor deviation from the brief's literal example —
the brief itself calls the URL structure illustrative ("can be simple,
for example") — chosen because it's the standard Django pattern and reads
more clearly as the project grows (`/journal/...`, `/backtesting/...`,
`/accounts/...` all namespaced by app).

## 13. Home page requires login

`core.views.home` is decorated with `@login_required`
(`LOGIN_URL = "accounts:login"`), so visiting `/` while unauthenticated
redirects to `/accounts/login/?next=/`. This satisfies "unauthenticated
users should be able to access Login/Register; authenticated users should
be able to access the main application" without needing a separate
public landing page — there's no marketing/landing content to show yet,
so redirecting straight to login is the simplest correct behavior for a
personal tool. A dedicated public landing page can be added later if this
becomes a multi-tenant product that needs one.

## 14. Journal / Backtesting placeholders

`journal.views.index` and `backtesting.views.index` are trivial
`@login_required` views rendering a one-line "Coming in Phase 2" /
"Coming in Phase 5" template. This exists purely so the navbar's links
resolve to something and the URL/app structure for those apps is proven
out before real functionality is built — no models, forms, or logic
beyond that.

## 15. Templates

- `templates/base.html` — the single shared layout (nav + messages +
  content block). Loads `static/css/base.css`.
- `templates/includes/navbar.html` — auth-aware: shows Login/Register
  when anonymous, Home/Journal/Backtesting/username/Logout when
  authenticated. Logout is a POST form (Django's `LogoutView` requires
  POST), not a link, to avoid a GET request logging someone out.
- `templates/includes/messages.html` — renders Django's messages
  framework output; nothing currently triggers a message, but it's wired
  up so future views (e.g. "trade saved") can use `messages.success(...)`
  without template changes.
- Each app keeps its templates under `templates/<app_name>/` at the
  project level (not `apps/<app>/templates/`) for Phase 1's small template
  count — this can be revisited if an app's templates grow enough to
  warrant colocating them with the app.

## 16. Static files

`static/css/base.css` is a minimal dark stylesheet (CSS variables, no
build step, no framework) — enough to prove `{% static %}` resolves
correctly and to make the auth-only foundation legible. No
`django-widget-tweaks`/CSS framework dependency was added, since none of
that is needed yet.

## 17. Test discovery fix

`apps/__init__.py` was added (an empty file) so that `python manage.py
test` with no arguments can discover tests inside `apps/<name>/tests.py`.
Without it, Python's default test discovery — which requires each
directory it walks to be a package — stopped at `apps/` because that
directory had no `__init__.py`, even though each app inside it did. This
doesn't change how apps are imported (still top-level `accounts`,
`journal`, etc., via the `sys.path` insert from Phase 0) — it only makes
`apps/` itself walkable by the test runner. Confirmed necessary by
testing both ways: `manage.py test` found 0 tests before this file
existed and 7 after.

## 18. Dependencies

No new dependencies. Still just `Django==6.1.1`. Everything in Phase 1
(auth, forms, templates, static files) is built-in Django functionality.

## 19. What was deliberately NOT done in Phase 1

- No custom User model or user profile model (see §11).
- No password reset / email verification flow — not required by the
  brief, and email sending infrastructure doesn't exist yet.
- No permissions/roles beyond Django's default `is_staff`/`is_superuser`
  for admin access.
- No ownership `ForeignKey`s on any trading model — there are still no
  trading models. The intended pattern (every trading-data model gets a
  `ForeignKey` to `User`, querysets always filtered by request.user) is
  unchanged from the Phase 0 design note and still applies once Phase 2
  introduces the first real model.
- No visual design polish beyond the minimal stylesheet.
- No production settings changes — `config/settings/prod.py` is untouched
  from Phase 0.

---

# Phase 2.1 additions — Journal Trade database model

Phase 1's auth system, templates, navigation, and URLs were untouched.
This milestone only adds a model (+ admin registration + migration +
tests) to the existing `journal` app.

## 20. Trade model

`journal.models.Trade` — one row per real trade recorded by a user.
Deliberately data-only: no `save()`-time calculations, no properties for
P/L/R-multiple/duration. Those are derived later (Phase 2.x) from the raw
fields stored here (entry/exit/stop/take-profit/position size).

- **Ownership**: `user = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name="journal_trades")`.
  Uses `settings.AUTH_USER_MODEL` rather than importing `django.contrib.auth.models.User`
  directly — standard Django practice so the FK keeps working if the
  project ever does introduce a custom user model later (see §11; still
  not needed now, this is just not making the FK harder to change later).
  `on_delete=CASCADE` — deleting a user deletes their trades, consistent
  with "a user's trading data belongs to them."
- **Choices**: `Direction` (BUY/SELL), `Timeframe` (M1/M5/M15/M30/H1/H4/D1),
  `Result` (OPEN/WIN/LOSS/BREAKEVEN) — all `models.TextChoices`, stored as
  short strings so the raw DB value stays human-readable (useful for
  admin/debugging) without needing a join to a lookup table for a small
  fixed set of values.
- **Decimal precision**:
  - `position_size`: `max_digits=12, decimal_places=4` — covers
    fractional lot sizes (e.g. `0.01`) and larger position sizes (e.g.
    crypto quantities) without rounding.
  - `entry_price` / `stop_loss` / `take_profit` / `exit_price`:
    `max_digits=14, decimal_places=5` — 5 decimal places covers forex
    pip-level precision (e.g. `1.08453`) and gold/crypto prices with
    room for larger integer parts (index/crypto prices in the tens of
    thousands).
  - `risk_amount`: `max_digits=12, decimal_places=2` — a currency amount,
    2 decimal places is standard for money.
  - All use `DecimalField`, never `FloatField`, per the brief.
- **Optional fields**: `stop_loss`, `take_profit`, `exit_price`,
  `risk_amount` (`null=True, blank=True` — genuinely absent, not just
  "empty text"). `strategy`, `session`, `notes`, `tags` are optional text
  (`blank=True`, no `null=True` — Django convention: `null=True` on
  `CharField`/`TextField` creates a second "empty" state (`NULL` vs `""`)
  that's rarely useful).
- **`strategy`**: plain `CharField`, no FK to a Strategy model — per the
  brief, that model doesn't exist yet.
- **`tags`**: plain `CharField` (comma-separated, e.g. "breakout, news"),
  no separate tagging model/library — per the brief.
- **`session`**: plain `CharField` rather than choices — trading sessions
  (Asian/London/NY, or a broker's custom session names) aren't
  standardized enough across brokers/traders to hardcode a choice list
  yet; free text avoids blocking someone whose broker uses different
  session names. Can become choices later if a consistent set emerges.
- **Meta**: `ordering = ["-date", "-time"]` (most recent trade first — the
  natural default for a journal). One composite index on `(user, -date)`
  since "this user's trades, most recent first" is the only access
  pattern that exists right now; no other indexes added speculatively.
- **`__str__`**: `"{asset} {direction} {date} ({result display})"`, e.g.
  `"XAUUSD BUY 2026-09-01 (Win)"`.

## 21. Admin registration

`journal.admin.TradeAdmin` registers `Trade` with a list display, a few
list filters (direction/timeframe/result), and search fields
(asset/strategy/tags/notes). This is purely so trade data can be
inspected/verified through Django admin during development — it is not a
journal UI and doesn't count as the "Add Trade / Trade list" pages the
brief excludes; those are user-facing app views/templates, which don't
exist yet.

## 22. Migration

`apps/journal/migrations/0001_initial.py` — one migration creating the
`Trade` table. No data migration needed (no pre-existing trade data).

## 23. Test discovery — Phase 1 fix reverted

Phase 1 added an empty `apps/__init__.py` so bare `python manage.py test`
(no args) could discover tests under `apps/<name>/tests.py`. With a real
model now present, that fix broke: filesystem-based discovery imported
the test module as `apps.journal.tests`, whose relative import
(`from .models import Trade`) loaded a *second*, differently-named copy
of `journal.models` (`apps.journal.models`) alongside the one Django's
app registry already loaded as `journal.models` (via the `sys.path`
insert from `config/settings/base.py`). Django's model machinery requires
a model's class to match an app registered in `INSTALLED_APPS`
(`"journal"`, not `"apps.journal"`), so this raised
`RuntimeError: Model class apps.journal.models.Trade doesn't declare an
explicit app_label and isn't in an application in INSTALLED_APPS`.

This is a direct consequence of the Phase 0 decision to make `apps/*`
importable as top-level packages (`journal`, not `apps.journal`) — it
works cleanly as long as nothing also makes `apps/` itself a package for
filesystem-based discovery to walk into.

Rather than patch around this with another workaround, `apps/__init__.py`
was removed again and this document says plainly: run tests with
explicit app labels — `python manage.py test core accounts journal` (see
README's "Running tests" section) — which was already confirmed to work
correctly in Phase 1's own verification, before the `__init__.py` fix was
added. Bare `python manage.py test` reports "Found 0 test(s)" and is a
known, documented limitation rather than a silently-broken feature. Fixing
this properly (e.g. a custom test command that defaults to explicit
labels) is possible but is more machinery than this project needs right
now — noted here rather than built.

## 24. Dependencies

None added. Still just `Django==6.1.1`.

## 25. What was deliberately NOT done in Phase 2.1

- No Add/Edit/Delete/List/Detail trade views, forms, or templates.
- No filters or search UI (the admin's filters are a debugging aid, not a
  journal feature).
- No P/L, R-multiple, risk/reward, or duration calculations — the raw
  fields needed for them are stored, nothing is computed yet.
- No screenshots/attachments.
- No Strategy model — `strategy` stays a plain text field.
- No changes to Journal's `index` view/template/URL — `/journal/` is
  still the Phase 1 "Coming in Phase 2" placeholder.

---

# Phase 2.2 additions — Add Trade form

Phase 1's auth/templates/nav and Phase 2.1's `Trade` model were untouched
except for one required change to the Journal landing page (see §27).

## 26. TradeForm

`journal.forms.TradeForm` is a plain `ModelForm` on `Trade`, listing
exactly the fields the brief asked for. `user`, `created_at`, and
`updated_at` are simply never listed in `Meta.fields` — there is no
`exclude` list to maintain and no risk of a submitted `user` value ever
reaching the form, because Django never builds a form field for it in the
first place. `date`/`time` get HTML5 `<input type="date">`/`<input
type="time">` widgets (native browser pickers, no JS); `notes` gets a
4-row `Textarea`. No other customization — validation is entirely
Django's default model/field validation (required vs `blank=True`,
`DecimalField` precision, choice validation).

## 27. add_trade view and ownership

`journal.views.add_trade` is `@login_required`. On `POST`, it builds the
form from `request.POST`, and if valid calls `form.save(commit=False)`,
sets `trade.user = request.user`, then saves. Because the form has no
`user` field, there is nothing to override — a malicious payload
including a `user` key is simply ignored (confirmed by
`test_submitted_user_field_is_ignored`). This is the standard Django
pattern for "server always chooses the owner" and needed no extra
sanitization.

On success: `messages.success(request, "Trade added successfully.")`,
then `redirect("journal:index")` — there's no Trade Detail page yet, so
the brief specifies redirecting back to Journal.

`journal.views.index` itself is unchanged in behavior, but its template
changed (see next section), which is why one existing Phase 1 test
needed updating — not because Phase 1 broke, but because the brief
explicitly asked for the placeholder text to be replaced.

## 27a. Journal landing page — required content change

The brief explicitly requires updating the Journal page to show the "Add
Trade" link and a message that the trade list is coming next, replacing
the old "Coming in Phase 2" placeholder text. `templates/journal/index.html`
was updated accordingly. This broke
`core.tests.PlaceholderPagesTests.test_journal_placeholder`, which
asserted the old placeholder text — that test was updated to assert on
"Add Trade" instead, since the underlying behavior (Journal page loads,
200 OK, login required) is unchanged and still covered; only the exact
wording changed, on purpose, per this milestone's own instructions.

## 28. Templates

- `templates/journal/index.html` — now shows "The trade list is coming
  in the next milestone." plus an "Add Trade" link, using the existing
  `.quick-links` style from Phase 1's home page.
- `templates/journal/trade_form.html` — new. Extends `base.html`, uses
  `<fieldset>`/`<legend>` to group fields into the four sections the
  brief suggested (Trade Information / Position / Trade Details / Notes),
  and renders each field with `{{ form.field.as_field_group }}` (Django
  6's built-in helper that renders label + widget + help text + errors
  together) rather than `form.as_p`, so the fieldset grouping is
  possible. A small CSS addition in `static/css/base.css` styles
  `fieldset`/`legend` to match the existing dark theme — no new visual
  system, just enough to make the grouping legible.

## 29. Dependencies

None added.

## 30. What was deliberately NOT done in Phase 2.2

- No Trade list, detail, edit, or delete views/templates.
- No filters or search.
- No P/L, R-multiple, risk/reward, or duration validation/calculation —
  only the model's own field-level validation runs.
- No Strategy model or validation against one — `strategy` stays free
  text, exactly as the form's underlying field.
- No screenshot/attachment upload.
