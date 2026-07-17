# Software Requirements Specification

## DaycareLog - Barangay Daycare Enrollment, Attendance & Health Monitoring System (Django Implementation)

**Version:** 2.0 (Development Continuation Milestone)
**Date:** July 15, 2026
**Prepared by:** Christian Earl Mahumot
**Repository:** https://github.com/earl1605/daycarelog-python

This document supersedes the SRS drafted for the initial core-feature milestone. It has been updated
to describe the system as actually implemented as of this milestone, including all supporting
features completed since.

---

## 1. Introduction

### 1.1 Purpose

This document specifies the functional and non-functional requirements for DaycareLog, a web-based
system that lets barangay daycare staff manage child enrollment, daily attendance, health and
nutrition monitoring, and immunization records, and lets parents/guardians view their own child's
records online.

### 1.2 Scope

DaycareLog replaces a paper-based daycare logbook. In scope for this Django implementation:

- Staff/BHW and Admin accounts, with public self-registration (staff only).
- Parent/Guardian accounts, provisioned exclusively by staff (never self-registered), each linked to
  one or more children.
- Child enrollment records (profile, status, blood type, medical conditions, photo).
- Daily attendance logging per child, restricted to weekdays.
- Health record logging (height, weight, temperature, allergies, notes) with WHO-based nutritional
  status classification.
- Immunization dose tracking against the DOH Expanded Program on Immunization (EPI) schedule.
- Monthly reports (attendance, nutrition trend, immunization coverage) with CSV export.
- A read-only parent portal scoped to each guardian's own children.
- A REST API mirroring the core dashboard actions, for non-browser clients.

Out of scope: billing/payments, multi-daycare/multi-branch support, SMS notifications, offline mode.

### 1.3 Definitions, Acronyms, Abbreviations

| Term | Meaning |
|---|---|
| BHW | Barangay Health Worker - the primary daily user of the STAFF role |
| EPI | (DOH) Expanded Program on Immunization |
| CRUD | Create, Read, Update, Delete |
| MX record | Mail Exchange DNS record, used to check whether an email domain can receive mail |
| Guardian | Interchangeable with Parent/Guardian in this document and in the code (`GuardianProfile`) |

### 1.4 References

- DOH Expanded Program on Immunization schedule (ported into `enrollment/immunizations.py`)
- WHO weight-for-age reference tables, ages 0-60 months (ported into `enrollment/nutritional_status.py`)
- Sibling Spring Boot + React DaycareLog project (shared vaccine schedule and nutritional-status logic,
  so both course deliverables classify identical inputs identically)

### 1.5 Overview

Section 2 describes the product at a high level (users, environment, constraints). Section 3 lists
detailed functional and non-functional requirements. Section 4 describes the data model. Section 5
lists known limitations.

---

## 2. Overall Description

### 2.1 Product Perspective

DaycareLog (Django) is a standalone, server-rendered web application. It is a separate course
deliverable from a sibling Spring Boot + React implementation of the same product concept; both
share the same vaccine schedule and nutritional-status classification logic so their outputs agree
on identical input data, but they do not share a database or codebase.

The system is a monolithic Django project (`daycarelog_django`) split into four apps:

- `accounts` - the custom User model and authentication.
- `enrollment` - the domain models (guardians, children, health records, immunizations, attendance).
- `dashboard` - the primary user interface (server-rendered templates + views) for every role.
- `api` - a Django REST Framework layer exposing the same core actions for non-browser clients.

### 2.2 Product Functions (Summary)

1. Account registration, authentication, and role-based routing.
2. Guardian provisioning and child enrollment (staff-managed).
3. Attendance logging (staff-managed, core feature).
4. Health record logging and nutritional-status monitoring (staff-managed).
5. Immunization dose tracking (staff-managed).
6. Monthly reporting with CSV export (staff-managed).
7. Read-only self-service portal for parents/guardians.
8. Account management for additional staff/admin users (admin-managed).
9. REST API access mirroring functions 2-5 for external/mobile clients.

### 2.3 User Classes and Characteristics

