import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from rest_framework.test import APIClient

from clients.models import Client
from jobs.models import Job
from expenses.models import Expense
from billing.models import Invoice


def login(api: APIClient, username: str, password: str) -> str:
    resp = api.post("/api/auth/login/",
                    {"username": username, "password": password}, format="json")
    assert resp.status_code == 200
    return resp.data["access"]


@pytest.mark.django_db
def test_invoice_totals_from_expenses_and_addons():
    # Not strictly required for invoices, but keeps job creation ecosystem consistent
    call_command("seed_milestones")

    User = get_user_model()
    User.objects.create_user(username="ops1", password="pass123", role="OPS")
    User.objects.create_user(
        username="acct1", password="pass123", role="ACCOUNTS")

    client = Client.objects.create(
        client_code="CINV1", client_prefix="DAA", client_name="Daasom Ltd")
    job = Job.objects.create(client=client, zone="DUTY",
                             file_number="FINV01", quantity=1)

    # Create expenses directly (fast + stable)
    Expense.objects.create(
        job=job,
        category="Clearing",
        description="Fee",
        amount="25000.00",
        currency="NGN",
        expense_date="2026-02-17",
        status="SUBMITTED",
    )

    api = APIClient()
    ops_access = login(api, "ops1", "pass123")
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {ops_access}")

    # Create invoice
    resp = api.post(
        "/api/invoices/",
        {"job": str(job.id), "invoice_number": "INV-T01", "currency": "NGN"},
        format="json",
    )
    assert resp.status_code == 201
    invoice_id = resp.data["id"]

    # Add addon
    resp2 = api.post(
        "/api/invoice-addons/",
        {"invoice": invoice_id, "description": "Extra Handling", "amount": "5000.00"},
        format="json",
    )
    assert resp2.status_code == 201

    # Refresh totals
    resp3 = api.post(f"/api/invoices/{invoice_id}/refresh_totals/")
    assert resp3.status_code == 200
    assert resp3.data["expenses_total"] == "25000.00"
    assert resp3.data["addons_total"] == "5000.00"
    assert resp3.data["grand_total"] == "30000.00"

    # Accounts can change status
    api = APIClient()
    acct_access = login(api, "acct1", "pass123")
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {acct_access}")

    resp4 = api.post(f"/api/invoices/{invoice_id}/issue/")
    assert resp4.status_code == 200
    assert resp4.data["status"] == "ISSUED"

    resp5 = api.post(f"/api/invoices/{invoice_id}/mark_paid/")
    assert resp5.status_code == 200
    assert resp5.data["status"] == "PAID"

    # sanity: invoice exists
    assert Invoice.objects.filter(id=invoice_id).exists()
