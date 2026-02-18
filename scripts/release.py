import os
import sys
from pathlib import Path

# Ensure project root is on sys.path so "config" is importable
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django  # noqa: E402
from django.core.management import call_command  # noqa: E402


def main():
    django.setup()

    call_command("migrate", interactive=False)
    call_command("seed_milestones")

    # Optional: auto-create superuser if env vars exist
    from django.contrib.auth import get_user_model  # noqa: E402

    User = get_user_model()
    username = os.getenv("DJANGO_SUPERUSER_USERNAME")
    email = os.getenv("DJANGO_SUPERUSER_EMAIL", "")
    password = os.getenv("DJANGO_SUPERUSER_PASSWORD")

    if username and password:
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(
                username=username, email=email, password=password)
            print("✅ Superuser created")
        else:
            print("ℹ️ Superuser already exists")
    else:
        print("ℹ️ Superuser env vars not set; skipping")

    print("✅ Release steps done: migrate + seed_milestones")


if __name__ == "__main__":
    main()
