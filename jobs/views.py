from django.utils import timezone
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from tracking.serializers import JobMilestoneSerializer, TrackerEntrySerializer
from tracking.models import JobMilestone, TrackerEntry

from core.rbac import PermissionCode, RBACActionPermissionMixin
from jobs.models import Job
from jobs.serializers import JobSerializer


class JobViewSet(RBACActionPermissionMixin, viewsets.ModelViewSet):
    queryset = Job.objects.all().select_related("client")
    serializer_class = JobSerializer
    write_permission = PermissionCode.JOBS_WRITE
    action_permission_map = {
        "mark_tracker_completed": PermissionCode.TRACKER_WRITE,
        "reopen_tracker": PermissionCode.TRACKER_WRITE,
    }
    read_permission_classes = (IsAuthenticated,)

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])
    def milestones(self, request, pk=None):
        job = self.get_object()
        qs = JobMilestone.objects.filter(job=job).select_related(
            "template").order_by("template__sort_order")
        return Response(JobMilestoneSerializer(qs, many=True).data)

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])
    def tracker_entries(self, request, pk=None):
        job = self.get_object()
        queryset = TrackerEntry.objects.filter(
            job=job).order_by("entry_date", "created_at")
        return Response(TrackerEntrySerializer(queryset, many=True).data)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def mark_tracker_completed(self, request, pk=None):
        job = self.get_object()
        job.tracker_completed = True
        job.tracker_completed_at = timezone.now()
        job.tracker_completed_by = request.user
        job.save(update_fields=[
                 "tracker_completed", "tracker_completed_at", "tracker_completed_by", "updated_at"])
        return Response(JobSerializer(job).data)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def reopen_tracker(self, request, pk=None):
        job = self.get_object()
        job.tracker_completed = False
        job.tracker_completed_at = None
        job.tracker_completed_by = None
        job.save(update_fields=[
                 "tracker_completed", "tracker_completed_at", "tracker_completed_by", "updated_at"])
        return Response(JobSerializer(job).data)
