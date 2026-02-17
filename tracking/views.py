from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from tracking.models import JobMilestone
from tracking.serializers import JobMilestoneSerializer
from jobs.permissions import CanManageJobs


class JobMilestoneViewSet(viewsets.ModelViewSet):
    queryset = JobMilestone.objects.all().select_related("template", "job")
    serializer_class = JobMilestoneSerializer

    def get_permissions(self):
        if self.action in ["update", "partial_update"]:
            return [CanManageJobs()]
        return [IsAuthenticated()]
