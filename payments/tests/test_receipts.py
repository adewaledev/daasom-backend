import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from rest_framework.test import APIClient

from clients.models import Client
from jobs.models import Job
from expenses.models import Expense
from billing.models import Invoice
from billing.services import recompute_invoice_totals


def login(api: APIClient, username: str, password: str) -> str:
    resp = api.post("/api/auth/login/",
                    {"username": username, "password": password}, format="json")
    assert resp.status_code == 200
    return resp.data["access"]


@pytest.mark.django_db
def test_receipts_update_invoice_payment_status_and_summary():
    call_command("seed_milestones")

    User = get_user_model()
    User.objects.create_user(username="ops1", password="pass123", role="OPS")
    User.objects.create_user(
        username="acct1", password="pass123", role="ACCOUNTS")
    User.objects.create_user(
        username="viewer1", password="pass123", role="VIEWER")

    client = Client.objects.create(
        client_code="CPAY1", client_prefix="DAA", client_name="Daasom Ltd")
    job = Job.objects.create(client=client, zone="DUTY",
                             file_number="FPAY01", quantity=1)

    Expense.objects.create(
        job=job,
        category="Clearing",
        description="Fee",
        amount="25000.00",
        currency="NGN",
        expense_date="2026-02-17",
        status="SUBMITTED",
    )

    invoice = Invoice.objects.create(
        job=job, invoice_number="INV-P01", currency="NGN")
    # add-on = 5000
    invoice.addons.create(description="Extra Handling", amount="5000.00")
    recompute_invoice_totals(invoice)  # total should be 30000.00

    # viewer cannot create receipt
    api = APIClient()
    viewer_access = login(api, "viewer1", "pass123")
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {viewer_access}")
    r0 = api.post(
        "/api/receipts/",
        {
            "invoice": str(invoice.id),
            "amount": "10000.00",
            "currency": "NGN",
            "payment_date": "2026-02-17",
            "method": "transfer",
            "reference": "TXN-VIEWER",
        },
        format="json",
    )
    assert r0.status_code == 403

    # accounts creates partial payment
    api = APIClient()
    acct_access = login(api, "acct1", "pass123")
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {acct_access}")

    r1 = api.post(
        "/api/receipts/",
        {
            "invoice": str(invoice.id),
            "amount": "10000.00",
            "currency": "NGN",
            "payment_date": "2026-02-17",
            "method": "transfer",
            "reference": "TXN1",
        },
        format="json",
    )
    assert r1.status_code == 201

    # summary endpoint on invoice
    s1 = api.get(f"/api/invoices/{invoice.id}/payment_summary/")
    assert s1.status_code == 200
    assert s1.data["total"] == "30000.00"
    assert s1.data["paid"] == "10000.00"
    assert s1.data["due"] == "20000.00"

    # second receipt pays remaining -> PAID
    r2 = api.post(
        "/api/receipts/",
        {
            "invoice": str(invoice.id),
            "amount": "20000.00",
            "currency": "NGN",
            "payment_date": "2026-02-17",
            "method": "transfer",
            "reference": "TXN2",
        },
        format="json",
    )
    assert r2.status_code == 201

    s2 = api.get(f"/api/invoices/{invoice.id}/payment_summary/")
    assert s2.status_code == 200
    assert s2.data["paid"] == "30000.00"
    assert s2.data["due"] == "0.00"

    invoice.refresh_from_db()
    assert invoice.status == "PAID"
