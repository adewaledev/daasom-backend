from django.db import models


class UserRole(models.TextChoices):
    ADMIN = "ADMIN", "Admin"
    OPS = "OPS", "Operations"
    ACCOUNTS = "ACCOUNTS", "Accounts"
    VIEWER = "VIEWER", "Viewer"


VALID_USER_ROLES = {value for value, _ in UserRole.choices}


def normalize_user_role(role: str | None) -> str:
    if role in VALID_USER_ROLES:
        return role
    return UserRole.VIEWER
