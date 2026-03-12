from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum

from core.rbac import PermissionCode, RBACActionPermissionMixin
from expenses.models import Expense
from expenses.serializers import ExpenseSerializer


class ExpenseViewSet(RBACActionPermissionMixin, viewsets.ModelViewSet):
    queryset = Expense.objects.all().select_related("job")
    serializer_class = ExpenseSerializer
    write_permission = PermissionCode.EXPENSES_WRITE
    read_permission_classes = (IsAuthenticated,)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def totals(self, request):
        job_id = request.query_params.get("job_id")
        qs = self.queryset
        if job_id:
            qs = qs.filter(job_id=job_id)

        total = qs.aggregate(total=Sum("amount"))["total"] or 0
        return Response({"job_id": job_id, "total": f"{total:.2f}"})
