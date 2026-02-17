from django.test import TestCase

# Create your tests here.
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


def login(client: APIClient, username: str, password: str) -> str:
    resp = client.post(
        "/api/auth/login/", {"username": username, "password": password}, format="json")
    assert resp.status_code == 200
    return resp.data["access"]


@pytest.mark.django_db
def test_admin_can_create_client_and_viewer_cannot():
    User = get_user_model()
    User.objects.create_user(
        username="admin1", password="pass123", role="ADMIN")
    User.objects.create_user(
        username="viewer1", password="pass123", role="VIEWER")

    c = APIClient()

    admin_access = login(c, "admin1", "pass123")
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {admin_access}")

    resp = c.post(
        "/api/clients/",
        {"client_code": "C001", "client_prefix": "DAA", "client_name": "Daasom Ltd"},
        format="json",
    )
    assert resp.status_code == 201
    assert resp.data["client_code"] == "C001"

    # duplicate should fail
    resp2 = c.post(
        "/api/clients/",
        {"client_code": "C001", "client_prefix": "DAA", "client_name": "Duplicate"},
        format="json",
    )
    assert resp2.status_code == 400

    # viewer cannot create
    c = APIClient()
    viewer_access = login(c, "viewer1", "pass123")
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {viewer_access}")

    resp3 = c.post(
        "/api/clients/",
        {"client_code": "C002", "client_prefix": "VVV",
            "client_name": "Viewer Attempt"},
        format="json",
    )
    assert resp3.status_code in (403, 401)
