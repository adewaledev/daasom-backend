import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from rest_framework.test import APIClient
from clients.models import Client
from jobs.models import Job


def login(api: APIClient, username: str, password: str) -> str:
    resp = api.post("/api/auth/login/",
                    {"username": username, "password": password}, format="json")
    assert resp.status_code == 200
    return resp.data["access"]


@pytest.mark.django_db
def test_expense_create_permissions_and_totals():
    # seed milestones so job creation doesn't fail due to missing templates
    call_command("seed_milestones")

    User = get_user_model()
    User.objects.create_user(username="ops1", password="pass123", role="OPS")
    User.objects.create_user(
        username="viewer1", password="pass123", role="VIEWER")
    User.objects.create_user(
        username="acct1", password="pass123", role="ACCOUNTS")

    client = Client.objects.create(
        client_code="CX01", client_prefix="DAA", client_name="Daasom Ltd")
    job = Job.objects.create(client=client, zone="DUTY",
                             file_number="FEX01", quantity=1)

    # OPS can create
    api = APIClient()
    ops_access = login(api, "ops1", "pass123")
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {ops_access}")

    resp = api.post(
        "/api/expenses/",
        {
            "job": str(job.id),
            "category": "Clearing",
            "description": "Port clearing fee",
            "amount": "25000.00",
            "currency": "NGN",
            "expense_date": "2026-02-17",
            "status": "SUBMITTED",
        },
        format="json",
    )
    assert resp.status_code == 201

    # Viewer cannot create
    api = APIClient()
    viewer_access = login(api, "viewer1", "pass123")
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {viewer_access}")
    resp2 = api.post(
        "/api/expenses/",
        {
            "job": str(job.id),
            "category": "Fuel",
            "description": "Diesel",
            "amount": "1000.00",
            "currency": "NGN",
            "expense_date": "2026-02-17",
            "status": "SUBMITTED",
        },
        format="json",
    )
    assert resp2.status_code == 403

    # Totals works
    api = APIClient()
    acct_access = login(api, "acct1", "pass123")
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {acct_access}")
    totals = api.get(f"/api/expenses/totals/?job_id={job.id}")
    assert totals.status_code == 200
    assert totals.data["total"] == "25000.00"
