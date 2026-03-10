from billing.models import Invoice


def recompute_invoice_totals(invoice: Invoice) -> Invoice:
    # Invoices are standalone and no longer derived from expenses/add-ons.
    if invoice.expenses_total != 0 or invoice.addons_total != 0:
        invoice.expenses_total = 0
        invoice.addons_total = 0
        invoice.save(update_fields=["expenses_total",
                     "addons_total", "updated_at"])
    return invoice
