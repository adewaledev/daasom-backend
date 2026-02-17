from django.db.models import Sum
from billing.models import Invoice
from payments.models import Receipt


def compute_paid(invoice: Invoice):
    return Receipt.objects.filter(invoice=invoice).aggregate(total=Sum("amount"))["total"] or 0


def recompute_invoice_payment(invoice: Invoice) -> dict:
    paid = compute_paid(invoice)
    total = invoice.grand_total
    due = total - paid

    # Avoid negative due if overpaid
    if due < 0:
        due = 0

    # Update status only when it makes sense
    if paid >= total and total > 0:
        invoice.status = "PAID"
        invoice.save(update_fields=["status", "updated_at"])
    elif paid > 0 and paid < total:
        invoice.status = "PARTIALLY_PAID"
        invoice.save(update_fields=["status", "updated_at"])

    return {"paid": str(paid), "due": str(due), "total": str(total)}
