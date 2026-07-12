from fastapi import APIRouter, Depends
from ..services.audit_service import audit_service
from ..services.auth_service import RoleChecker

router = APIRouter(prefix="/audit", tags=["audit"])

@router.get("/logs")
def get_audit_logs(current_user: dict = Depends(RoleChecker(["admin"]))):
    logs = audit_service.get_logs()
    
    # Audit log the access of the audit logs itself
    audit_service.log_action(
        username=current_user["sub"],
        user_role=current_user["role"],
        action="VIEW_AUDIT_LOGS",
        resource="system:audit_logs",
        details="Admin accessed system security audit trails"
    )
    
    return logs
