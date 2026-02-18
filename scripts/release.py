from django.contrib.auth import get_user_model
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


User = get_user_model()
username = os.getenv("DJANGO_SUPERUSER_USERNAME")
email = os.getenv("DJANGO_SUPERUSER_EMAIL")
password = os.getenv("DJANGO_SUPERUSER_PASSWORD")

if username and password:
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(
            username=username, email=email or "", password=password)
        print("✅ Superuser created")
    else:
        print("ℹ️ Superuser already exists")
else:
    print("ℹ️ Superuser env vars not set; skipping")


if __name__ == "__main__":
    main()
