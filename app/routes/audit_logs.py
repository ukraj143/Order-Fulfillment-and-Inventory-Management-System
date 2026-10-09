from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_roles
from app.services.audit_log_service import AuditLogService


router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs"],
)


@router.get("/")
def list_audit_logs(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("Admin")),
):
    return AuditLogService(db).get_all()


@router.get("/user/{user_id}")
def get_user_audit_logs(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("Admin")),
):
    return AuditLogService(db).get_by_user(user_id)


@router.get("/entity/{entity_type}/{entity_id}")
def get_entity_audit_logs(
    entity_type: str,
    entity_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("Admin")),
):
    return AuditLogService(db).get_by_entity(
        entity_type=entity_type,
        entity_id=entity_id,
    )