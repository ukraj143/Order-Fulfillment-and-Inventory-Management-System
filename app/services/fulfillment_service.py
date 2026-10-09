from datetime import datetime, timezone
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.fulfillment import Fulfillment
from app.models.user import User
from app.repositories.fulfillment_repository import FulfillmentRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.warehouse_repository import WarehouseRepository
from app.schemas.fulfillment import FulfillmentCreate, FulfillmentUpdate


class FulfillmentService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = FulfillmentRepository(db)
        self.order_repository = OrderRepository(db)
        self.warehouse_repository = WarehouseRepository(db)

    def create(self, data: FulfillmentCreate) -> Fulfillment:
        order = self.order_repository.get_by_id(data.order_id)

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found",
            )

        if order.status not in {"Pending", "Confirmed", "Processing"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order is not ready for fulfillment",
            )

        existing = self.repository.get_by_order(data.order_id)

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Fulfillment already exists for this order",
            )

        warehouse = self.warehouse_repository.get_by_id(data.warehouse_id)

        if not warehouse or not warehouse.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or inactive warehouse",
            )

        fulfillment = Fulfillment(
            order_id=data.order_id,
            warehouse_id=data.warehouse_id,
            status="Pending",
        )

        order.status = "Processing"

        self.db.add(fulfillment)
        self.db.commit()
        self.db.refresh(fulfillment)

        return fulfillment

    def get(self, fulfillment_id: int) -> Fulfillment:
        fulfillment = self.repository.get_by_id(fulfillment_id)

        if not fulfillment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fulfillment not found",
            )

        return fulfillment

    def get_all(self) -> list[Fulfillment]:
        return self.repository.get_all()

    def assign_agent(
        self,
        fulfillment_id: int,
        agent_id: int,
    ) -> Fulfillment:
        fulfillment = self.get(fulfillment_id)

        agent = self.db.get(User, agent_id)

        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fulfillment agent not found",
            )

        if not agent.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive fulfillment agent cannot be assigned",
            )

        if not agent.role or agent.role.name != "Fulfillment Agent":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not a Fulfillment Agent",
            )

        fulfillment.assigned_agent_id = agent_id

        self.db.commit()
        self.db.refresh(fulfillment)

        return fulfillment

    def reassign_agent(
        self,
        fulfillment_id: int,
        agent_id: int,
    ) -> Fulfillment:
        fulfillment = self.get(fulfillment_id)

        if fulfillment.status in {"Shipped", "Delivered", "Cancelled"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Fulfillment cannot be reassigned in its current status",
            )

        return self.assign_agent(
            fulfillment_id=fulfillment_id,
            agent_id=agent_id,
        )

    def update(self, fulfillment_id: int, data: FulfillmentUpdate) -> Fulfillment:
        fulfillment = self.get(fulfillment_id)

        if data.assigned_agent_id is not None:
            self.assign_agent(
                fulfillment_id=fulfillment_id,
                agent_id=data.assigned_agent_id,
            )
            fulfillment = self.get(fulfillment_id)

        if data.status is not None:
            self._change_status(
                fulfillment=fulfillment,
                new_status=data.status,
            )

        if data.tracking_number is not None:
            fulfillment.tracking_number = data.tracking_number

        self.db.commit()
        self.db.refresh(fulfillment)

        return fulfillment

    def _change_status(
        self,
        fulfillment: Fulfillment,
        new_status: str,
    ) -> None:
        allowed_transitions = {
            "Pending": {"Accepted", "Cancelled"},
            "Accepted": {"Processing", "Cancelled"},
            "Processing": {"Packed", "Cancelled"},
            "Packed": {"Shipped", "Cancelled"},
            "Shipped": {"Delivered"},
            "Delivered": set(),
            "Cancelled": set(),
        }

        current_status = fulfillment.status

        if new_status not in allowed_transitions.get(current_status, set()):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Invalid fulfillment transition: "
                    f"{current_status} -> {new_status}"
                ),
            )

        if new_status in {"Accepted", "Processing", "Packed"}:
            if not fulfillment.assigned_agent_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A Fulfillment Agent must be assigned before processing",
                )

        fulfillment.status = new_status

        order = self.order_repository.get_by_id(fulfillment.order_id)

        if order:
            order_status_map = {
                "Accepted": "Confirmed",
                "Processing": "Processing",
                "Packed": "Packed",
                "Shipped": "Shipped",
                "Delivered": "Delivered",
                "Cancelled": "Cancelled",
            }

            mapped_status = order_status_map.get(new_status)

            if mapped_status:
                order.status = mapped_status

        if new_status == "Shipped":
            fulfillment.shipped_at = datetime.now(timezone.utc)

            if not fulfillment.tracking_number:
                fulfillment.tracking_number = (
                    f"TRK-{uuid4().hex[:12].upper()}"
                )

        if new_status == "Delivered":
            fulfillment.delivered_at = datetime.now(timezone.utc)

    def accept(self, fulfillment_id: int) -> Fulfillment:
        return self.update(
            fulfillment_id,
            FulfillmentUpdate(status="Accepted"),
        )

    def process(self, fulfillment_id: int) -> Fulfillment:
        return self.update(
            fulfillment_id,
            FulfillmentUpdate(status="Processing"),
        )

    def pack(self, fulfillment_id: int) -> Fulfillment:
        return self.update(
            fulfillment_id,
            FulfillmentUpdate(status="Packed"),
        )

    def ship(self, fulfillment_id: int) -> Fulfillment:
        return self.update(
            fulfillment_id,
            FulfillmentUpdate(status="Shipped"),
        )

    def deliver(self, fulfillment_id: int) -> Fulfillment:
        return self.update(
            fulfillment_id,
            FulfillmentUpdate(status="Delivered"),
        )
