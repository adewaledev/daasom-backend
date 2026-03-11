from core.rbac import PermissionByCode, PermissionCode


class CanCreateExpense(PermissionByCode):
    required_permission = PermissionCode.EXPENSES_WRITE


class CanApproveExpense(PermissionByCode):
    required_permission = PermissionCode.EXPENSES_WRITE
