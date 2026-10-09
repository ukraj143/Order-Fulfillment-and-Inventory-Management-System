from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)
        self.role_repository = RoleRepository(db)

    def create_user(self, data: UserCreate) -> User:
        if self.user_repository.get_by_email(data.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email is already registered",
            )

        role = self.role_repository.get_by_id(data.role_id)

        if not role or not role.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or inactive role",
            )

        user = User(
            role_id=data.role_id,
            full_name=data.full_name,
            email=data.email,
            hashed_password=hash_password(data.password),
            phone=data.phone,
            is_active=True,
        )

        return self.user_repository.create(user)

    def get_user(self, user_id: int) -> User:
        user = self.user_repository.get_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        return user

    def get_users(self) -> list[User]:
        return self.user_repository.get_all()

    def update_user(self, user_id: int, data: UserUpdate) -> User:
        user = self.get_user(user_id)

        if data.role_id is not None:
            role = self.role_repository.get_by_id(data.role_id)

            if not role or not role.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid or inactive role",
                )

            user.role_id = data.role_id

        if data.full_name is not None:
            user.full_name = data.full_name

        if data.phone is not None:
            user.phone = data.phone

        if data.is_active is not None:
            user.is_active = data.is_active

        return self.user_repository.update(user)

    def deactivate_user(self, user_id: int) -> User:
        user = self.get_user(user_id)
        user.is_active = False
        return self.user_repository.update(user)

    def activate_user(self, user_id: int) -> User:
        user = self.get_user(user_id)
        user.is_active = True
        return self.user_repository.update(user)

    def delete_user(self, user_id: int) -> None:
        user = self.get_user(user_id)
        self.user_repository.delete(user)