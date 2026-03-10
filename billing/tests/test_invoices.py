import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from rest_framework.test import APIClient

from clients.models import Client
from jobs.models import Job
from billing.models import Invoice


def login(api: APIClient, username: str, password: str) -> str:
    resp = api.post("/api/auth/login/",
                    {"username": username, "password": password}, format="json")
    assert resp.status_code == 200
    return resp.data["access"]


@pytest.mark.django_db
def test_invoice_create_and_status_lifecycle():
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

    api = APIClient()
    ops_access = login(api, "ops1", "pass123")
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {ops_access}")

    # Create invoice
    resp = api.post(
        "/api/invoices/",
        {
            "job": str(job.id),
            "invoice_number": "INV-T01",
            "currency": "NGN",
            "grand_total": "30000.00",
        },
        format="json",
    )
    assert resp.status_code == 201
    invoice_id = resp.data["id"]

    # Accounts can change status
    api = APIClient()
    acct_access = login(api, "acct1", "pass123")
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {acct_access}")

    resp2 = api.post(f"/api/invoices/{invoice_id}/issue/")
    assert resp2.status_code == 200
    assert resp2.data["status"] == "ISSUED"

    resp3 = api.post(f"/api/invoices/{invoice_id}/mark_paid/")
    assert resp3.status_code == 200
    assert resp3.data["status"] == "PAID"

    # sanity: invoice exists
    assert Invoice.objects.filter(id=invoice_id).exists()
