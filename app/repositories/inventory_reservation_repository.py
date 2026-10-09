from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.inventory_reservation import InventoryReservation


class InventoryReservationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(
        self,
        reservation_id: int,
    ) -> InventoryReservation | None:
        return self.db.get(InventoryReservation, reservation_id)

    def get_by_order(self, order_id: int) -> list[InventoryReservation]:
        statement = (
            select(InventoryReservation)
            .where(InventoryReservation.order_id == order_id)
            .order_by(InventoryReservation.id)
        )
        return list(self.db.scalars(statement).all())

    def get_active_by_product_and_warehouse(
        self,
        product_id: int,
        warehouse_id: int,
    ) -> list[InventoryReservation]:
        statement = (
            select(InventoryReservation)
            .where(
                InventoryReservation.product_id == product_id,
                InventoryReservation.warehouse_id == warehouse_id,
                InventoryReservation.status == "Reserved",
            )
            .order_by(InventoryReservation.id)
        )
        return list(self.db.scalars(statement).all())

    def create(
        self,
        reservation: InventoryReservation,
    ) -> InventoryReservation:
        self.db.add(reservation)
        self.db.flush()
        self.db.refresh(reservation)
        return reservation

    def update(
        self,
        reservation: InventoryReservation,
    ) -> InventoryReservation:
        self.db.flush()
        self.db.refresh(reservation)
        return reservation