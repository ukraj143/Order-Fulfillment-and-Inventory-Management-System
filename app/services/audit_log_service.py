from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.repositories.audit_log_repository import AuditLogRepository
from app.schemas.audit_log import AuditLogCreate


class AuditLogService:
    def __init__(self, db: Session):
        self.repository = AuditLogRepository(db)

    def create(self, data: AuditLogCreate) -> AuditLog:
        audit_log = AuditLog(
            user_id=data.user_id,
            action=data.action,
            entity_type=data.entity_type,
            entity_id=data.entity_id,
            description=data.description,
        )

        return self.repository.create(audit_log)

    def log(
        self,
        user_id: int | None,
        action: str,
        entity_type: str,
        entity_id: int | str | None = None,
        description: str | None = None,
    ) -> AuditLog:
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=str(entity_id) if entity_id is not None else None,
            description=description,
        )

        return self.repository.create(audit_log)

    def get(self, audit_log_id: int) -> AuditLog | None:
        return self.repository.get_by_id(audit_log_id)

    def get_all(self) -> list[AuditLog]:
        return self.repository.get_all()

    def get_by_user(self, user_id: int) -> list[AuditLog]:
        return self.repository.get_by_user(user_id)

    def get_by_entity(
        self,
        entity_type: str,
        entity_id: str,
    ) -> list[AuditLog]:
        return self.repository.get_by_entity(
            entity_type,
            entity_id,
        )