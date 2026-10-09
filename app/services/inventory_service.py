from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.inventory import Inventory
from app.models.inventory_transaction import InventoryTransaction
from app.models.product import Product
from app.repositories.inventory_repository import InventoryRepository
from app.schemas.inventory import (
    InventoryAdjustment,
    InventoryCreate,
    InventoryUpdate,
)


class InventoryService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = InventoryRepository(db)

    def create(self, data: InventoryCreate) -> Inventory:
        existing = self.repository.get_by_product_and_warehouse(
            product_id=data.product_id,
            warehouse_id=data.warehouse_id,
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Inventory already exists for this product and warehouse",
            )

        product = self.db.get(Product, data.product_id)

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )

        inventory = Inventory(
            product_id=data.product_id,
            warehouse_id=data.warehouse_id,
            quantity=data.quantity,
            reserved_quantity=data.reserved_quantity,
            reorder_level=data.reorder_level,
        )

        self.db.add(inventory)
        self.db.commit()
        self.db.refresh(inventory)

        return inventory

    def get(self, inventory_id: int) -> Inventory:
        inventory = self.repository.get_by_id(inventory_id)

        if not inventory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inventory not found",
            )

        return inventory

    def get_by_product(self, product_id: int) -> list[Inventory]:
        product = self.db.get(Product, product_id)

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )

        return self.repository.get_by_product(product_id)

    def list_all(self) -> list[Inventory]:
        return self.repository.get_all()

    def update(
        self,
        inventory_id: int,
        data: InventoryUpdate,
    ) -> Inventory:
        inventory = self.get(inventory_id)

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(inventory, field, value)

        self.db.commit()
        self.db.refresh(inventory)

        return inventory

    def adjust_stock(
        self,
        inventory_id: int,
        adjustment: InventoryAdjustment,
        user_id: int,
    ) -> Inventory:
        inventory = self.repository.get_by_id_for_update(
            inventory_id
        )

        if not inventory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inventory not found",
            )

        previous_quantity = inventory.quantity
        new_quantity = previous_quantity + adjustment.amount

        if new_quantity < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inventory quantity cannot be negative",
            )

        inventory.quantity = new_quantity

        transaction = InventoryTransaction(
            inventory_id=inventory.id,
            product_id=inventory.product_id,
            warehouse_id=inventory.warehouse_id,
            transaction_type="ADJUSTMENT",
            quantity=adjustment.amount,
            reference_type="INVENTORY",
            reference_id=inventory.id,
            reason=adjustment.reason,
            created_by=user_id,
        )

        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(inventory)

        return inventory

    def get_low_stock(self) -> list[Inventory]:
        return self.repository.get_low_stock()

    def get_transactions(
        self,
        inventory_id: int | None = None,
        product_id: int | None = None,
        warehouse_id: int | None = None,
        transaction_type: str | None = None,
    ) -> list[InventoryTransaction]:
        return self.repository.get_transactions(
            inventory_id=inventory_id,
            product_id=product_id,
            warehouse_id=warehouse_id,
            transaction_type=transaction_type,
        )

    def transfer(
        self,
        product_id: int,
        source_warehouse_id: int,
        destination_warehouse_id: int,
        quantity: int,
        user_id: int,
    ) -> dict:
        if quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Transfer quantity must be greater than zero",
            )

        if source_warehouse_id == destination_warehouse_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Source and destination warehouses must be different",
            )

        source = (
            self.repository
            .get_by_product_and_warehouse_for_update(
                product_id=product_id,
                warehouse_id=source_warehouse_id,
            )
        )

        if not source:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source inventory not found",
            )

        destination = (
            self.repository
            .get_by_product_and_warehouse_for_update(
                product_id=product_id,
                warehouse_id=destination_warehouse_id,
            )
        )

        if not destination:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Destination inventory not found",
            )

        available_quantity = (
            source.quantity - source.reserved_quantity
        )

        if available_quantity < quantity:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Insufficient available inventory for transfer",
            )

        source.quantity -= quantity
        destination.quantity += quantity

        source_transaction = InventoryTransaction(
            inventory_id=source.id,
            product_id=product_id,
            warehouse_id=source_warehouse_id,
            transaction_type="TRANSFER_OUT",
            quantity=quantity,
            reference_type="WAREHOUSE_TRANSFER",
            reference_id=destination_warehouse_id,
            reason=f"Transfer to warehouse {destination_warehouse_id}",
            created_by=user_id,
        )

        destination_transaction = InventoryTransaction(
            inventory_id=destination.id,
            product_id=product_id,
            warehouse_id=destination_warehouse_id,
            transaction_type="TRANSFER_IN",
            quantity=quantity,
            reference_type="WAREHOUSE_TRANSFER",
            reference_id=source_warehouse_id,
            reason=f"Transfer from warehouse {source_warehouse_id}",
            created_by=user_id,
        )

        self.db.add(source_transaction)
        self.db.add(destination_transaction)

        self.db.commit()

        return {
            "message": "Inventory transferred successfully",
            "product_id": product_id,
            "source_warehouse_id": source_warehouse_id,
            "destination_warehouse_id": destination_warehouse_id,
            "quantity": quantity,
        }
