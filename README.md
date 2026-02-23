# Daasom Backend

A Django + Django REST Framework backend for managing customs/logistics operations across clients, jobs, milestone tracking, expenses, invoicing, receipts, ledger entries, and document uploads.

---

## Table of contents

- [Overview](#overview)
- [Tech stack](#tech-stack)
- [Project structure](#project-structure)
- [Domain model](#domain-model)
- [Authentication and roles](#authentication-and-roles)
- [API endpoints](#api-endpoints)
- [Setup](#setup)
- [Environment variables](#environment-variables)
- [Run the application](#run-the-application)
- [Management commands](#management-commands)
- [Testing](#testing)
- [Deployment notes](#deployment-notes)
- [Known gaps / follow-ups](#known-gaps--follow-ups)

---

## Overview

This backend exposes a role-aware REST API for operational and finance workflows:

1. Create and manage **clients**.
2. Create **jobs** tied to clients.
3. Auto-seed **job milestones** from templates (by job zone).
4. Record **expenses** on jobs and compute totals.
5. Generate **invoices** (with add-ons) and recompute totals.
6. Record **receipts** and update invoice payment status.
7. Project financial events into a **ledger** (idempotent upserts).
8. Upload and query **documents** linked to jobs/invoices/receipts.

---

## Tech stack

- **Python / Django** for the web framework
- **Django REST Framework** for API layer
- **SimpleJWT** for auth tokens
- **PostgreSQL-compatible DB URL config** via `dj-database-url`
- **Cloudinary** for file storage uploads
- **Pytest + pytest-django** for tests
- **Whitenoise + Gunicorn** for deployment-ready serving

Dependencies are pinned in `requirements.txt` and lint settings are in `pyproject.toml`.

---

## Project structure

```text
config/        Django project config (settings, root urls)
accounts/      Custom user model + role permissions
core/          Health/auth helper endpoints
clients/       Client CRUD
jobs/          Job CRUD + milestone accessor
tracking/      Milestone templates, job milestones, tracker API
expenses/      Expense CRUD + totals endpoint
billing/       Invoice and invoice add-on APIs + totals/status flows
payments/      Receipts + payment status recompute
ledger/        Read-only ledger + sync command + signal upserts
documents/     Document metadata + upload flow (Cloudinary)
tests/         Project-level smoke tests
```

---

## Domain model

### `accounts.User`
- Extends `AbstractUser`
- Adds `role` enum: `ADMIN`, `OPS`, `ACCOUNTS`, `VIEWER`

### `clients.Client`
- `client_code` (unique), `client_prefix`, `client_name`, active flag

### `jobs.Job`
- Belongs to `Client`
- Zone: `DUTY | FREE | EXPORT`
- Shipment/operations metadata (file number, containers, BL/AWB, etc.)

### `tracking.MilestoneTemplate`
- Zone-specific template milestone (`key`, `label`, `sort_order`)

### `tracking.JobMilestone`
- Belongs to `Job` + `MilestoneTemplate`
- `status`: `PENDING | DONE`, optional `date`

### `expenses.Expense`
- Belongs to `Job`
- Category, amount, currency, expense date, workflow status

### `billing.Invoice`
- One-to-one with `Job`
- Stores `expenses_total`, `addons_total`, `grand_total`
- Status: `DRAFT | ISSUED | PARTIALLY_PAID | PAID | VOID`

### `billing.InvoiceAddon`
- Extra charge line-items belonging to an invoice

### `payments.Receipt`
- Payment record belonging to invoice
- Unique non-empty reference per invoice

### `ledger.LedgerEntry`
- Normalized accounting projection for expenses/receipts
- Idempotent via unique `source_id`

### `documents.Document`
- Metadata for uploaded document
- Linked by `doc_type` + one of `job_id` / `invoice_id` / `receipt_id`
- Stores provider key + URL returned from Cloudinary

---

## Authentication and roles

### Auth
- JWT login: `POST /api/auth/login/`
- JWT refresh: `POST /api/auth/refresh/`
- Default API permission is authenticated access.

### Role model
- `ADMIN`: full access
- `OPS`: operations-heavy write access (clients/jobs/expenses/invoice creation)
- `ACCOUNTS`: finance-heavy actions (expense approvals, invoice status, receipts)
- `VIEWER`: read-only behavior through authenticated endpoints

### Permission highlights
- Client create/update/delete: `ADMIN`, `OPS`
- Job create/update/delete: `ADMIN`, `OPS`
- Expense create: `ADMIN`, `OPS`
- Expense update/approve semantics: `ADMIN`, `ACCOUNTS`
- Invoice create: `ADMIN`, `OPS`
- Invoice status transitions: `ADMIN`, `ACCOUNTS`
- Receipt create/update/delete: `ADMIN`, `ACCOUNTS`
- Documents: authenticated users

---

## API endpoints

All routes are mounted under `/api/` unless stated otherwise.

### Core
- `GET /api/health/`
- `GET /api/me/`
- `GET /api/admin-only/`
- `GET /api/ops-only/`

### Auth
- `POST /api/auth/login/`
- `POST /api/auth/refresh/`

### Clients
- `GET /api/clients/`
- `POST /api/clients/`
- `GET /api/clients/{id}/`
- `PUT /api/clients/{id}/`
- `PATCH /api/clients/{id}/`
- `DELETE /api/clients/{id}/`

### Jobs
- `GET /api/jobs/`
- `POST /api/jobs/`
- `GET /api/jobs/{id}/`
- `PUT /api/jobs/{id}/`
- `PATCH /api/jobs/{id}/`
- `DELETE /api/jobs/{id}/`
- `GET /api/jobs/{id}/milestones/`

### Tracking
- `GET /api/job-milestones/`
- `POST /api/job-milestones/`
- `GET /api/job-milestones/{id}/`
- `PUT /api/job-milestones/{id}/`
- `PATCH /api/job-milestones/{id}/`
- `DELETE /api/job-milestones/{id}/`
- `GET /api/tracker/?zone=&client_code=&file_number=`

### Expenses
- `GET /api/expenses/`
- `POST /api/expenses/`
- `GET /api/expenses/{id}/`
- `PUT /api/expenses/{id}/`
- `PATCH /api/expenses/{id}/`
- `DELETE /api/expenses/{id}/` *(blocked by view logic; returns method-not-allowed)*
- `GET /api/expenses/totals/?job_id=`

### Billing
- `GET /api/invoices/`
- `POST /api/invoices/`
- `GET /api/invoices/{id}/`
- `PUT /api/invoices/{id}/`
- `PATCH /api/invoices/{id}/`
- `DELETE /api/invoices/{id}/`
- `POST /api/invoices/{id}/refresh_totals/`
- `POST /api/invoices/{id}/issue/`
- `POST /api/invoices/{id}/mark_partial/`
- `POST /api/invoices/{id}/mark_paid/`
- `POST /api/invoices/{id}/void/`
- `GET /api/invoices/{id}/payment_summary/`

Invoice add-ons:
- `GET /api/invoice-addons/`
- `POST /api/invoice-addons/`
- `GET /api/invoice-addons/{id}/`
- `PUT /api/invoice-addons/{id}/`
- `PATCH /api/invoice-addons/{id}/`
- `DELETE /api/invoice-addons/{id}/`

### Payments
- `GET /api/receipts/`
- `POST /api/receipts/`
- `GET /api/receipts/{id}/`
- `PUT /api/receipts/{id}/`
- `PATCH /api/receipts/{id}/`
- `DELETE /api/receipts/{id}/`
- `GET /api/receipts/summary/?invoice_id=`

### Ledger
- `GET /api/ledger/`
- `GET /api/ledger/{id}/`

Filters:
- `/api/ledger/?job_id=`
- `/api/ledger/?invoice_id=`
- `/api/ledger/?entry_type=EXPENSE|RECEIPT`

### Documents
- `GET /api/documents/`
- `POST /api/documents/` *(multipart upload with `file` + ids)*
- `GET /api/documents/{id}/`
- `PUT /api/documents/{id}/`
- `PATCH /api/documents/{id}/`
- `DELETE /api/documents/{id}/`
- `GET /api/documents/by_job/?job_id=`
- `GET /api/documents/{id}/download/` *(authenticated backend-proxied download)*

---

## Setup

### 1) Clone and enter repo

```bash
git clone <repo-url>
cd daasom-backend
```

### 2) Create virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

### 4) Create environment file

Create `.env` in project root (see [Environment variables](#environment-variables)).

### 5) Apply migrations

```bash
python manage.py migrate
```

### 6) Seed milestone templates (recommended)

```bash
python manage.py seed_milestones
```

---

## Environment variables

Minimal examples:

```env
DEBUG=True
SECRET_KEY=replace-me
DATABASE_URL=postgresql://user:pass@localhost:5432/daasom

ALLOWED_HOSTS=127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8000,http://localhost:8000
CORS_ALLOWED_ORIGINS=http://127.0.0.1:3000,http://localhost:3000

CLOUDINARY_CLOUD_NAME=...
CLOUDINARY_API_KEY=...
CLOUDINARY_API_SECRET=...
```

Notes:
- `DATABASE_URL` is required by current settings path.
- In non-debug mode, security settings enforce SSL/HSTS and secure cookies.

---

## Run the application

```bash
python manage.py runserver
```

App will be served at `http://127.0.0.1:8000/` by default.

Admin site: `http://127.0.0.1:8000/admin/`

---

## Management commands

### Seed milestone templates

```bash
python manage.py seed_milestones
```

Creates/updates milestone templates per zone (`DUTY`, `FREE`, `EXPORT`) and is safe to rerun.

### Sync ledger projection

```bash
python manage.py sync_ledger
```

Backfills/updates ledger entries from existing expenses and receipts.

---

## Testing

Run tests with:

```bash
pytest -q
```

or (if using project venv explicitly):

```bash
.venv/bin/python -m pytest -q
```

Current test suites cover:
- auth and role protections
- client permissions
- job milestone auto-creation
- expense permissions/totals
- invoice totals and payment summaries
- ledger entry creation/filtering

---

## Deployment notes

- App includes `gunicorn` and `whitenoise` dependencies.
- Proxy-aware settings are enabled (`SECURE_PROXY_SSL_HEADER`, `USE_X_FORWARDED_HOST`).
- For production:
  - set `DEBUG=False`
  - provide strong `SECRET_KEY`
  - configure `ALLOWED_HOSTS`, CSRF/CORS origins
  - provide a real `DATABASE_URL`

---

## Known gaps / follow-ups

- Improve API docs generation (e.g., OpenAPI/Swagger) for contract discoverability.
- Add endpoint-level examples (request/response JSON) to this README.
- Add dedicated tests for document upload (`POST /api/documents/`) and Cloudinary failure handling.
