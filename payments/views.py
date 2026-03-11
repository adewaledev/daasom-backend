from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.rbac import PermissionCode, RBACActionPermissionMixin
from payments.models import Receipt
from payments.serializers import ReceiptSerializer
from payments.services import recompute_invoice_payment


class ReceiptViewSet(RBACActionPermissionMixin, viewsets.ModelViewSet):
    queryset = Receipt.objects.all().select_related("invoice")
    serializer_class = ReceiptSerializer
    write_permission = PermissionCode.RECEIPTS_WRITE
    read_permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        receipt = serializer.save()
        recompute_invoice_payment(receipt.invoice)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def summary(self, request):
        invoice_id = request.query_params.get("invoice_id")
        if not invoice_id:
            return Response({"detail": "invoice_id is required"}, status=400)

        # fetch invoice through the receipts relation
        invoice = Receipt.objects.filter(invoice_id=invoice_id).first()
        if invoice is None:
            # If no receipts yet, we still need invoice totals: handle in billing endpoint later
            return Response({"invoice_id": invoice_id, "paid": "0", "due": None}, status=200)

        data = recompute_invoice_payment(invoice.invoice)
        return Response({"invoice_id": invoice_id, **data})
