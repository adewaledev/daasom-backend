from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum

from expenses.models import Expense
from expenses.serializers import ExpenseSerializer
from expenses.permissions import CanCreateExpense, CanApproveExpense
from rest_framework.exceptions import MethodNotAllowed


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all().select_related("job")
    serializer_class = ExpenseSerializer

    def get_permissions(self):
        if self.action in ["create"]:
            return [CanCreateExpense()]
        if self.action in ["update", "partial_update"]:
            return [CanApproveExpense()]
        if self.action in ["destroy"]:
            # only Accounts/Admin can delete (or we disable below)
            return [CanApproveExpense()]
        return [IsAuthenticated()]

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def totals(self, request):
        job_id = request.query_params.get("job_id")
        qs = self.queryset
        if job_id:
            qs = qs.filter(job_id=job_id)

        total = qs.aggregate(total=Sum("amount"))["total"] or 0
        return Response({"job_id": job_id, "total": str(total)})

    def destroy(self, request, *args, **kwargs):
        raise MethodNotAllowed("DELETE")
