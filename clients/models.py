from django.db import models

# Create your models here.
import uuid
from django.db import models


class Client(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client_code = models.CharField(max_length=50, unique=True)
    client_prefix = models.CharField(max_length=50)
    client_name = models.CharField(max_length=255)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.client_name} ({self.client_code})"
