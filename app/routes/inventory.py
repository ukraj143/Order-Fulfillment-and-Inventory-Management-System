from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_roles
from app.schemas.inventory import (
    InventoryAdjustment,
    InventoryCreate,
    InventoryResponse,
    InventoryTransactionResponse,
    InventoryUpdate,
)
from app.services.inventory_service import InventoryService


router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"],
)


@router.post(
    "/",
    response_model=InventoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_inventory(
    data: InventoryCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles("Admin", "Warehouse Manager")
    ),
):
    return InventoryService(db).create(data)


@router.get(
    "/",
    response_model=list[InventoryResponse],
)
def list_inventory(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return InventoryService(db).list_all()


@router.get(
    "/low-stock",
    response_model=list[InventoryResponse],
)
def get_low_stock_inventory(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return InventoryService(db).get_low_stock()


@router.get(
    "/transactions",
    response_model=list[InventoryTransactionResponse],
)
def get_inventory_transactions(
    inventory_id: int | None = Query(default=None, ge=1),
    product_id: int | None = Query(default=None, ge=1),
    warehouse_id: int | None = Query(default=None, ge=1),
    transaction_type: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Admin",
            "Warehouse Manager",
        )
    ),
):
    return InventoryService(db).get_transactions(
        inventory_id=inventory_id,
        product_id=product_id,
        warehouse_id=warehouse_id,
        transaction_type=transaction_type,
    )


@router.get(
    "/product/{product_id}",
    response_model=list[InventoryResponse],
)
def get_inventory_by_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return InventoryService(db).get_by_product(product_id)


@router.get(
    "/{inventory_id}/transactions",
    response_model=list[InventoryTransactionResponse],
)
def get_inventory_transaction_history(
    inventory_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Admin",
            "Warehouse Manager",
        )
    ),
):
    return InventoryService(db).get_transactions(
        inventory_id=inventory_id
    )


@router.get(
    "/{inventory_id}",
    response_model=InventoryResponse,
)
def get_inventory(
    inventory_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return InventoryService(db).get(inventory_id)


@router.put(
    "/{inventory_id}",
    response_model=InventoryResponse,
)
def update_inventory(
    inventory_id: int,
    data: InventoryUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Admin",
            "Warehouse Manager",
        )
    ),
):
    return InventoryService(db).update(
        inventory_id,
        data,
    )


@router.post(
    "/adjust",
    response_model=InventoryResponse,
)
def adjust_inventory(
    data: InventoryAdjustment,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Admin",
            "Warehouse Manager",
        )
    ),
):
    return InventoryService(db).adjust_stock(
        inventory_id=data.inventory_id,
        adjustment=data,
        user_id=current_user.id,
    )


@router.post(
    "/transfer",
)
def transfer_inventory(
    product_id: int,
    source_warehouse_id: int,
    destination_warehouse_id: int,
    quantity: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Admin",
            "Warehouse Manager",
        )
    ),
):
    return InventoryService(db).transfer(
        product_id=product_id,
        source_warehouse_id=source_warehouse_id,
        destination_warehouse_id=destination_warehouse_id,
        quantity=quantity,
        user_id=current_user.id,
    )