| Role | How the account is created | Primary goals | Access level |
|---|---|---|---|
| **Staff/BHW** | Public self-registration | Day-to-day data entry: enroll children, log attendance/health/immunizations, provision guardians | Full dashboard access except Account Management |
| **Admin** | Created by an existing Staff/Admin from the dashboard | Same as Staff, plus creating other Staff/Admin accounts | Full dashboard access including Account Management |
| **Parent/Guardian** | Created by Staff/Admin from the Guardians page, together with a child; identity verified in person | Check on their own child's attendance, health, and immunization history | Read-only, scoped to their own linked children only |

### 2.4 Operating Environment

- Server: any WSGI host supporting Django 6 / Python 3.x (deployed to Vercel via `build_files.sh`;
  developed and tested locally on Windows).
- Database: PostgreSQL via Supabase, accessed through the Transaction Pooler.
- Client: any modern desktop or mobile browser (server-rendered HTML + Tailwind CSS, no SPA framework;
  minimal vanilla JS for interactive widgets).

### 2.5 Design and Implementation Constraints

- **No Django Admin panel.** `django.contrib.admin` is not in `INSTALLED_APPS`; all entity management
  must go through the custom `dashboard` app. This is an explicit assignment requirement, not an
  incidental omission.
- **Supabase transaction pooler.** The pooler does not support Django's normal test-database
  teardown (`DROP DATABASE` fails because the pooled connection is still considered "in use"), so
  local test runs require `manage.py test --keepdb`.
- **Serverless static files.** Deployed to Vercel, whose filesystem is ephemeral between deployments,
  so user-uploaded images (profile photos, child photos) are stored as base64 data URIs on the model
  rather than as files on disk.
- **Tailwind compiled at build time**, not loaded via the CDN Play script, to avoid recompiling the
  utility set on every page navigation.

### 2.6 Assumptions and Dependencies

- Each child has at most one guardian in this system (a `ForeignKey`, not a many-to-many); siblings
  are enrolled as separate `Child` records under the same `GuardianProfile`.
- The daycare operates on a standard Monday-Friday week; attendance cannot be recorded for
  Saturday/Sunday.

---

## 3. Specific Requirements

### 3.1 Functional Requirements

#### 3.1.1 Authentication & Account Management

| ID | Requirement |
|---|---|
| FR-1.1 | The system shall allow public self-registration, always creating a STAFF account regardless of any role field submitted by the client. |
| FR-1.2 | The system shall reject registration if the email domain is a known disposable-email provider, or has no resolvable MX record. |
| FR-1.3 | The system shall reject registration with an email address already in use. |
| FR-1.4 | A newly registered account shall be able to log in immediately, with no separate email-verification step. |
| FR-1.5 | The system shall authenticate users by email and password and reject sign-in with a generic error message that does not reveal whether the email exists (no user enumeration). |
| FR-1.6 | The system shall redirect a user after login to the dashboard appropriate to their role (Staff/Admin dashboard vs. Parent portal). |
| FR-1.7 | The system shall allow an Admin to create additional Staff or Admin accounts from the Account Management page; this capability shall not be reachable by Staff or Parent roles. |
| FR-1.8 | The system shall let a logged-in user edit their own profile fields, upload a profile photo, and change their password from a Settings page. |

#### 3.1.2 Guardian (Parent/Guardian) Management

| ID | Requirement |
|---|---|
| FR-2.1 | The system shall allow Staff/Admin to create a new Parent/Guardian user account and its guardian profile in a single action, generating a one-time temporary password. |
| FR-2.2 | A guardian account created by staff shall be immediately usable for login, since staff verify the guardian's identity in person. |
| FR-2.3 | The system shall require a `relationship_to_child` value when creating or editing a guardian profile. |
| FR-2.4 | The system shall allow Staff/Admin to edit or delete an existing guardian profile. |
| FR-2.5 | The system shall never allow a Parent/Guardian account to be created through public self-registration. |

#### 3.1.3 Child Enrollment

