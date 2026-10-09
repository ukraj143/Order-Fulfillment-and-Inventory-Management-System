from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.return_order import ReturnOrder
from app.repositories.order_repository import OrderRepository
from app.repositories.return_repository import ReturnRepository
from app.schemas.return_order import ReturnCreate, ReturnStatusUpdate


class ReturnService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = ReturnRepository(db)
        self.order_repository = OrderRepository(db)

    def create(
        self,
        data: ReturnCreate,
    ) -> ReturnOrder:
        order = self.order_repository.get_by_id(data.order_id)

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found",
            )

        if order.status not in {"Fulfilled", "Delivered"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Return can only be requested for fulfilled orders",
            )

        if data.quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Return quantity must be greater than zero",
            )

        total_order_quantity = sum(
            item.quantity
            for item in order.items
        )

        if data.quantity > total_order_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Return quantity exceeds ordered quantity",
            )

        return_order = ReturnOrder(
            order_id=data.order_id,
            reason=data.reason,
            quantity=data.quantity,
            status="Requested",
        )

        return self.repository.create(return_order)

    def get(self, return_id: int) -> ReturnOrder:
        return_order = self.repository.get_by_id(return_id)

        if not return_order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Return request not found",
            )

        return return_order

    def get_all(self) -> list[ReturnOrder]:
        return self.repository.get_all()

    def get_by_order(self, order_id: int) -> list[ReturnOrder]:
        return self.repository.get_by_order(order_id)

    def update_status(
        self,
        return_id: int,
        data: ReturnStatusUpdate,
    ) -> ReturnOrder:
        return_order = self.get(return_id)

        allowed = {
            "Requested": {"Approved", "Rejected"},
            "Approved": {"Processed"},
            "Rejected": set(),
            "Processed": set(),
        }

        if data.status not in allowed.get(
            return_order.status,
            set(),
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Invalid return status transition: "
                    f"{return_order.status} -> {data.status}"
                ),
            )

        return_order.status = data.status

        if data.status == "Processed":
            return_order.processed_at = datetime.now(timezone.utc)

        return self.repository.update(return_order)