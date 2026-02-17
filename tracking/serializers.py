from rest_framework import serializers
from tracking.models import JobMilestone


class JobMilestoneSerializer(serializers.ModelSerializer):
    template_label = serializers.CharField(
        source="template.label", read_only=True)
    template_key = serializers.CharField(source="template.key", read_only=True)
    sort_order = serializers.IntegerField(
        source="template.sort_order", read_only=True)

    class Meta:
        model = JobMilestone
        fields = ("id", "job", "template", "template_key",
                  "template_label", "sort_order", "status", "date")
        read_only_fields = ("id", "template_key",
                            "template_label", "sort_order")
