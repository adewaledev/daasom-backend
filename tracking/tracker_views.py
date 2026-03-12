from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from jobs.models import Job
from tracking.models import TrackerEntry


class TrackerView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        zone = request.query_params.get("zone")
        client_code = request.query_params.get("client_code")
        file_number = request.query_params.get("file_number")
        tracker_completed = request.query_params.get("tracker_completed")

        jobs = Job.objects.select_related(
            "client", "tracker_completed_by").all().order_by("-created_at")

        if zone:
            jobs = jobs.filter(zone=zone)
        if client_code:
            jobs = jobs.filter(client__client_code=client_code)
        if file_number:
            jobs = jobs.filter(file_number__icontains=file_number)
        if tracker_completed is not None:
            normalized = tracker_completed.strip().lower()
            if normalized in {"true", "1", "yes"}:
                jobs = jobs.filter(tracker_completed=True)
            elif normalized in {"false", "0", "no"}:
                jobs = jobs.filter(tracker_completed=False)

        job_ids = [j.id for j in jobs]

        entries = TrackerEntry.objects.filter(
            job_id__in=job_ids).order_by("entry_date", "created_at")

        tracker_rows = {}
        for entry in entries:
            tracker_rows.setdefault(str(entry.job_id), []).append(
                {
                    "id": str(entry.id),
                    "entry_date": entry.entry_date.isoformat(),
                    "progress_report": entry.progress_report,
                    "next_step": entry.next_step,
                    "created_at": entry.created_at.isoformat().replace("+00:00", "Z"),
                    "updated_at": entry.updated_at.isoformat().replace("+00:00", "Z"),
                }
            )

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
                "tracker_completed": j.tracker_completed,
                "tracker_completed_at": j.tracker_completed_at.isoformat().replace("+00:00", "Z") if j.tracker_completed_at else None,
                "tracker_completed_by": j.tracker_completed_by.username if j.tracker_completed_by else None,
                "tracker_entries": tracker_rows.get(str(j.id), []),
            })

        return Response(rows)
