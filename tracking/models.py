from django.db import models

# Create your models here.
import uuid
from django.db import models
from jobs.models import Job


class MilestoneTemplate(models.Model):
    class Zone(models.TextChoices):
        DUTY = "DUTY", "Duty Zone"
        FREE = "FREE", "Free Zone"
        EXPORT = "EXPORT", "Export"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    zone = models.CharField(max_length=10, choices=Zone.choices)
    key = models.CharField(max_length=80)          # e.g. "ETA", "DTI_DATE"
    label = models.CharField(max_length=120)       # e.g. "ETA"
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("zone", "key")
        ordering = ["zone", "sort_order"]

    def __str__(self):
        return f"{self.zone}:{self.label}"


class JobMilestone(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        DONE = "DONE", "Done"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(Job, on_delete=models.CASCADE,
                            related_name="milestones")
    template = models.ForeignKey(MilestoneTemplate, on_delete=models.PROTECT)

    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING)
    date = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ("job", "template")
        ordering = ["template__sort_order"]
