from rest_framework.decorators import action
from tracking.serializers import JobMilestoneSerializer
from tracking.models import JobMilestone
from rest_framework.response import Response
from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from jobs.models import Job
from jobs.serializers import JobSerializer
from jobs.permissions import CanManageJobs


class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all().select_related("client")
    serializer_class = JobSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [CanManageJobs()]
        return [IsAuthenticated()]

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])
    def milestones(self, request, pk=None):
        job = self.get_object()
        qs = JobMilestone.objects.filter(job=job).select_related(
            "template").order_by("template__sort_order")
        return Response(JobMilestoneSerializer(qs, many=True).data)
