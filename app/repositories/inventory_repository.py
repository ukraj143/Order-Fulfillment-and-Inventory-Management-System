from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.inventory import Inventory
from app.models.inventory_transaction import InventoryTransaction


class InventoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, inventory_id: int):
        return self.db.get(Inventory, inventory_id)

    def get_by_id_for_update(self, inventory_id: int):
        statement = (
            select(Inventory)
            .where(Inventory.id == inventory_id)
            .with_for_update()
        )

        return self.db.execute(statement).scalar_one_or_none()

    def get_all(self):
        statement = select(Inventory).order_by(Inventory.id)
        return list(self.db.execute(statement).scalars().all())

    def get_by_product(self, product_id: int):
        statement = (
            select(Inventory)
            .where(Inventory.product_id == product_id)
            .order_by(Inventory.id)
        )

        return list(self.db.execute(statement).scalars().all())

    def get_by_product_and_warehouse(
        self,
        product_id: int,
        warehouse_id: int,
    ):
        statement = select(Inventory).where(
            Inventory.product_id == product_id,
            Inventory.warehouse_id == warehouse_id,
        )

        return self.db.execute(statement).scalar_one_or_none()

    def get_by_product_and_warehouse_for_update(
        self,
        product_id: int,
        warehouse_id: int,
    ):
        statement = (
            select(Inventory)
            .where(
                Inventory.product_id == product_id,
                Inventory.warehouse_id == warehouse_id,
            )
            .with_for_update()
        )

        return self.db.execute(statement).scalar_one_or_none()

    def get_low_stock(self):
        statement = (
            select(Inventory)
            .where(
                Inventory.quantity <= Inventory.reorder_level
            )
            .order_by(Inventory.id)
        )

        return list(self.db.execute(statement).scalars().all())

    def get_transactions(
        self,
        inventory_id: int | None = None,
        product_id: int | None = None,
        warehouse_id: int | None = None,
        transaction_type: str | None = None,
    ):
        statement = select(InventoryTransaction)

        if inventory_id is not None:
            statement = statement.where(
                InventoryTransaction.inventory_id == inventory_id
            )

        if product_id is not None:
            statement = statement.where(
                InventoryTransaction.product_id == product_id
            )

        if warehouse_id is not None:
            statement = statement.where(
                InventoryTransaction.warehouse_id == warehouse_id
            )

        if transaction_type is not None:
            statement = statement.where(
                InventoryTransaction.transaction_type
                == transaction_type
            )

        statement = statement.order_by(
            InventoryTransaction.id.desc()
        )

        return list(
            self.db.execute(statement).scalars().all()
        )

    def delete(self, inventory: Inventory) -> None:
        self.db.delete(inventory)
