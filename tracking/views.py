from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from core.rbac import PermissionCode, RBACActionPermissionMixin
from tracking.models import JobMilestone, TrackerEntry
from tracking.serializers import JobMilestoneSerializer, TrackerEntrySerializer


class JobMilestoneViewSet(RBACActionPermissionMixin, viewsets.ModelViewSet):
    queryset = JobMilestone.objects.all().select_related("template", "job")
    serializer_class = JobMilestoneSerializer
    write_permission = PermissionCode.TRACKER_WRITE
    read_permission_classes = (IsAuthenticated,)


class TrackerEntryViewSet(RBACActionPermissionMixin, viewsets.ModelViewSet):
    queryset = TrackerEntry.objects.all().select_related("job")
    serializer_class = TrackerEntrySerializer
    write_permission = PermissionCode.TRACKER_WRITE
    read_permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = super().get_queryset()
        job_id = self.request.query_params.get("job_id")
        if job_id:
            queryset = queryset.filter(job_id=job_id)
        return queryset
