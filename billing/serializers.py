from rest_framework import serializers

from billing.models import Invoice


class InvoiceSerializer(serializers.ModelSerializer):
    # Backward/frontend compatibility: accept/use `amount` as alias of `grand_total`.
    amount = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
        source="grand_total",
        required=False,
    )

    class Meta:
        model = Invoice
        fields = "__all__"
        read_only_fields = ("id", "expenses_total",
                            "addons_total", "created_at", "updated_at")
