from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


class AuditLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, audit_log_id: int) -> AuditLog | None:
        return self.db.get(AuditLog, audit_log_id)

    def get_all(self) -> list[AuditLog]:
        statement = (
            select(AuditLog)
            .order_by(AuditLog.id.desc())
        )
        return list(self.db.scalars(statement).all())

    def get_by_user(self, user_id: int) -> list[AuditLog]:
        statement = (
            select(AuditLog)
            .where(AuditLog.user_id == user_id)
            .order_by(AuditLog.id.desc())
        )
        return list(self.db.scalars(statement).all())

    def get_by_entity(
        self,
        entity_type: str,
        entity_id: str,
    ) -> list[AuditLog]:
        statement = (
            select(AuditLog)
            .where(
                AuditLog.entity_type == entity_type,
                AuditLog.entity_id == entity_id,
            )
            .order_by(AuditLog.id.desc())
        )
        return list(self.db.scalars(statement).all())

    def create(self, audit_log: AuditLog) -> AuditLog:
        self.db.add(audit_log)
        self.db.flush()
        self.db.refresh(audit_log)
        return audit_log