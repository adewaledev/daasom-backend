from core.rbac import PermissionByCode, PermissionCode


class CanManageClient(PermissionByCode):
    required_permission = PermissionCode.CLIENTS_WRITE
