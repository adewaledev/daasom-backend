import os
import sys
import django
from django.core.management import call_command

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()


def main():
    call_command("migrate", interactive=False)
    # seed milestones (safe to re-run if command is idempotent)
    call_command("seed_milestones")
    print("✅ Release steps done: migrate + seed_milestones")


if __name__ == "__main__":
    main()
