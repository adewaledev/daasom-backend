from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from jobs.models import Job
from tracking.models import JobMilestone

# the milestone keys we want surfaced in the tracker view
TRACKER_KEYS = [
    "ETA",
    "ATA",
    "DTI_DATE",
    "DUTY_PAID_DATE",
    "EXAM_DATE",
    "RELEASE_EC_DATE",
    "DATE_DELIVERED",
    "DATE_INVOICED",
    "DATE_OF_PAYMENT",
]


class TrackerView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        zone = request.query_params.get("zone")
        client_code = request.query_params.get("client_code")
        file_number = request.query_params.get("file_number")

        jobs = Job.objects.select_related(
            "client").all().order_by("-created_at")

        if zone:
            jobs = jobs.filter(zone=zone)
        if client_code:
            jobs = jobs.filter(client__client_code=client_code)
        if file_number:
            jobs = jobs.filter(file_number__icontains=file_number)

        job_ids = [j.id for j in jobs]

        milestones = (
            JobMilestone.objects
            .filter(job_id__in=job_ids, template__key__in=TRACKER_KEYS)
            .select_related("template")
        )

        # map: job_id -> {key: {status,date}}
        mm = {}
        for m in milestones:
            mm.setdefault(str(m.job_id), {})[m.template.key] = {
                "status": m.status,
                "date": m.date.isoformat() if m.date else None,
            }

        rows = []
        for j in jobs:
            rows.append({
                "job_id": str(j.id),
                "zone": j.zone,
                "file_number": j.file_number,
                "client_code": j.client.client_code,
                "client_name": j.client.client_name,
                "bl_awb": j.bl_awb,
                "weight_kg": str(j.weight_kg) if j.weight_kg is not None else None,
                "container_40ft": j.container_40ft,
                "container_20ft": j.container_20ft,
                "container_number": j.container_number,
                "transit_days": j.transit_days,
                "milestones": mm.get(str(j.id), {}),
            })

        return Response(rows)
