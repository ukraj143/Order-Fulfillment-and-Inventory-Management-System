from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.fulfillment import Fulfillment
from app.models.order import Order


class OrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, order_id: int):
        return self.db.get(Order, order_id)

    def get_by_id_for_update(self, order_id: int):
        statement = (
            select(Order)
            .where(Order.id == order_id)
            .with_for_update()
        )

        return self.db.execute(statement).scalar_one_or_none()

    def get_all(self):
        statement = (
            select(Order)
            .order_by(Order.id.desc())
        )

        return list(
            self.db.execute(statement).scalars().all()
        )

    def get_by_customer(self, customer_id: int):
        statement = (
            select(Order)
            .where(Order.customer_id == customer_id)
            .order_by(Order.id.desc())
        )

        return list(
            self.db.execute(statement).scalars().all()
        )

    def search(
        self,
        status: str | None = None,
        customer_id: int | None = None,
        warehouse_id: int | None = None,
        min_total: Decimal | None = None,
        max_total: Decimal | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        page: int = 1,
        page_size: int = 20,
    ):
        statement = select(Order)

        if status:
            statement = statement.where(
                Order.status == status
            )

        if customer_id:
            statement = statement.where(
                Order.customer_id == customer_id
            )

        if warehouse_id:
            statement = statement.join(
                Fulfillment,
                Fulfillment.order_id == Order.id,
            ).where(
                Fulfillment.warehouse_id == warehouse_id
            )

        if min_total is not None:
            statement = statement.where(
                Order.total_amount >= min_total
            )

        if max_total is not None:
            statement = statement.where(
                Order.total_amount <= max_total
            )

        if start_date:
            statement = statement.where(
                Order.created_at >= start_date
            )

        if end_date:
            statement = statement.where(
                Order.created_at <= end_date
            )

        statement = (
            statement
            .order_by(Order.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        return list(
            self.db.execute(statement).scalars().all()
        )
