from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_roles
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user_service import UserService


router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("Admin")),
):
    return UserService(db).create_user(data)


@router.get(
    "/",
    response_model=list[UserResponse],
)
def list_users(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("Admin")),
):
    return UserService(db).get_users()


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_my_profile(
    current_user=Depends(get_current_user),
):
    return current_user


@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("Admin")),
):
    return UserService(db).get_user(user_id)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
)
def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("Admin")),
):
    return UserService(db).update_user(user_id, data)


@router.patch(
    "/{user_id}/activate",
    response_model=UserResponse,
)
def activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("Admin")),
):
    return UserService(db).activate_user(user_id)


@router.patch(
    "/{user_id}/deactivate",
    response_model=UserResponse,
)
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("Admin")),
):
    return UserService(db).deactivate_user(user_id)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("Admin")),
):
    UserService(db).delete_user(user_id)
    return None
