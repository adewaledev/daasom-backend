from rest_framework.permissions import BasePermission


class CanCreateInvoice(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in {"ADMIN", "OPS"}


class CanManageInvoiceStatus(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in {"ADMIN", "ACCOUNTS"}
