from accounts.roles import UserRole
from core.rbac import AllowedRolesPermission


class IsAdmin(AllowedRolesPermission):
    allowed_roles = frozenset({UserRole.ADMIN})


class IsOps(AllowedRolesPermission):
    allowed_roles = frozenset({UserRole.ADMIN, UserRole.OPS})


class IsAccounts(AllowedRolesPermission):
    allowed_roles = frozenset({UserRole.ADMIN, UserRole.ACCOUNTS})
