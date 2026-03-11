from core.rbac import PermissionByCode, PermissionCode


class CanCreateReceipt(PermissionByCode):
    required_permission = PermissionCode.RECEIPTS_WRITE
