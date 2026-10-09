from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.return_order import ReturnOrder


class ReturnRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, return_id: int) -> ReturnOrder | None:
        return self.db.get(ReturnOrder, return_id)

    def get_by_order(self, order_id: int) -> list[ReturnOrder]:
        statement = (
            select(ReturnOrder)
            .where(ReturnOrder.order_id == order_id)
            .order_by(ReturnOrder.id.desc())
        )
        return list(self.db.scalars(statement).all())

    def get_all(self) -> list[ReturnOrder]:
        statement = select(ReturnOrder).order_by(ReturnOrder.id.desc())
        return list(self.db.scalars(statement).all())

    def create(self, return_order: ReturnOrder) -> ReturnOrder:
        self.db.add(return_order)
        self.db.flush()
        self.db.refresh(return_order)
        return return_order

    def update(self, return_order: ReturnOrder) -> ReturnOrder:
        self.db.flush()
        self.db.refresh(return_order)
        return return_order