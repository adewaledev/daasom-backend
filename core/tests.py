from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.test import TestCase

# Create your tests here.
import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_health(client):
    url = reverse("health")
    resp = client.get(url)
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@pytest.mark.django_db
def test_role_protection_admin_and_viewer():
    User = get_user_model()
    User.objects.create_user(
        username="admin1", password="pass123", role="ADMIN")
    User.objects.create_user(
        username="viewer1", password="pass123", role="VIEWER")

    c = APIClient()

    # viewer cannot access
    resp = c.post("/api/auth/login/",
                  {"username": "viewer1", "password": "pass123"}, format="json")
    viewer_access = resp.data["access"]
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {viewer_access}")
    assert c.get("/api/admin-only/").status_code == 403
    assert c.get("/api/ops-only/").status_code == 403

    # admin can access
    c = APIClient()
    resp = c.post("/api/auth/login/",
                  {"username": "admin1", "password": "pass123"}, format="json")
    admin_access = resp.data["access"]
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {admin_access}")
    assert c.get("/api/admin-only/").status_code == 200
    assert c.get("/api/ops-only/").status_code == 200
