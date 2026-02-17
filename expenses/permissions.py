from rest_framework.permissions import BasePermission


class CanCreateExpense(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in {"ADMIN", "OPS"}


class CanApproveExpense(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in {"ADMIN", "ACCOUNTS"}
