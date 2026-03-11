from rest_framework.permissions import BasePermission, IsAuthenticated

from accounts.roles import UserRole, normalize_user_role


class PermissionCode:
    CLIENTS_WRITE = "clients.write"
    JOBS_WRITE = "jobs.write"
    TRACKER_WRITE = "tracker.write"
    EXPENSES_WRITE = "expenses.write"
    INVOICES_WRITE = "invoices.write"
    RECEIPTS_WRITE = "receipts.write"
    DOCUMENTS_WRITE = "documents.write"


ALL_WRITE_PERMISSIONS = frozenset(
    {
        PermissionCode.CLIENTS_WRITE,
        PermissionCode.JOBS_WRITE,
        PermissionCode.TRACKER_WRITE,
        PermissionCode.EXPENSES_WRITE,
        PermissionCode.INVOICES_WRITE,
        PermissionCode.RECEIPTS_WRITE,
        PermissionCode.DOCUMENTS_WRITE,
    }
)

ROLE_PERMISSION_MATRIX = {
    UserRole.ADMIN: ALL_WRITE_PERMISSIONS,
    UserRole.OPS: frozenset(
        {
            PermissionCode.CLIENTS_WRITE,
            PermissionCode.JOBS_WRITE,
            PermissionCode.TRACKER_WRITE,
            PermissionCode.EXPENSES_WRITE,
            PermissionCode.INVOICES_WRITE,
            PermissionCode.DOCUMENTS_WRITE,
        }
    ),
    UserRole.ACCOUNTS: frozenset(
        {
            PermissionCode.INVOICES_WRITE,
            PermissionCode.RECEIPTS_WRITE,
            PermissionCode.DOCUMENTS_WRITE,
        }
    ),
    UserRole.VIEWER: frozenset(),
}


WRITE_ACTIONS = frozenset({"create", "update", "partial_update", "destroy"})


def get_user_role(user) -> str:
    return normalize_user_role(getattr(user, "role", None))


def user_has_permission(user, permission_code: str) -> bool:
    if not getattr(user, "is_authenticated", False):
        return False
    return permission_code in ROLE_PERMISSION_MATRIX[get_user_role(user)]


class AllowedRolesPermission(BasePermission):
    allowed_roles = frozenset()

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and get_user_role(user) in self.allowed_roles
        )


class PermissionByCode(BasePermission):
    required_permission = None

    def has_permission(self, request, view):
        if self.required_permission is None:
            return False
        return user_has_permission(request.user, self.required_permission)


class RBACActionPermissionMixin:
    write_permission = None
    action_permission_map = {}
    read_permission_classes = (IsAuthenticated,)

    def get_required_permission(self):
        if self.action in self.action_permission_map:
            return self.action_permission_map[self.action]
        if self.action in WRITE_ACTIONS:
            return self.write_permission
        return None

    def get_permissions(self):
        required_permission = self.get_required_permission()
        if required_permission:
            permission = PermissionByCode()
            permission.required_permission = required_permission
            return [permission]
        return [permission_class() for permission_class in self.read_permission_classes]
