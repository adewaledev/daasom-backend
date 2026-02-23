import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from documents.models import Document


@pytest.mark.django_db
def test_document_download_requires_authentication():
    doc = Document.objects.create(
        doc_type="JOB",
        job_id="11111111-1111-1111-1111-111111111111",
        filename="test.pdf",
        content_type="application/pdf",
        size_bytes=10,
        storage_provider="cloudinary",
        storage_key="abc123",
        url="https://example.com/test.pdf",
        uploaded_by=get_user_model().objects.create_user(
            username="admin1", password="pass123", role="ADMIN"
        ),
    )

    api = APIClient()
    resp = api.get(f"/api/documents/{doc.id}/download/")
    assert resp.status_code == 401


@pytest.mark.django_db
def test_document_download_returns_attachment(monkeypatch):
    User = get_user_model()
    user = User.objects.create_user(username="admin1", password="pass123", role="ADMIN")

    doc = Document.objects.create(
        doc_type="JOB",
        job_id="11111111-1111-1111-1111-111111111111",
        filename="test.pdf",
        content_type="application/pdf",
        size_bytes=10,
        storage_provider="cloudinary",
        storage_key="abc123",
        url="https://example.com/test.pdf",
        uploaded_by=user,
    )

    class DummyResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return b"PDFDATA"

    def fake_urlopen(url):
        assert url == doc.url
        return DummyResponse()

    monkeypatch.setattr("documents.views.urllib_request.urlopen", fake_urlopen)

    api = APIClient()
    login = api.post("/api/auth/login/", {"username": "admin1", "password": "pass123"}, format="json")
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

    resp = api.get(f"/api/documents/{doc.id}/download/")
    assert resp.status_code == 200
    assert resp.content == b"PDFDATA"
    assert resp["Content-Type"] == "application/pdf"
    assert 'attachment; filename="test.pdf"' == resp["Content-Disposition"]
