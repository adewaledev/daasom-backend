from rest_framework.permissions import IsAuthenticated
from accounts.permissions import IsAdmin, IsOps
from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response({"status": "ok"})


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        u = request.user
        return Response({"id": u.id, "username": u.username})


class AdminOnlyView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        return Response({"ok": True, "scope": "admin"})


class OpsOnlyView(APIView):
    permission_classes = [IsOps]

    def get(self, request):
        return Response({"ok": True, "scope": "ops"})
