from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets

from core.rbac import PermissionCode, RBACActionPermissionMixin
from .models import Client
from .serializers import ClientSerializer


class ClientViewSet(RBACActionPermissionMixin, viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    write_permission = PermissionCode.CLIENTS_WRITE
