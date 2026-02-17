from django.db import models

# Create your models here.
import uuid
from django.db import models
from billing.models import Invoice


class Receipt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(
        Invoice, on_delete=models.PROTECT, related_name="receipts")

    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=10, default="NGN")

    payment_date = models.DateField()
    method = models.CharField(
        max_length=50, blank=True, default="")     # transfer/cash/etc
    reference = models.CharField(
        max_length=120, blank=True, default="")  # bank ref

    notes = models.CharField(max_length=255, blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["invoice", "reference"],
                name="uniq_receipt_reference_per_invoice",
                condition=~models.Q(reference=""),
            )
        ]
