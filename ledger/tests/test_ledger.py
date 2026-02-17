import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from clients.models import Client
from jobs.models import Job
from expenses.models import Expense
from billing.models import Invoice
from payments.models import Receipt
from ledger.models import LedgerEntry


def login(api: APIClient, username: str, password: str) -> str:
    resp = api.post("/api/auth/login/",
                    {"username": username, "password": password}, format="json")
    assert resp.status_code == 200
    return resp.data["access"]


@pytest.mark.django_db
def test_ledger_entries_created_and_filterable():
    User = get_user_model()
    User.objects.create_user(
        username="admin1", password="pass123", role="ADMIN")

    client = Client.objects.create(
        client_code="CL01", client_prefix="DAA", client_name="Daasom Ltd")
    job = Job.objects.create(client=client, zone="DUTY",
                             file_number="LJOB01", quantity=1)
    invoice = Invoice.objects.create(
        job=job, invoice_number="INV-L01", currency="NGN")

    exp = Expense.objects.create(
        job=job,
        category="Clearing",
        description="Port clearing fee",
        amount="25000.00",
        currency="NGN",
        expense_date="2026-02-17",
        status="SUBMITTED",
    )

    rec = Receipt.objects.create(
        invoice=invoice,
        amount="10000.00",
        currency="NGN",
        payment_date="2026-02-17",
        method="transfer",
        reference="LEDGER-TXN1",
    )

    # If you're using signals, ledger entries should exist immediately.
    assert LedgerEntry.objects.filter(
        source_id=exp.id, entry_type="EXPENSE").exists()
    assert LedgerEntry.objects.filter(
        source_id=rec.id, entry_type="RECEIPT").exists()

    api = APIClient()
    token = login(api, "admin1", "pass123")
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    resp = api.get(f"/api/ledger/?job_id={job.id}")
    assert resp.status_code == 200
    assert len(resp.data) == 2

    # filter receipts only
    resp2 = api.get(f"/api/ledger/?job_id={job.id}&entry_type=RECEIPT")
    assert resp2.status_code == 200
    assert len(resp2.data) == 1
    assert resp2.data[0]["direction"] == "CREDIT"
