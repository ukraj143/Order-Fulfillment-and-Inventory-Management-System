from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        return self.db.scalar(statement)

    def get_all(self) -> list[User]:
        statement = select(User).order_by(User.id)
        return list(self.db.scalars(statement).all())

    def get_by_role(self, role_id: int) -> list[User]:
        statement = (
            select(User)
            .where(User.role_id == role_id)
            .order_by(User.id)
        )
        return list(self.db.scalars(statement).all())

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.flush()
        self.db.refresh(user)
        return user

    def update(self, user: User) -> User:
        self.db.flush()
        self.db.refresh(user)
        return user

    def delete(self, user: User) -> None:
        self.db.delete(user)
        self.db.flush()