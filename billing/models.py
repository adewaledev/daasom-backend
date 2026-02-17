from django.db import models

# Create your models here.
import uuid
from django.db import models
from jobs.models import Job


class Invoice(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        ISSUED = "ISSUED", "Issued"
        PARTIALLY_PAID = "PARTIALLY_PAID", "Partially Paid"
        PAID = "PAID", "Paid"
        VOID = "VOID", "Void"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.OneToOneField(
        Job, on_delete=models.PROTECT, related_name="invoice")

    invoice_number = models.CharField(max_length=50, unique=True)
    currency = models.CharField(max_length=10, default="NGN")

    expenses_total = models.DecimalField(
        max_digits=14, decimal_places=2, default=0)
    addons_total = models.DecimalField(
        max_digits=14, decimal_places=2, default=0)
    grand_total = models.DecimalField(
        max_digits=14, decimal_places=2, default=0)

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT)

    issued_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)

    notes = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class InvoiceAddon(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name="addons")

    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=14, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
