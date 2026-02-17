from django.db import models

# Create your models here.
import uuid
from django.db import models
from clients.models import Client


class Job(models.Model):
    class Zone(models.TextChoices):
        DUTY = "DUTY", "Duty Zone"
        FREE = "FREE", "Free Zone"
        EXPORT = "EXPORT", "Export"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(
        Client, on_delete=models.PROTECT, related_name="jobs")
    zone = models.CharField(max_length=10, choices=Zone.choices)

    file_number = models.CharField(max_length=80, unique=True)
    quantity = models.PositiveIntegerField(default=0)

    bl_awb = models.CharField(max_length=120, blank=True, default="")
    weight_kg = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True)

    container_40ft = models.PositiveIntegerField(default=0)
    container_20ft = models.PositiveIntegerField(default=0)
    others = models.CharField(max_length=255, blank=True, default="")

    description = models.TextField(blank=True, default="")
    container_number = models.CharField(max_length=120, blank=True, default="")
    transit_days = models.PositiveIntegerField(null=True, blank=True)

    duty_amount = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True)
    refund_amount = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.file_number} - {self.client.client_name}"
