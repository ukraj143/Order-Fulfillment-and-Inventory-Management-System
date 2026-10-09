from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_roles
from app.schemas.warehouse import (
    WarehouseCreate,
    WarehouseResponse,
    WarehouseUpdate,
)
from app.services.warehouse_service import WarehouseService


router = APIRouter(
    prefix="/warehouses",
    tags=["Warehouses"],
)


@router.post(
    "/",
    response_model=WarehouseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_warehouse(
    data: WarehouseCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("Admin")),
):
    return WarehouseService(db).create(data)


@router.get(
    "/",
    response_model=list[WarehouseResponse],
)
def list_warehouses(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return WarehouseService(db).list_all()


@router.get(
    "/{warehouse_id}",
    response_model=WarehouseResponse,
)
def get_warehouse(
    warehouse_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return WarehouseService(db).get(warehouse_id)


@router.put(
    "/{warehouse_id}",
    response_model=WarehouseResponse,
)
def update_warehouse(
    warehouse_id: int,
    data: WarehouseUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("Admin")),
):
    return WarehouseService(db).update(
        warehouse_id,
        data,
    )


@router.patch(
    "/{warehouse_id}/activate",
    response_model=WarehouseResponse,
)
def activate_warehouse(
    warehouse_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("Admin")),
):
    return WarehouseService(db).activate(warehouse_id)


@router.patch(
    "/{warehouse_id}/deactivate",
    response_model=WarehouseResponse,
)
def deactivate_warehouse(
    warehouse_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("Admin")),
):
    return WarehouseService(db).deactivate(warehouse_id)


@router.delete("/{warehouse_id}")
def delete_warehouse(
    warehouse_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("Admin")),
):
    WarehouseService(db).delete(warehouse_id)

    return {
        "message": "Warehouse deleted successfully"
    }
