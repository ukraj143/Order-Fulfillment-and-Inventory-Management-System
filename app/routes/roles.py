from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_roles
from app.schemas.role import RoleCreate, RoleResponse, RoleUpdate
from app.services.user_service import UserService


router = APIRouter(prefix="/roles", tags=["Roles"])


@router.post(
    "/",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_role(
    data: RoleCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("Admin")),
):
    service = UserService(db)
    return service.create_role(data)


@router.get(
    "/",
    response_model=list[RoleResponse],
)
def list_roles(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("Admin")),
):
    return UserService(db).list_roles()


@router.get(
    "/{role_id}",
    response_model=RoleResponse,
)
def get_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("Admin")),
):
    return UserService(db).get_role(role_id)


@router.put(
    "/{role_id}",
    response_model=RoleResponse,
)
def update_role(
    role_id: int,
    data: RoleUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("Admin")),
):
    return UserService(db).update_role(role_id, data)


@router.delete("/{role_id}")
def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("Admin")),
):
    UserService(db).delete_role(role_id)

    return {
        "message": "Role deleted successfully"
    }