| ID | Requirement |
|---|---|
| FR-3.1 | The system shall allow Staff/Admin to enroll a child with first/last name, date of birth, sex, status (Enrolled/Pending/Withdrawn), blood type, medical conditions, and an optional photo. |
| FR-3.2 | The system shall reject a date of birth in the future. |
| FR-3.3 | The system shall allow Staff/Admin to edit or delete a child record, with a confirmation prompt before delete. |
| FR-3.4 | The system shall provide a per-child detail page showing the child's profile, health history, attendance history, and immunization progress in one place. |
| FR-3.5 | A child's guardian link may be null (a child may be enrolled before a guardian account exists) and is set to null, not cascade-deleted, if the guardian profile is removed. |

#### 3.1.4 Attendance (Core Feature)

| ID | Requirement |
|---|---|
| FR-4.1 | The system shall allow Staff/Admin to record one attendance entry per child per date, with status Present, Absent, or Late, and optional remarks. |
| FR-4.2 | The system shall reject an attendance date that falls on a Saturday or Sunday. |
| FR-4.3 | The system shall reject an attendance date in the future. |
| FR-4.4 | The system shall reject a duplicate attendance entry for the same child and date, at both the form-validation and database-constraint level. |
| FR-4.5 | The system shall allow Staff/Admin to edit or delete an existing attendance entry. |
| FR-4.6 | The system shall display live attendance counts (present/absent/total) and a weekly attendance chart on the Staff dashboard. |

#### 3.1.5 Health Records & Nutritional Monitoring

| ID | Requirement |
|---|---|
| FR-5.1 | The system shall allow Staff/Admin to record a health visit per child: date, height (cm), weight (kg), temperature (°C), allergies, and notes. |
| FR-5.2 | The system shall reject height, weight, or temperature values outside realistic physiological ranges (height 0-250cm, weight 0-200kg, temperature 30-45°C). |
| FR-5.3 | The system shall attribute each health record to the staff user who recorded it. |
| FR-5.4 | The system shall classify a child's most recent weight, given their date of birth, sex, and the record date, into a nutritional status (Normal, Underweight, Severely Underweight, Overweight, or unclassified if outside the supported 0-60 month age range) using WHO weight-for-age reference tables. |
| FR-5.5 | The system shall chart the nutritional-status distribution over the last 6 months on the Staff dashboard and monthly Reports page. |

#### 3.1.6 Immunization Tracking

| ID | Requirement |
|---|---|
| FR-6.1 | The system shall allow Staff/Admin to record a vaccine dose per child: vaccine name (from the DOH EPI schedule), dose number, date given, administered-by, and notes. |
| FR-6.2 | The system shall reject a date given in the future. |
| FR-6.3 | The system shall reject recording the same dose number of the same vaccine for the same child more than once. |
| FR-6.4 | The system shall compute and display each child's immunization progress (doses given vs. expected) against the EPI schedule on the child detail page. |
| FR-6.5 | The system shall bucket each active child into Fully / Partially / Not Started Immunized, and chart per-vaccine coverage, on the Staff dashboard and Reports page. |

#### 3.1.7 Reporting

| ID | Requirement |
|---|---|
| FR-7.1 | The system shall provide a monthly Reports page showing school days, attendance rate, nutritional-status trend, and immunization coverage for a selected month. |
| FR-7.2 | The system shall allow exporting a per-child summary (name, sex, date of birth, status) as a CSV file. |

#### 3.1.8 Parent/Guardian Portal

| ID | Requirement |
|---|---|
| FR-8.1 | The system shall show a Parent/Guardian, upon login, only the children linked to their own guardian profile. |
| FR-8.2 | The system shall provide read-only Attendance, Health Records, and Immunizations pages scoped server-side to the logged-in guardian's own children - a parent shall not be able to view another guardian's child by any means, including guessing a record's URL/ID. |
| FR-8.3 | Attempting to open another guardian's child detail page directly shall return "not found" (404), not the record's data. |

#### 3.1.9 Access Control (cross-cutting)

| ID | Requirement |
|---|---|
| FR-9.1 | Every Staff/Admin-only view shall reject unauthenticated users (redirect to login) and authenticated non-staff users (403 Forbidden). |
| FR-9.2 | Every Admin-only view (Account Management) shall reject Staff and Parent roles with 403 Forbidden. |
| FR-9.3 | A 403 response shall render a branded error page consistent with the rest of the UI, not a bare framework default. |

