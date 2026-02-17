from django.db.models.signals import post_save
from django.dispatch import receiver
from jobs.models import Job
from tracking.services import ensure_job_milestones


@receiver(post_save, sender=Job)
def create_milestones_on_job_create(sender, instance: Job, created: bool, **kwargs):
    if created:
        ensure_job_milestones(instance)
