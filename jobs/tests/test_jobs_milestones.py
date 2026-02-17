import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from rest_framework.test import APIClient
from clients.models import Client
from tracking.models import JobMilestone, MilestoneTemplate


@pytest.mark.django_db
def test_job_creation_auto_creates_milestones():
    # Seed templates into the TEST database
    call_command("seed_milestones")
    assert MilestoneTemplate.objects.count() > 0

    User = get_user_model()
    User.objects.create_user(
        username="admin1", password="pass123", role="ADMIN")

    client = Client.objects.create(
        client_code="C001X", client_prefix="DAA", client_name="Daasom Ltd")

    api = APIClient()
    login = api.post("/api/auth/login/",
                     {"username": "admin1", "password": "pass123"}, format="json")
    assert login.status_code == 200
    access = login.data["access"]
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    resp = api.post(
        "/api/jobs/",
        {
            "client": str(client.id),
            "zone": "DUTY",
            "file_number": "F100",
            "quantity": 1,
            "bl_awb": "BL100",
            "container_40ft": 1,
            "container_20ft": 0,
        },
        format="json",
    )
    assert resp.status_code == 201
    job_id = resp.data["id"]

    assert JobMilestone.objects.filter(job_id=job_id).count() > 0

    resp2 = api.get(f"/api/jobs/{job_id}/milestones/")
    assert resp2.status_code == 200
    assert len(resp2.data) > 0

    resp3 = api.get("/api/tracker/?zone=DUTY")
    assert resp3.status_code == 200
    assert any(r["file_number"] == "F100" for r in resp3.data)
