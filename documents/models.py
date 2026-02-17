from django.db import models

# Create your models here.
import uuid
from django.db import models


class Document(models.Model):
    class DocType(models.TextChoices):
        JOB = "JOB", "Job"
        INVOICE = "INVOICE", "Invoice"
        RECEIPT = "RECEIPT", "Receipt"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    doc_type = models.CharField(max_length=20, choices=DocType.choices)

    job_id = models.UUIDField(null=True, blank=True)
    invoice_id = models.UUIDField(null=True, blank=True)
    receipt_id = models.UUIDField(null=True, blank=True)

    filename = models.CharField(max_length=255)
    content_type = models.CharField(max_length=120, blank=True, default="")
    size_bytes = models.BigIntegerField(default=0)

    storage_provider = models.CharField(max_length=30, default="cloudinary")
    storage_key = models.CharField(max_length=255)  # cloudinary public_id
    url = models.URLField()

    uploaded_by = models.ForeignKey(
        "accounts.User", on_delete=models.PROTECT, related_name="documents")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["job_id"]),
            models.Index(fields=["invoice_id"]),
            models.Index(fields=["receipt_id"]),
        ]
