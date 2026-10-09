from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.warehouse import Warehouse
from app.repositories.warehouse_repository import WarehouseRepository
from app.schemas.warehouse import WarehouseCreate, WarehouseUpdate


class WarehouseService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = WarehouseRepository(db)

    def create(self, data: WarehouseCreate) -> Warehouse:
        warehouse = Warehouse(**data.model_dump())

        self.db.add(warehouse)
        self.db.commit()
        self.db.refresh(warehouse)

        return warehouse

    def get(self, warehouse_id: int) -> Warehouse:
        warehouse = self.repository.get_by_id(warehouse_id)

        if not warehouse:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Warehouse not found",
            )

        return warehouse

    def list_all(self) -> list[Warehouse]:
        return self.repository.get_all()

    def update(
        self,
        warehouse_id: int,
        data: WarehouseUpdate,
    ) -> Warehouse:
        warehouse = self.get(warehouse_id)

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(warehouse, field, value)

        self.db.commit()
        self.db.refresh(warehouse)

        return warehouse

    def delete(self, warehouse_id: int) -> None:
        warehouse = self.get(warehouse_id)

        self.repository.delete(warehouse)

        self.db.commit()

    def activate(self, warehouse_id: int) -> Warehouse:
        warehouse = self.get(warehouse_id)

        if warehouse.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Warehouse is already active",
            )

        warehouse.is_active = True

        self.db.commit()
        self.db.refresh(warehouse)

        return warehouse

    def deactivate(self, warehouse_id: int) -> Warehouse:
        warehouse = self.get(warehouse_id)

        if not warehouse.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Warehouse is already inactive",
            )

        warehouse.is_active = False

        self.db.commit()
        self.db.refresh(warehouse)

        return warehouse
