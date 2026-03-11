import itertools

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from accounts.roles import UserRole
from billing.models import Invoice
from clients.models import Client
from documents.models import Document
from jobs.models import Job
from tracking.models import JobMilestone


ROLE_ORDER = [UserRole.ADMIN, UserRole.OPS, UserRole.ACCOUNTS, UserRole.VIEWER]
_ALLOWED_CLIENTS = {UserRole.ADMIN, UserRole.OPS}
_ALLOWED_JOBS = {UserRole.ADMIN, UserRole.OPS}
_ALLOWED_TRACKER = {UserRole.ADMIN, UserRole.OPS}
_ALLOWED_EXPENSES = {UserRole.ADMIN, UserRole.OPS}
_ALLOWED_INVOICES = {UserRole.ADMIN, UserRole.OPS, UserRole.ACCOUNTS}
_ALLOWED_RECEIPTS = {UserRole.ADMIN, UserRole.ACCOUNTS}
_ALLOWED_DOCUMENTS = {UserRole.ADMIN, UserRole.OPS, UserRole.ACCOUNTS}
_counter = itertools.count(1)


@pytest.fixture(autouse=True)
def seed_milestones(db):
    call_command("seed_milestones")


def next_value(prefix: str) -> str:
    return f"{prefix}{next(_counter)}"


def make_user(role: str):
    User = get_user_model()
    username = next_value(role.lower())
    return User.objects.create_user(username=username, password="pass123", role=role)


def make_client() -> Client:
    return Client.objects.create(
        client_code=next_value("C"),
        client_prefix="DAA",
        client_name=next_value("Client "),
    )


def make_job(*, client: Client | None = None) -> Job:
    return Job.objects.create(
        client=client or make_client(),
        zone="DUTY",
        file_number=next_value("JOB"),
        quantity=1,
    )


def make_invoice(*, total: str = "30000.00") -> Invoice:
    return Invoice.objects.create(
        job=make_job(),
        invoice_number=next_value("INV"),
        currency="NGN",
        grand_total=total,
        invoice_amount=total,
    )


def api_client(user=None) -> APIClient:
    client = APIClient()
    if user is not None:
        client.force_authenticate(user=user)
    return client


@pytest.mark.django_db
def test_login_and_me_expose_canonical_role():
    user = make_user(UserRole.OPS)
    client = APIClient()

    login = client.post(
        "/api/auth/login/",
        {"username": user.username, "password": "pass123"},
        format="json",
    )

    assert login.status_code == 200
    assert login.data["role"] == UserRole.OPS
    assert AccessToken(login.data["access"])["role"] == UserRole.OPS

    client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
    me = client.get("/api/me/")
    assert me.status_code == 200
    assert me.data["role"] == UserRole.OPS


@pytest.mark.django_db
def test_unauthenticated_write_returns_401_and_forbidden_write_returns_403():
    unauthenticated = APIClient()
    no_auth_response = unauthenticated.post(
        "/api/clients/",
        {"client_code": next_value(
            "C"), "client_prefix": "DAA", "client_name": "No Auth"},
        format="json",
    )
    assert no_auth_response.status_code == 401

    viewer = make_user(UserRole.VIEWER)
    viewer_client = api_client(viewer)
    forbidden_response = viewer_client.post(
        "/api/clients/",
        {"client_code": next_value(
            "C"), "client_prefix": "DAA", "client_name": "Viewer"},
        format="json",
    )
    assert forbidden_response.status_code == 403


@pytest.mark.django_db
def test_clients_write_matrix_for_create_and_update():
    for role in ROLE_ORDER:
        user = make_user(role)
        client = api_client(user)
        response = client.post(
            "/api/clients/",
            {
                "client_code": next_value("C"),
                "client_prefix": "DAA",
                "client_name": "RBAC Client",
            },
            format="json",
        )
        if role in _ALLOWED_CLIENTS:
            assert response.status_code == 201
        else:
            assert response.status_code == 403

    for role in ROLE_ORDER:
        user = make_user(role)
        client = api_client(user)
        target = make_client()
        response = client.patch(
            f"/api/clients/{target.id}/",
            {"client_name": "Updated Client"},
            format="json",
        )
        if role in _ALLOWED_CLIENTS:
            assert response.status_code == 200
        else:
            assert response.status_code == 403


@pytest.mark.django_db
def test_jobs_and_tracker_write_matrix():
    base_client = make_client()

    for role in ROLE_ORDER:
        user = make_user(role)
        client = api_client(user)
        response = client.post(
            "/api/jobs/",
            {
                "client": str(base_client.id),
                "zone": "DUTY",
                "file_number": next_value("FILE"),
                "quantity": 1,
            },
            format="json",
        )
        if role in _ALLOWED_JOBS:
            assert response.status_code == 201
        else:
            assert response.status_code == 403

    milestone_job = make_job(client=base_client)
    milestone = JobMilestone.objects.filter(job=milestone_job).first()
    assert milestone is not None

    for role in ROLE_ORDER:
        user = make_user(role)
        client = api_client(user)
        response = client.patch(
            f"/api/job-milestones/{milestone.id}/",
            {"status": "DONE", "date": "2026-03-11"},
            format="json",
        )
        if role in _ALLOWED_TRACKER:
            assert response.status_code == 200
        else:
            assert response.status_code == 403


