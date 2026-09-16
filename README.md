# Trade Assistant

A Django web application for traders, intended to grow into a serious
personal trading-performance platform (journal, backtesting, forward
testing, analytics, strategy management) rather than a spreadsheet
replacement.

Developed gradually using an MVP-first approach. See `ARCHITECTURE.md` for
the reasoning behind the project structure.

## Current phase

**Phase 2.3 — Trade Detail page.**

Authenticated users can view the full detail of one of their own trades
at `/journal/trades/<id>/`. Ownership is enforced in the query itself
(`get_object_or_404(Trade, pk=pk, user=request.user)`), so viewing
another user's trade or a non-existent one both return a plain 404.
There's still no trade list — `/journal/trades/<id>/` currently has to be
typed by hand or reached via the ID Django assigns.

## Roadmap

| Phase | Scope |
|-------|-------|
| 0 | Architecture and project structure |
| 1 | Django foundation |
| 2 | Trading Journal MVP *(in progress — 2.1 Trade model, 2.2 Add Trade form, 2.3 Trade Detail done)* |
| 2 | Trading Journal MVP |
| 3 | Screenshots and trade documentation |
| 4 | Dashboard and statistics |
| 5 | Backtesting |
| 6 | Forward Testing |
| 7 | Strategy Management |
| 8 | Psychology / Execution Analysis |
| 9 | Advanced Analytics |
| 10 | Polish, exports, integrations, possible mobile/PWA |

## Development principles

- MVP-first: build the smallest useful version of each feature before
  layering on complexity.
- No premature abstraction. Don't build for a feature that doesn't exist
  yet (e.g. no Strategy model until something actually needs it).
- Keep Journal Trades, Backtests, Backtest Trades, Forward Tests,
  Strategies, and Analytics as logically separate concepts — Analytics
  reads from the others, it isn't a source of trading data itself.
- Timeframe is a first-class field wherever trades are recorded — never an
  afterthought.
- All trading data (journal trades, backtests, forward tests, screenshots,
  notes, analytics) is owned by a user and must stay private to that user.
- SQLite for development; the architecture should allow a clean move to
  PostgreSQL later without restructuring.
- Django templates + plain HTML/CSS/JS. No frontend framework (React,
  Vue, Next.js) unless a compelling architectural reason shows up — there
  currently isn't one.
- Avoid unnecessary third-party dependencies.

## Tech stack

- **Backend:** Python, Django
- **Database:** SQLite (dev), PostgreSQL-ready (prod, not yet configured)
- **Frontend:** Django Templates, HTML, CSS, JS only when necessary
- **Tooling:** Git/GitHub, Cursor

## Project layout

```
trade_assistant/
├── manage.py
├── config/                # Project package: settings, root urls, wsgi/asgi
│   ├── settings/
│   │   ├── base.py        # Shared settings
│   │   ├── dev.py         # Local development (active by default)
│   │   └── prod.py        # Production scaffold (not wired up yet)
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── apps/                  # All local Django apps
│   ├── core/               # Shared/cross-cutting concerns, home route
│   ├── accounts/           # Users, auth (register/login/logout)
│   ├── journal/            # Trading Journal (placeholder; Phase 2+)
│   ├── backtesting/        # Backtesting (placeholder; Phase 5+)
│   └── analytics/          # Analytics (Phase 9+, reads from other apps)
├── templates/              # Project-level shared templates
│   ├── base.html
│   ├── includes/            # navbar.html, messages.html
│   ├── core/                # home.html
│   ├── accounts/            # login.html, register.html
│   ├── journal/              # index.html (placeholder)
│   └── backtesting/          # index.html (placeholder)
├── static/css/base.css     # Minimal dark stylesheet
├── media/                  # User uploads (screenshots, etc. — Phase 3+)
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── ARCHITECTURE.md
```

See `ARCHITECTURE.md` for why it's organized this way.

## Running locally

1. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Apply migrations:
   ```bash
   python manage.py migrate
   ```
4. (Optional) create an admin account:
   ```bash
   python manage.py createsuperuser
   ```
5. Run the dev server:
   ```bash
   python manage.py runserver
   ```
6. Visit `http://127.0.0.1:8000/` — unauthenticated users are redirected to
   `/accounts/login/`. Register an account at `/accounts/register/`, or log
   in, to reach the home page. `http://127.0.0.1:8000/admin/` is also
   available for superusers.

Development settings (`config.settings.dev`) work out of the box with no
`.env` file. `.env.example` documents the variables `config.settings.prod`
will eventually need.

### Running tests

Run tests with explicit app labels rather than a bare `manage.py test`:

```bash
python manage.py test core accounts journal
```

A bare `python manage.py test` currently reports 0 tests — see
ARCHITECTURE.md ("Test discovery" note) for why, and don't be alarmed by
it; the command above is the one that actually runs the suite.

## Authentication

Built entirely on Django's built-in `django.contrib.auth`:

- **Register** (`/accounts/register/`) — a small custom view + form
  (`accounts.forms.RegisterForm`, subclassing `UserCreationForm`) that
  creates a normal `auth.User` and logs the new user in immediately.
- **Login** (`/accounts/login/`) — Django's built-in `LoginView`, pointed
  at a project template.
- **Logout** (`/accounts/logout/`) — Django's built-in `LogoutView`
  (POST-only, triggered from a small form in the navbar).

No custom User model and no third-party auth package — the default
`auth.User` model is sufficient for Phase 1 and keeps things simple.

## URL structure

```
/                     core home (login required)
/accounts/register/   registration
/accounts/login/      login
/accounts/logout/     logout (POST)
/journal/             journal landing page + Add Trade link (login required)
/journal/trades/add/  Add Trade form (login required)
/journal/trades/<id>/ Trade Detail page, owner-only (login required)
/backtesting/          placeholder — "Coming in Phase 5" (login required)
/admin/                Django admin
```

## Django apps

- **core** — shared/cross-cutting functionality: the authenticated home
  page and the base template/navbar/messages includes.
- **accounts** — registration/login/logout views, forms, and templates.
- **journal** — Trading Journal. Has a `Trade` model (Phase 2.1, in Django
  admin for inspection), an Add Trade form at `/journal/trades/add/`
  (Phase 2.2), and a Trade Detail page at `/journal/trades/<id>/`
  (Phase 2.3). No trade list/edit/delete yet.
- **backtesting** — Backtests and Backtest Trades. Placeholder index page
  only; models start in Phase 5.
- **analytics** — derives performance data from journal/backtesting/forward
  test data. Still an empty shell — nothing to derive from yet.

No trading data models exist yet — that's intentional and starts in
Phase 2.
