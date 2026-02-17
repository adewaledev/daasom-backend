from rest_framework import serializers
from billing.models import Invoice, InvoiceAddon


class InvoiceAddonSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceAddon
        fields = "__all__"
        read_only_fields = ("id", "created_at")


class InvoiceSerializer(serializers.ModelSerializer):
    addons = InvoiceAddonSerializer(many=True, read_only=True)

    class Meta:
        model = Invoice
        fields = "__all__"
        read_only_fields = ("id", "expenses_total", "addons_total",
                            "grand_total", "created_at", "updated_at")
