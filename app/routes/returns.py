from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_roles
from app.schemas.return_order import (
    ReturnCreate,
    ReturnResponse,
    ReturnStatusUpdate,
)
from app.services.return_service import ReturnService


router = APIRouter(
    prefix="/returns",
    tags=["Returns"],
)


@router.post(
    "/",
    response_model=ReturnResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_return(
    data: ReturnCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles("Admin", "Customer")
    ),
):
    service = ReturnService(db)

    if current_user.role.name == "Customer":
        order = service.order_repository.get_by_id(
            data.order_id
        )

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found",
            )

        if order.customer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to create a return for this order",
            )

    return service.create(
        data=data,
        created_by=current_user.id,
    )


@router.get(
    "/",
    response_model=list[ReturnResponse],
)
def list_returns(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ReturnService(db)

    if current_user.role.name == "Customer":
        returns = []

        orders = service.order_repository.get_by_customer(
            current_user.id
        )

        for order in orders:
            returns.extend(
                service.get_by_order(order.id)
            )

        return returns

    return service.get_all()


@router.get(
    "/{return_id}",
    response_model=ReturnResponse,
)
def get_return(
    return_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ReturnService(db)
    return_order = service.get(return_id)

    if current_user.role.name == "Customer":
        order = service.order_repository.get_by_id(
            return_order.order_id
        )

        if not order or order.customer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to access this return",
            )

    return return_order


@router.get(
    "/order/{order_id}",
    response_model=list[ReturnResponse],
)
def get_order_returns(
    order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ReturnService(db)

    if current_user.role.name == "Customer":
        order = service.order_repository.get_by_id(order_id)

        if not order or order.customer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to access this order",
            )

    return service.get_by_order(order_id)


@router.put(
    "/{return_id}/status",
    response_model=ReturnResponse,
)
def update_return_status(
    return_id: int,
    data: ReturnStatusUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Admin",
            "Warehouse Manager",
            "Fulfillment Agent",
        )
    ),
):
    return ReturnService(db).update_status(
        return_id=return_id,
        data=data,
    )