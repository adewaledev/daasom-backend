from django.contrib.auth.models import AbstractUser
from django.db import models

from accounts.roles import UserRole


class User(AbstractUser):
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.VIEWER,
    )
