from django.db.models.signals import post_save
from django.dispatch import receiver

from ledger.models import LedgerEntry
from expenses.models import Expense
from payments.models import Receipt


@receiver(post_save, sender=Expense)
def upsert_ledger_from_expense(sender, instance: Expense, **kwargs):
    LedgerEntry.objects.update_or_create(
        source_id=instance.id,
        defaults={
            "entry_type": "EXPENSE",
            "direction": "DEBIT",
            "job_id": instance.job_id,
            "invoice_id": getattr(getattr(instance.job, "invoice", None), "id", None),
            "description": f"{instance.category}: {instance.description}".strip(": "),
            "amount": instance.amount,
            "currency": instance.currency,
            "event_date": instance.expense_date,
        },
    )


@receiver(post_save, sender=Receipt)
def upsert_ledger_from_receipt(sender, instance: Receipt, **kwargs):
    LedgerEntry.objects.update_or_create(
        source_id=instance.id,
        defaults={
            "entry_type": "RECEIPT",
            "direction": "CREDIT",
            "job_id": instance.invoice.job_id,
            "invoice_id": instance.invoice_id,
            "description": f"Receipt {instance.method} {instance.reference}".strip(),
            "amount": instance.amount,
            "currency": instance.currency,
            "event_date": instance.payment_date,
        },
    )
