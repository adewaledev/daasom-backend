from rest_framework import serializers
from payments.models import Receipt


class ReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receipt
        fields = "__all__"
        read_only_fields = ("id", "created_at")

    def validate(self, attrs):
        invoice = attrs.get("invoice")
        reference = (attrs.get("reference") or "").strip()

        # Only enforce if reference provided
        if invoice and reference:
            qs = Receipt.objects.filter(invoice=invoice, reference=reference)
            if self.instance:
                qs = qs.exclude(id=self.instance.id)

            if qs.exists():
                raise serializers.ValidationError(
                    {"reference": "Duplicate reference for this invoice."}
                )

        return attrs
