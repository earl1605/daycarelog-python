# DaycareLog (Django)

Barangay Daycare Enrollment and Health Tracking System - Django + Supabase (PostgreSQL) implementation.

This is a separate course deliverable from the existing Spring Boot + React DaycareLog project. It uses Django as the backend framework with server-rendered templates, a **custom-built admin dashboard** (the default Django Admin is not used as the primary interface), and Supabase PostgreSQL as the database.

## Tech Stack

- Django 6
- Supabase (PostgreSQL) via the Transaction Pooler
- django-rest-framework (available for future API endpoints)
- python-decouple for environment configuration
- Tailwind CSS, compiled to a static file at build time (not the CDN Play script - see "Rebuilding CSS" below)

## Project Structure

```
daycarelog_django/   Project settings, root URLconf
accounts/            Custom User model (PARENT/STAFF/ADMIN roles), registration, login/logout
enrollment/           Guardian, Child, HealthRecord, Attendance models
dashboard/            Custom staff/admin dashboard and parent dashboard views
templates/            Server-rendered HTML templates
static/               CSS
```

## Roles

- **PARENT** - created only through public self-registration (`/accounts/register/`). Sees their own children's records.
- **STAFF** / **ADMIN** - created only by an existing ADMIN from the dashboard's Account Management page. Public registration can never create a STAFF or ADMIN account.

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

6. Create a superuser (optional, for Django Admin access as a fallback tool):
   ```
   python manage.py createsuperuser
   ```

7. Run the development server:
   ```
   python manage.py runserver
   ```

8. Visit `http://127.0.0.1:8000/` for the landing page. Register a Staff/BHW account at `/accounts/register/` - Parent/Guardian accounts are created by Staff/Admin from the dashboard's Guardians page instead (see Roles below).

## Rebuilding CSS

Tailwind is compiled to a static file (`static/css/tailwind-built.css`) at commit time, not loaded from the CDN Play script - this makes every page load much faster since the browser doesn't recompile the whole utility set on every navigation. If you add new Tailwind classes to any template, rebuild it:

```
npm install
npx tailwindcss -i static/css/tailwind-input.css -o static/css/tailwind-built.css --minify
```

Then commit the updated `tailwind-built.css`.

## Features

- **Registration** - Staff/BHW self-registration with server-side validation, duplicate-email prevention, and hashed passwords. Public registration can never create a Parent/Guardian or Admin account.
- **Login/Logout** - Email-based authentication with generic error messages (no user enumeration) and role-based redirect after login.
- **Custom Dashboard** - `/dashboard/` for STAFF/ADMIN with menus for Enrolled Children, Parent/Guardian Records (including creating a verified Guardian account with a generated temporary password), Health Records, Attendance, Reports, Settings, and (ADMIN-only) Users. `/dashboard/parent/` for PARENT users to view their own children, with read-only Attendance and Health Records pages scoped to their own linked children.
