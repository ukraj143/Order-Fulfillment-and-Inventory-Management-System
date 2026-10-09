from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Inventory(Base):
    __tablename__ = "inventory"

    __table_args__ = (
        CheckConstraint("quantity >= 0", name="ck_inventory_quantity"),
        CheckConstraint("reserved_quantity >= 0", name="ck_inventory_reserved"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        nullable=False,
    )

    warehouse_id: Mapped[int] = mapped_column(
        ForeignKey("warehouses.id"),
        nullable=False,
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    reserved_quantity: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    reorder_level: Mapped[int] = mapped_column(
        Integer,
        default=10,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    product = relationship(
        "Product",
        back_populates="inventory",
    )

    warehouse = relationship(
        "Warehouse",
        back_populates="inventory",
    )

    transactions = relationship(
        "InventoryTransaction",
        back_populates="inventory",
        cascade="all, delete-orphan",
    )
