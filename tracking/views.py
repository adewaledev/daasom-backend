from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from core.rbac import PermissionCode, RBACActionPermissionMixin
from tracking.models import JobMilestone
from tracking.serializers import JobMilestoneSerializer


class JobMilestoneViewSet(RBACActionPermissionMixin, viewsets.ModelViewSet):
    queryset = JobMilestone.objects.all().select_related("template", "job")
    serializer_class = JobMilestoneSerializer
    write_permission = PermissionCode.TRACKER_WRITE
    read_permission_classes = (IsAuthenticated,)
