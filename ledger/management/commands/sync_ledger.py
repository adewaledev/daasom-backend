from django.core.management.base import BaseCommand
from ledger.services import sync_ledger


class Command(BaseCommand):
    help = "Sync ledger entries from expenses and receipts (idempotent)."

    def handle(self, *args, **options):
        sync_ledger()
        self.stdout.write(self.style.SUCCESS("Ledger sync complete."))