#### 3.1.10 REST API

| ID | Requirement |
|---|---|
| FR-10.1 | The system shall expose token-based authentication endpoints (register, login, logout, current-user) under `/api/`. |
| FR-10.2 | The system shall expose CRUD viewsets for children, guardians, health records, and attendance, enforcing the same role-based permissions as the dashboard (Staff/Admin full access; a Parent may only read their own children's records). |

### 3.2 Non-Functional Requirements

| ID | Category | Requirement |
|---|---|---|
| NFR-1 | Security | Passwords are stored using Django's salted-hash mechanism; never in plain text. |
| NFR-2 | Security | Session and CSRF cookies are marked `Secure`, and HTTP is redirected to HTTPS with HSTS, whenever `DEBUG` is off (production). |
| NFR-3 | Security | Every dashboard and API view enforces role-based access control server-side; the UI hiding a link is never the only protection (defense in depth). |
| NFR-4 | Security | Login failure messages are generic and do not reveal whether a given email is registered. |
| NFR-5 | Data Integrity | Duplicate attendance entries and duplicate immunization doses are prevented at the database constraint level, not only in application code. |
| NFR-6 | Usability | The interface is a single custom, role-aware dashboard shell (sidebar navigation, consistent card/table styling) - no framework-default admin screens are shown to any user. |
| NFR-7 | Usability | Destructive actions (deleting a child, guardian, health record, attendance entry, or immunization) require an explicit confirmation prompt. |
| NFR-8 | Performance | Tailwind CSS is precompiled to a static file at build time rather than compiled in-browser on every page load. |
| NFR-9 | Maintainability | Domain logic shared with the sibling React/Spring Boot implementation (EPI schedule, WHO nutritional-status tables) is centralized in dedicated modules (`enrollment/immunizations.py`, `enrollment/nutritional_status.py`) rather than duplicated inline. |
| NFR-10 | Testability | Core workflows (registration/login, staff enrollment-to-attendance-to-health-to-immunization, parent-portal access scoping) and key negative paths (duplicate records, invalid input, unauthorized access) are covered by an automated test suite runnable via `manage.py test`. |

### 3.3 External Interface Requirements

**User interfaces:** Landing page; Login; Register; Staff/Admin
dashboard (Home, Children, Guardians, Attendance, Health Records, Immunizations, Reports, Settings,
Account Management); Parent portal (Home, Attendance, Health Records, Immunizations); 403 error page.

**Software interfaces:** PostgreSQL (Supabase, via `psycopg2`); a REST API consumable by any HTTP client.

**Hardware interfaces:** None beyond a standard web server and client device.

**Communications interfaces:** HTTPS in production (enforced via redirect once `DEBUG=False`).

---

## 4. Data Model

| Entity | Key fields | Relationships |
|---|---|---|
| **User** (`accounts`) | email (unique), role (PARENT/STAFF/ADMIN), contact_number (PH format), profile_photo | 1-1 with GuardianProfile (when role=PARENT) |
| **GuardianProfile** (`enrollment`) | address, relationship_to_child | 1-1 with User (role=PARENT); 1-many with Child |
| **Child** (`enrollment`) | first/last name, date_of_birth, sex, status, blood_type, medical_conditions, photo, enrollment_date | many-1 with GuardianProfile (nullable); 1-many with Attendance, HealthRecord, Immunization |
| **Attendance** (`enrollment`) | date, status (Present/Absent/Late), remarks | many-1 with Child; unique (child, date) |
| **HealthRecord** (`enrollment`) | record_date, height_cm, weight_kg, temperature_c, allergies, notes, recorded_by | many-1 with Child; many-1 with User (recorder) |
| **Immunization** (`enrollment`) | vaccine_name, dose_number, date_given, administered_by, notes, recorded_by | many-1 with Child; unique (child, vaccine_name, dose_number) |

---

## 5. Known Limitations

- The REST API does not yet expose an Immunization viewset (dashboard-only for now).
- A child supports at most one guardian; multi-guardian households are not modeled.
- No SMS or push notifications - email is the only out-of-band channel.
- No automated data retention/archival policy for withdrawn children's historical records.
