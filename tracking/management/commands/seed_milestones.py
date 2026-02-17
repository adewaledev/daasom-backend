from django.core.management.base import BaseCommand
from tracking.models import MilestoneTemplate


def keyify(label: str) -> str:
    return (
        label.strip()
        .upper()
        .replace("/", "_")
        .replace(" ", "_")
        .replace("-", "_")
        .replace("__", "_")
    )


class Command(BaseCommand):
    help = "Seed milestone templates for DUTY, FREE, EXPORT zones."

    def handle(self, *args, **options):
        duty = [
            "ETA",
            "ATA",
            "Complete_Documents_Date",
            "DTI_Date",
            "Duty_Paid_Date",
            "Exam_Date",
            "Release_EC_Date",
            "Date_Delivered",
            "DATE_INVOICED",
            "Date_of_Payment",
            "Container_Returned_Date",
            "Refund_Applied_Date",
            "Refund_Paid_Date",
            "EC_Dispatched_Date",
            "EC_Collected_By",
        ]

        free_export = [
            "ETA",
            "ATA",
            "Complete_Documents_Date",
            "DTI_Date",
            "NEPZA_Request_Date",
            "NEPZA_Received_Date",
            "Cover_Letter_Received_Date",
            "Release_Date",
            "TDO_Date",
            "Exam_Date",
            "Release_EC_Date",
            "Date_Delivered",
            "DATE_INVOICED",
            "Date_of_Payment",
            "Container_Returned_Date",
            "Refund_Applied_Date",
            "Refund_Paid_Date",
        ]

        def upsert(zone: str, labels: list[str]):
            created = 0
            updated = 0
            for i, label in enumerate(labels, start=1):
                key = keyify(label)
                obj, was_created = MilestoneTemplate.objects.update_or_create(
                    zone=zone,
                    key=key,
                    defaults={"label": label, "sort_order": i},
                )
                created += 1 if was_created else 0
                updated += 0 if was_created else 1
            return created, updated

        c1, u1 = upsert("DUTY", duty)
        c2, u2 = upsert("FREE", free_export)
        c3, u3 = upsert("EXPORT", free_export)

        self.stdout.write(self.style.SUCCESS(
            f"Seeded milestone templates. "
            f"DUTY: created={c1}, updated={u1}; "
            f"FREE: created={c2}, updated={u2}; "
            f"EXPORT: created={c3}, updated={u3}"
        ))
