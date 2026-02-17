from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        OPS = "OPS", "Operations"
        ACCOUNTS = "ACCOUNTS", "Accounts"
        VIEWER = "VIEWER", "Viewer"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.VIEWER,
    )