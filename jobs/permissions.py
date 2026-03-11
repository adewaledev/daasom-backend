from core.rbac import PermissionByCode, PermissionCode


class CanManageJobs(PermissionByCode):
    required_permission = PermissionCode.JOBS_WRITE
