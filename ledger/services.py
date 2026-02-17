from ledger.models import LedgerEntry
from expenses.models import Expense
from payments.models import Receipt


def sync_expenses_to_ledger():
    for e in Expense.objects.all().select_related("job"):
        LedgerEntry.objects.update_or_create(
            source_id=e.id,
            defaults={
                "entry_type": "EXPENSE",
                "direction": "DEBIT",
                "job_id": e.job_id,
                "invoice_id": getattr(getattr(e.job, "invoice", None), "id", None),
                "description": f"{e.category}: {e.description}".strip(": "),
                "amount": e.amount,
                "currency": e.currency,
                "event_date": e.expense_date,
            },
        )


def sync_receipts_to_ledger():
    for r in Receipt.objects.all().select_related("invoice", "invoice__job"):
        LedgerEntry.objects.update_or_create(
            source_id=r.id,
            defaults={
                "entry_type": "RECEIPT",
                "direction": "CREDIT",
                "job_id": r.invoice.job_id,
                "invoice_id": r.invoice_id,
                "description": f"Receipt {r.method} {r.reference}".strip(),
                "amount": r.amount,
                "currency": r.currency,
                "event_date": r.payment_date,
            },
        )


def sync_ledger():
    sync_expenses_to_ledger()
    sync_receipts_to_ledger()
