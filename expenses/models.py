from django.db import models

# Create your models here.
import uuid
from django.db import models
from jobs.models import Job


class Expense(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        SUBMITTED = "SUBMITTED", "Submitted"
        APPROVED = "APPROVED", "Approved"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    job = models.ForeignKey(
        Job, on_delete=models.CASCADE, related_name="expenses")

    # we’ll add categories table later if needed
    category = models.CharField(max_length=80)
    description = models.CharField(max_length=255, blank=True, default="")
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=10, default="NGN")

    expense_date = models.DateField()

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.job.file_number} - {self.category} - {self.amount}"
