from payments.models import Receipt
from django.db.models import Sum
from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.rbac import PermissionCode, RBACActionPermissionMixin
from billing.models import Invoice
from billing.serializers import InvoiceSerializer
from billing.services import recompute_invoice_totals


class InvoiceViewSet(RBACActionPermissionMixin, viewsets.ModelViewSet):
    queryset = Invoice.objects.all().select_related("job")
    serializer_class = InvoiceSerializer
    write_permission = PermissionCode.INVOICES_WRITE
    action_permission_map = {
        "refresh_totals": PermissionCode.INVOICES_WRITE,
        "issue": PermissionCode.INVOICES_WRITE,
        "mark_partial": PermissionCode.INVOICES_WRITE,
        "mark_paid": PermissionCode.INVOICES_WRITE,
        "void": PermissionCode.INVOICES_WRITE,
    }
    read_permission_classes = (IsAuthenticated,)

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
