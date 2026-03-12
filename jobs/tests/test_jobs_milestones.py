import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from clients.models import Client
from tracking.models import TrackerEntry


@pytest.mark.django_db
def test_job_tracker_entries_and_completion_flow():
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

    list_resp = api.get(f"/api/jobs/{job_id}/tracker_entries/")
    assert list_resp.status_code == 200
    assert list_resp.data == []

    entry_resp = api.post(
        "/api/tracker-entries/",
        {
            "job": job_id,
            "entry_date": "2026-03-12",
            "progress_report": "Shipment documents reviewed",
            "next_step": "Submit customs paperwork",
        },
        format="json",
    )
    assert entry_resp.status_code == 201
    assert TrackerEntry.objects.filter(job_id=job_id).count() == 1

    resp2 = api.get(f"/api/jobs/{job_id}/tracker_entries/")
    assert resp2.status_code == 200
    assert len(resp2.data) == 1
    assert resp2.data[0]["progress_report"] == "Shipment documents reviewed"

    resp3 = api.get("/api/tracker/?zone=DUTY")
    assert resp3.status_code == 200
    tracker_row = next(r for r in resp3.data if r["file_number"] == "F100")
    assert tracker_row["tracker_completed"] is False
    assert tracker_row["tracker_entries"][0]["next_step"] == "Submit customs paperwork"

    complete_resp = api.post(f"/api/jobs/{job_id}/mark_tracker_completed/")
    assert complete_resp.status_code == 200
    assert complete_resp.data["tracker_completed"] is True

    completed_only = api.get("/api/tracker/?tracker_completed=true")
    assert completed_only.status_code == 200
    assert len(completed_only.data) == 1
    assert completed_only.data[0]["job_id"] == job_id
