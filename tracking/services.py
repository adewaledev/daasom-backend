from tracking.models import MilestoneTemplate, JobMilestone
from jobs.models import Job


def ensure_job_milestones(job: Job) -> None:
    templates = MilestoneTemplate.objects.filter(
        zone=job.zone).order_by("sort_order")
    # create only missing (safe to call multiple times)
    existing = set(
        JobMilestone.objects.filter(job=job).values_list(
            "template_id", flat=True)
    )
    to_create = [
        JobMilestone(job=job, template=t)
        for t in templates
        if t.id not in existing
    ]
    if to_create:
        JobMilestone.objects.bulk_create(to_create)
