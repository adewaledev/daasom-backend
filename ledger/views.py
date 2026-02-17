from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from ledger.models import LedgerEntry
from ledger.serializers import LedgerEntrySerializer


class LedgerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LedgerEntry.objects.all().order_by("-event_date", "-created_at")
    serializer_class = LedgerEntrySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        job_id = self.request.query_params.get("job_id")
        invoice_id = self.request.query_params.get("invoice_id")
        entry_type = self.request.query_params.get("entry_type")

        if job_id:
            qs = qs.filter(job_id=job_id)
        if invoice_id:
            qs = qs.filter(invoice_id=invoice_id)
        if entry_type:
            qs = qs.filter(entry_type=entry_type)

        return qs
