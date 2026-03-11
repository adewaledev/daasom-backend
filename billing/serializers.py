from rest_framework import serializers

from billing.models import Invoice


class InvoiceSerializer(serializers.ModelSerializer):
    # Backward/frontend compatibility: accept/use `amount` as alias of `invoice_amount`.
    amount = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
        source="invoice_amount",
        required=False,
    )

    class Meta:
        model = Invoice
        fields = "__all__"
        read_only_fields = ("id", "expenses_total",
                            "addons_total", "created_at", "updated_at")

    def validate(self, attrs):
        invoice_amount = attrs.get("invoice_amount")
        grand_total = attrs.get("grand_total")

        if invoice_amount is not None and grand_total is None:
            attrs["grand_total"] = invoice_amount
        elif grand_total is not None and invoice_amount is None:
            attrs["invoice_amount"] = grand_total

        return attrs
