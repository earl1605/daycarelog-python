# DaycareLog (Django)

Barangay Daycare Enrollment, Attendance, and Health/Immunization Tracking System - Django + Supabase (PostgreSQL) implementation.

This is a separate course deliverable from the sibling Spring Boot + React DaycareLog project. It uses Django as the backend framework with server-rendered templates and a **custom-built dashboard** - the Django Admin app is not installed at all, per the assignment requirement that it not be used as the primary interface.

See [`SRS.md`](SRS.md) for the full Software Requirements Specification (functional/non-functional requirements, user roles, and data model).

## Tech Stack

- Django 6, Django REST Framework (mobile/API access mirroring the core dashboard actions)
- Supabase (PostgreSQL) via the Transaction Pooler
- dnspython (MX-record lookup for email-domain validation at registration)
- python-decouple for environment configuration
- Tailwind CSS, compiled to a static file at build time (not the CDN Play script - see "Rebuilding CSS" below)
- WhiteNoise for static file serving

## Project Structure

```
daycarelog_django/   Project settings, root URLconf
accounts/             Custom User model (PARENT/STAFF/ADMIN roles), registration, login/logout
enrollment/           GuardianProfile, Child, HealthRecord, Immunization, Attendance models; EPI schedule and WHO nutritional-status classification
dashboard/            Custom staff/admin dashboard and parent portal views/forms - the primary UI
api/                  Django REST Framework endpoints mirroring the dashboard's core actions
templates/            Server-rendered HTML templates (dashboard/, accounts/, layouts/)
static/               Tailwind input/output CSS, JS, images
```

## Roles

- **STAFF/BHW** - created through public self-registration (`/accounts/register/`) and can log in immediately. Full dashboard access: children, attendance, health records, guardians, immunizations, reports, settings.
- **ADMIN** - functionally identical to STAFF, plus Account Management (creating other STAFF/ADMIN accounts). Created only by an existing STAFF/ADMIN user from the dashboard - never through public registration.
- **PARENT/GUARDIAN** - created only by an existing STAFF/ADMIN from the dashboard's Guardians page, together with a specific child, and handed a one-time temporary password. Parents see only their own linked children, read-only: home overview, attendance, health records, and immunizations.

Public self-registration **always** creates a STAFF account and **never** PARENT or ADMIN, regardless of submitted data - claiming a specific child requires staff verification, so Parent/Guardian accounts cannot be self-service.

## Setup

1. Clone the repository and enter the project folder:
   ```
   git clone https://github.com/earl1605/daycarelog-python.git
   cd daycarelog-python
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # macOS/Linux
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and fill in your Supabase database credentials (use the **Transaction Pooler** connection details from Supabase Project Settings > Database > Connection Pooling):
   ```
   copy .env.example .env
   ```

5. Run migrations:
   ```
   python manage.py migrate
   ```

6. Build static files (required at least once so templates that reference `static/css/tailwind-built.css` don't 404 locally):
   ```
   python manage.py collectstatic --noinput
   ```

7. Run the development server:
   ```
   python manage.py runserver
   ```

8. Visit `http://127.0.0.1:8000/` for the landing page. Register a Staff/BHW account at `/accounts/register/` and sign in right away. Parent/Guardian accounts are created by Staff/Admin from the dashboard's Guardians page instead (see Roles above).

There is no Django Admin panel to fall back on - `django.contrib.admin` is intentionally left out of `INSTALLED_APPS`. All record management goes through `/dashboard/`.

## Rebuilding CSS

Tailwind is compiled to a static file (`static/css/tailwind-built.css`) at build time, not loaded from the CDN Play script - this makes every page load much faster since the browser doesn't recompile the whole utility set on every navigation. If you add new Tailwind classes to any template, rebuild it:

```
npm install
npx tailwindcss -i static/css/tailwind-input.css -o static/css/tailwind-built.css --minify
```

Then commit the updated `tailwind-built.css`.

## Running Tests

```
python manage.py test --keepdb
```

`--keepdb` is required locally: the Supabase transaction pooler holds the test connection open, which makes Django's normal `DROP DATABASE` teardown fail. The suite covers three end-to-end workflows (registration/login, staff enrollment-through-attendance-through-health-through-immunization, and parent-portal access) plus validation/duplicate-record/unauthorized-access negative-path tests - see `accounts/tests.py` and `dashboard/tests.py`.

## Deploying to Vercel

`build_files.sh` no longer runs migrations - it only installs dependencies and collects static files. Run migrations locally against Supabase before deploying:

```
python manage.py migrate
```

This keeps preview/production builds on Vercel from ever touching the live schema. Deploy only after migrating locally and confirming the change is safe.

## Features

- **Registration** - Staff/BHW self-registration with disposable-email and invalid-mail-domain rejection, duplicate-email prevention, and hashed passwords.
- **Login/Logout** - Email-based authentication with generic error messages (no user enumeration) and role-based redirect after login.
- **Children** - full CRUD (add/edit/delete) with photo, blood type, medical conditions, and enrollment status; a per-child detail page tabbing Profile, Health history, and Attendance history, plus live immunization-dose progress against the DOH EPI schedule.
- **Guardians** - staff provision a new Parent/Guardian account and profile together in one step (temporary password shown once), or edit/remove an existing one.
- **Attendance** (core feature) - Present/Absent/Late logging per child per weekday, with validation against weekend dates, future dates, and duplicate (child, date) entries.
- **Health Records** - height/weight/temperature/allergies/notes per visit, with realistic value-range validation; latest weight is classified into a WHO-based nutritional status and charted as a trend.
- **Immunizations** - dose tracking against the DOH Expanded Program on Immunization schedule, with a duplicate-dose database constraint.
- **Reports** - monthly attendance rate, nutritional-status trend, and immunization coverage, with CSV export.
- **Settings** - a user's own profile fields, profile photo, and password change.
- **Account Management** (Admin only) - create additional Staff/Admin accounts.
- **Parent Portal** - `/dashboard/parent/` and read-only Attendance/Health Records/Immunizations pages, all scoped server-side to the logged-in guardian's own children.
- **Access control** - every dashboard view is guarded by a `staff_or_admin_required` or `admin_required` decorator, or an explicit guardian-ownership check for parent views; unauthorized access renders a branded 403 page instead of Django's bare default.
- **REST API** (`/api/`) - token-based auth, registration/login/logout, and viewsets for children/guardians/health records/attendance, mirroring the dashboard's core actions for programmatic/mobile access.
