from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.repositories.notification_repository import NotificationRepository
from app.repositories.user_repository import UserRepository
from app.schemas.notification import (
    NotificationCreate,
    NotificationUpdate,
)


class NotificationService:
    def __init__(self, db: Session):
        self.repository = NotificationRepository(db)
        self.user_repository = UserRepository(db)

    def create(self, data: NotificationCreate) -> Notification:
        user = self.user_repository.get_by_id(data.user_id)

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or inactive user",
            )

        notification = Notification(
            user_id=data.user_id,
            title=data.title,
            message=data.message,
            notification_type=data.notification_type,
            is_read=False,
        )

        return self.repository.create(notification)

    def get(self, notification_id: int) -> Notification:
        notification = self.repository.get_by_id(notification_id)

        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found",
            )

        return notification

    def get_user_notifications(
        self,
        user_id: int,
    ) -> list[Notification]:
        return self.repository.get_by_user(user_id)

    def get_unread(
        self,
        user_id: int,
    ) -> list[Notification]:
        return self.repository.get_unread_by_user(user_id)

    def mark_as_read(
        self,
        notification_id: int,
        data: NotificationUpdate,
    ) -> Notification:
        notification = self.get(notification_id)
        notification.is_read = data.is_read

        return self.repository.update(notification)