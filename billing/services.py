from django.db.models import Sum
from expenses.models import Expense
from billing.models import Invoice, InvoiceAddon


def recompute_invoice_totals(invoice: Invoice) -> Invoice:
    expenses_total = (
        Expense.objects.filter(job=invoice.job).aggregate(
            total=Sum("amount"))["total"] or 0
    )
    addons_total = (
        InvoiceAddon.objects.filter(invoice=invoice).aggregate(
            total=Sum("amount"))["total"] or 0
    )
    grand_total = expenses_total + addons_total

    invoice.expenses_total = expenses_total
    invoice.addons_total = addons_total
    invoice.grand_total = grand_total
    invoice.save(update_fields=["expenses_total",
                 "addons_total", "grand_total", "updated_at"])
    return invoice
