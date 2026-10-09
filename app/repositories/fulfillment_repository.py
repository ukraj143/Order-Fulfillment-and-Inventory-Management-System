from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.fulfillment import Fulfillment


class FulfillmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, fulfillment_id: int) -> Fulfillment | None:
        return self.db.get(Fulfillment, fulfillment_id)

    def get_by_order(self, order_id: int) -> Fulfillment | None:
        statement = select(Fulfillment).where(
            Fulfillment.order_id == order_id
        )
        return self.db.scalar(statement)

    def get_all(self) -> list[Fulfillment]:
        statement = select(Fulfillment).order_by(Fulfillment.id.desc())
        return list(self.db.scalars(statement).all())

    def get_by_warehouse(self, warehouse_id: int) -> list[Fulfillment]:
        statement = (
            select(Fulfillment)
            .where(Fulfillment.warehouse_id == warehouse_id)
            .order_by(Fulfillment.id.desc())
        )
        return list(self.db.scalars(statement).all())

    def create(self, fulfillment: Fulfillment) -> Fulfillment:
        self.db.add(fulfillment)
        self.db.flush()
        self.db.refresh(fulfillment)
        return fulfillment

    def update(self, fulfillment: Fulfillment) -> Fulfillment:
        self.db.flush()
        self.db.refresh(fulfillment)
        return fulfillment