from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.warehouse import Warehouse


class WarehouseRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, warehouse_id: int) -> Warehouse | None:
        return self.db.get(Warehouse, warehouse_id)

    def get_by_code(self, code: str) -> Warehouse | None:
        statement = select(Warehouse).where(Warehouse.code == code)
        return self.db.scalar(statement)

    def get_all(self) -> list[Warehouse]:
        statement = select(Warehouse).order_by(Warehouse.id)
        return list(self.db.scalars(statement).all())

    def get_active(self) -> list[Warehouse]:
        statement = (
            select(Warehouse)
            .where(Warehouse.is_active.is_(True))
            .order_by(Warehouse.name)
        )
        return list(self.db.scalars(statement).all())

    def create(self, warehouse: Warehouse) -> Warehouse:
        self.db.add(warehouse)
        self.db.flush()
        self.db.refresh(warehouse)
        return warehouse

    def update(self, warehouse: Warehouse) -> Warehouse:
        self.db.flush()
        self.db.refresh(warehouse)
        return warehouse

    def delete(self, warehouse: Warehouse) -> None:
        self.db.delete(warehouse)
        self.db.flush()