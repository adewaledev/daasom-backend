from core.rbac import PermissionByCode, PermissionCode


class CanCreateInvoice(PermissionByCode):
    required_permission = PermissionCode.INVOICES_WRITE


class CanManageInvoiceStatus(PermissionByCode):
    required_permission = PermissionCode.INVOICES_WRITE
