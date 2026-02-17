from django.db import models

# Create your models here.
import uuid
from django.db import models


class LedgerEntry(models.Model):
    class EntryType(models.TextChoices):
        EXPENSE = "EXPENSE", "Expense"
        RECEIPT = "RECEIPT", "Receipt"

    class Direction(models.TextChoices):
        DEBIT = "DEBIT", "Debit"   # money out
        CREDIT = "CREDIT", "Credit"  # money in

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    entry_type = models.CharField(max_length=20, choices=EntryType.choices)
    direction = models.CharField(max_length=10, choices=Direction.choices)

    # link back to source (ensures idempotent sync)
    source_id = models.UUIDField(unique=True)

    # optional links for filtering
    job_id = models.UUIDField(null=True, blank=True)
    invoice_id = models.UUIDField(null=True, blank=True)

    description = models.CharField(max_length=255, blank=True, default="")
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=10, default="NGN")

    event_date = models.DateField()  # expense_date or payment_date
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["job_id", "event_date"]),
            models.Index(fields=["invoice_id", "event_date"]),
            models.Index(fields=["entry_type", "event_date"]),
        ]
