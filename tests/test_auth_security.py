import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APIClient


def login_pair(client: APIClient, username: str, password: str) -> dict:
    response = client.post(
        "/api/auth/login/",
        {"username": username, "password": password},
        format="json",
    )
    assert response.status_code == 200
    return response.data


@pytest.mark.django_db
def test_refresh_rotation_and_logout_blacklist_refresh_tokens():
    user_model = get_user_model()
    user_model.objects.create_user(
        username="ops1", password="pass123", role="OPS")

    client = APIClient()
    tokens = login_pair(client, "ops1", "pass123")

    first_refresh = tokens["refresh"]
    refresh_response = client.post(
        "/api/auth/refresh/",
        {"refresh": first_refresh},
        format="json",
    )
    assert refresh_response.status_code == 200
    assert "refresh" in refresh_response.data

    second_refresh = refresh_response.data["refresh"]

    replay_response = client.post(
        "/api/auth/refresh/",
        {"refresh": first_refresh},
        format="json",
    )
    assert replay_response.status_code == 401

    logout_response = client.post(
        "/api/auth/logout/",
        {"refresh": second_refresh},
        format="json",
    )
    assert logout_response.status_code == 200

    blacklisted_response = client.post(
        "/api/auth/refresh/",
        {"refresh": second_refresh},
        format="json",
    )
    assert blacklisted_response.status_code == 401


@pytest.mark.django_db
def test_password_change_invalidates_existing_access_token():
    user_model = get_user_model()
    user = user_model.objects.create_user(
        username="viewer1", password="pass123", role="VIEWER")

    client = APIClient()
    tokens = login_pair(client, "viewer1", "pass123")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

    assert client.get("/api/me/").status_code == 200

    user.set_password("newpass123")
    user.save(update_fields=["password"])

    assert client.get("/api/me/").status_code == 401


@pytest.mark.django_db
def test_login_endpoint_is_throttled():
    cache.clear()

    user_model = get_user_model()
    user_model.objects.create_user(
        username="admin1", password="pass123", role="ADMIN")

    client = APIClient()

    try:
        responses = []
        for _ in range(11):
            responses.append(
                client.post(
                    "/api/auth/login/",
                    {"username": "admin1", "password": "wrong-pass"},
                    format="json",
                )
            )

        assert all(response.status_code == 401 for response in responses[:-1])
        assert responses[-1].status_code == 429
    finally:
        cache.clear()