@pytest.mark.django_db
def test_expenses_write_matrix_for_create_and_update():
    job = make_job()

    for role in ROLE_ORDER:
        user = make_user(role)
        client = api_client(user)
        response = client.post(
            "/api/expenses/",
            {
                "job": str(job.id),
                "category": "Clearing",
                "description": "Port clearing fee",
                "amount": "25000.00",
                "currency": "NGN",
                "expense_date": "2026-03-11",
                "status": "SUBMITTED",
            },
            format="json",
        )
        if role in _ALLOWED_EXPENSES:
            assert response.status_code == 201
        else:
            assert response.status_code == 403

    expense_owner = make_user(UserRole.ADMIN)
    expense = api_client(expense_owner).post(
        "/api/expenses/",
        {
            "job": str(job.id),
            "category": "Fuel",
            "description": "Diesel",
            "amount": "1000.00",
            "currency": "NGN",
            "expense_date": "2026-03-11",
            "status": "SUBMITTED",
        },
        format="json",
    )
    expense_id = expense.data["id"]

    for role in ROLE_ORDER:
        user = make_user(role)
        client = api_client(user)
        response = client.patch(
            f"/api/expenses/{expense_id}/",
            {"status": "APPROVED"},
            format="json",
        )
        if role in _ALLOWED_EXPENSES:
            assert response.status_code == 200
        else:
            assert response.status_code == 403


@pytest.mark.django_db
def test_invoice_crud_write_matrix():
    for role in ROLE_ORDER:
        user = make_user(role)
        client = api_client(user)
        job = make_job()
        response = client.post(
            "/api/invoices/",
            {
                "job": str(job.id),
                "invoice_number": next_value("INV-"),
                "currency": "NGN",
                "grand_total": "30000.00",
            },
            format="json",
        )
        if role in _ALLOWED_INVOICES:
            assert response.status_code == 201
            assert response.data["invoice_amount"] == "30000.00"
        else:
            assert response.status_code == 403

    for role in ROLE_ORDER:
        user = make_user(role)
        client = api_client(user)
        invoice = make_invoice()
        patch_response = client.patch(
            f"/api/invoices/{invoice.id}/",
            {"notes": "Updated note"},
            format="json",
        )
        delete_response = client.delete(f"/api/invoices/{invoice.id}/")
        if role in _ALLOWED_INVOICES:
            assert patch_response.status_code == 200
            assert delete_response.status_code == 204
        else:
            assert patch_response.status_code == 403
            assert delete_response.status_code == 403


@pytest.mark.django_db
@pytest.mark.parametrize("action", ["issue", "mark_partial", "mark_paid", "void", "refresh_totals"])
def test_invoice_custom_actions_follow_write_matrix(action):
    for role in ROLE_ORDER:
        user = make_user(role)
        client = api_client(user)
        invoice = make_invoice()
        if action == "refresh_totals":
            invoice.expenses_total = "5.00"
            invoice.addons_total = "1.00"
            invoice.save(update_fields=[
                         "expenses_total", "addons_total", "updated_at"])
        response = client.post(f"/api/invoices/{invoice.id}/{action}/")
        if role in _ALLOWED_INVOICES:
            assert response.status_code == 200
        else:
            assert response.status_code == 403


@pytest.mark.django_db
def test_receipts_write_matrix_for_create_and_update():
    for role in ROLE_ORDER:
        user = make_user(role)
        client = api_client(user)
        invoice = make_invoice()
        response = client.post(
            "/api/receipts/",
            {
                "invoice": str(invoice.id),
                "amount": "10000.00",
                "currency": "NGN",
                "payment_date": "2026-03-11",
                "method": "transfer",
                "reference": next_value("TXN"),
            },
            format="json",
        )
        if role in _ALLOWED_RECEIPTS:
            assert response.status_code == 201
        else:
            assert response.status_code == 403

    for role in ROLE_ORDER:
        user = make_user(role)
        client = api_client(user)
        invoice = make_invoice()
        receipt = api_client(make_user(UserRole.ADMIN)).post(
            "/api/receipts/",
            {
                "invoice": str(invoice.id),
                "amount": "5000.00",
                "currency": "NGN",
                "payment_date": "2026-03-11",
                "method": "transfer",
                "reference": next_value("TXN"),
            },
            format="json",
        )
        receipt_id = receipt.data["id"]
        response = client.patch(
            f"/api/receipts/{receipt_id}/",
            {"notes": "Updated"},
            format="json",
        )
        if role in _ALLOWED_RECEIPTS:
            assert response.status_code == 200
        else:
            assert response.status_code == 403


@pytest.mark.django_db
def test_documents_write_matrix_for_upload_and_delete(monkeypatch):
    import documents.views as document_views

    monkeypatch.setattr(
        document_views,
        "upload_file",
        lambda file_obj, folder: {
            "public_id": f"mock/{folder}", "url": "https://example.com/file.pdf"},
    )

    for role in ROLE_ORDER:
        user = make_user(role)
        client = api_client(user)
        job = make_job()
        upload = SimpleUploadedFile(
            "test.pdf", b"pdf-content", content_type="application/pdf")
        response = client.post(
            "/api/documents/",
            {
                "doc_type": "JOB",
                "job_id": str(job.id),
                "file": upload,
            },
            format="multipart",
        )
        if role in _ALLOWED_DOCUMENTS:
            assert response.status_code == 201
        else:
            assert response.status_code == 403

    admin = make_user(UserRole.ADMIN)
    for role in ROLE_ORDER:
        user = make_user(role)
        client = api_client(user)
        document = Document.objects.create(
            doc_type="JOB",
            job_id=make_job().id,
            filename="stored.pdf",
            content_type="application/pdf",
            size_bytes=10,
            storage_provider="cloudinary",
            storage_key=next_value("stored"),
            url="https://example.com/stored.pdf",
            uploaded_by=admin,
        )
        response = client.delete(f"/api/documents/{document.id}/")
        if role in _ALLOWED_DOCUMENTS:
            assert response.status_code == 204
        else:
            assert response.status_code == 403
