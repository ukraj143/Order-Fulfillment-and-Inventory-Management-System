from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.notification import Notification


class NotificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, notification_id: int) -> Notification | None:
        return self.db.get(Notification, notification_id)

    def get_by_user(self, user_id: int) -> list[Notification]:
        statement = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.id.desc())
        )
        return list(self.db.scalars(statement).all())

    def get_unread_by_user(self, user_id: int) -> list[Notification]:
        statement = (
            select(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.is_read.is_(False),
            )
            .order_by(Notification.id.desc())
        )
        return list(self.db.scalars(statement).all())

    def create(self, notification: Notification) -> Notification:
        self.db.add(notification)
        self.db.flush()
        self.db.refresh(notification)
        return notification

    def update(self, notification: Notification) -> Notification:
        self.db.flush()
        self.db.refresh(notification)
        return notification