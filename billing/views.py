from payments.models import Receipt
from django.db.models import Sum
from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from billing.models import Invoice, InvoiceAddon
from billing.serializers import InvoiceSerializer, InvoiceAddonSerializer
from billing.permissions import CanCreateInvoice, CanManageInvoiceStatus
from billing.services import recompute_invoice_totals


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all().select_related("job").prefetch_related("addons")
    serializer_class = InvoiceSerializer

    def get_permissions(self):
        if self.action in ["create"]:
            return [CanCreateInvoice()]
        if self.action in ["issue", "mark_paid", "mark_partial", "void"]:
            return [CanManageInvoiceStatus()]
        return [IsAuthenticated()]

    @action(detail=True, methods=["post"])
    def refresh_totals(self, request, pk=None):
        invoice = self.get_object()
        recompute_invoice_totals(invoice)
        return Response(InvoiceSerializer(invoice).data)

    @action(detail=True, methods=["post"])
    def issue(self, request, pk=None):
        invoice = self.get_object()
        invoice.status = "ISSUED"
        invoice.save(update_fields=["status", "updated_at"])
        return Response(InvoiceSerializer(invoice).data)

    @action(detail=True, methods=["post"])
    def mark_partial(self, request, pk=None):
        invoice = self.get_object()
        invoice.status = "PARTIALLY_PAID"
        invoice.save(update_fields=["status", "updated_at"])
        return Response(InvoiceSerializer(invoice).data)

    @action(detail=True, methods=["post"])
    def mark_paid(self, request, pk=None):
        invoice = self.get_object()
        invoice.status = "PAID"
        invoice.save(update_fields=["status", "updated_at"])
        return Response(InvoiceSerializer(invoice).data)

    @action(detail=True, methods=["post"])
    def void(self, request, pk=None):
        invoice = self.get_object()
        invoice.status = "VOID"
        invoice.save(update_fields=["status", "updated_at"])
        return Response(InvoiceSerializer(invoice).data)

    from rest_framework.decorators import action

    @action(detail=True, methods=["get"])
    def payment_summary(self, request, pk=None):
        invoice = self.get_object()

        paid = Receipt.objects.filter(invoice=invoice).aggregate(
            total=Sum("amount"))["total"] or 0
        total = invoice.grand_total
        due = total - paid
        if due < 0:
            due = 0

        return Response({
            "invoice_id": str(invoice.id),
            "total": str(total),
            "paid": str(paid),
            "due": str(due),
            "status": invoice.status,
        })


class InvoiceAddonViewSet(viewsets.ModelViewSet):
    queryset = InvoiceAddon.objects.all().select_related("invoice")
    serializer_class = InvoiceAddonSerializer

    def get_permissions(self):
        # allow OPS/ADMIN to add add-ons; accounts/admin can also edit
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [CanCreateInvoice()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        addon = serializer.save()
        recompute_invoice_totals(addon.invoice)
