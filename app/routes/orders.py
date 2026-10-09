from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.order import OrderCreate, OrderResponse, OrderStatusUpdate
from app.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post(
    "/",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_order(
    data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = OrderService(db)

    return service.create(
        data=data,
        created_by=current_user.id,
    )


@router.get(
    "/",
    response_model=list[OrderResponse],
)
def list_orders(
    status_filter: str | None = Query(default=None, alias="status"),
    customer_id: int | None = Query(default=None, ge=1),
    warehouse_id: int | None = Query(default=None, ge=1),
    min_total: Decimal | None = Query(default=None, ge=0),
    max_total: Decimal | None = Query(default=None, ge=0),
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = OrderService(db)

    if current_user.role.name == "Customer":
        return service.search(
            customer_id=current_user.id,
            page=page,
            page_size=page_size,
        )

    return service.search(
        status=status_filter,
        customer_id=customer_id,
        warehouse_id=warehouse_id,
        min_total=min_total,
        max_total=max_total,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = OrderService(db)
    order = service.get(order_id)

    if (
        current_user.role.name == "Customer"
        and order.customer_id != current_user.id
    ):
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own orders",
        )

    return order


@router.put(
    "/{order_id}/status",
    response_model=OrderResponse,
)
def update_order_status(
    order_id: int,
    data: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = OrderService(db)

    return service.update_status(
        order_id=order_id,
        data=data,
    )


@router.post(
    "/{order_id}/cancel",
    response_model=OrderResponse,
)
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = OrderService(db)
    order = service.get(order_id)

    if (
        current_user.role.name == "Customer"
        and order.customer_id != current_user.id
    ):
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only cancel your own orders",
        )

    return service.cancel(order_id)
