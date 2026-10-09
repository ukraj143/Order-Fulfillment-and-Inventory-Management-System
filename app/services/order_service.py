from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.fulfillment import Fulfillment
from app.models.inventory import Inventory
from app.models.inventory_reservation import InventoryReservation
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.warehouse import Warehouse
from app.repositories.order_repository import OrderRepository
from app.schemas.order import OrderCreate, OrderStatusUpdate


class OrderService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = OrderRepository(db)

    def get(self, order_id: int) -> Order:
        order = self.repository.get_by_id(order_id)

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found",
            )

        return order

    def get_all(self) -> list[Order]:
        return self.repository.get_all()

    def get_customer_orders(self, customer_id: int) -> list[Order]:
        return self.repository.get_by_customer(customer_id)

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
    ) -> list[Order]:
        return self.repository.search(
            status=status,
            customer_id=customer_id,
            warehouse_id=warehouse_id,
            min_total=min_total,
            max_total=max_total,
            start_date=start_date,
            end_date=end_date,
            page=page,
            page_size=page_size,
        )

    def create(
        self,
        data: OrderCreate,
        created_by: int,
    ) -> Order:
        customer_id = data.customer_id or created_by

        warehouse = self.db.get(Warehouse, data.warehouse_id)

        if not warehouse:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Warehouse not found",
            )

        if not warehouse.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Warehouse is inactive",
            )

        order = Order(
            order_number=f"ORD-{uuid4().hex[:10].upper()}",
            customer_id=customer_id,
            created_by=created_by,
            status="Pending",
            total_amount=Decimal("0.00"),
            shipping_address=data.shipping_address,
        )

        self.db.add(order)
        self.db.flush()

        total_amount = Decimal("0.00")

        for item_data in data.items:
            product = self.db.get(Product, item_data.product_id)

            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product {item_data.product_id} not found",
                )

            if not product.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Product {product.id} is inactive and cannot be ordered",
                )

            inventory_statement = (
                select(Inventory)
                .where(
                    Inventory.product_id == product.id,
                    Inventory.warehouse_id == data.warehouse_id,
                )
                .with_for_update()
            )

            inventory = (
                self.db.execute(inventory_statement)
                .scalar_one_or_none()
            )

            if not inventory:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=(
                        f"Inventory not found for product "
                        f"{product.id} in warehouse "
                        f"{data.warehouse_id}"
                    ),
                )

            available_quantity = (
                inventory.quantity - inventory.reserved_quantity
            )

            if available_quantity < item_data.quantity:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Insufficient inventory for product {product.sku}",
                )

            unit_price = Decimal(str(product.price))
            subtotal = unit_price * item_data.quantity

            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=item_data.quantity,
                unit_price=unit_price,
                subtotal=subtotal,
            )

            self.db.add(order_item)

            inventory.reserved_quantity += item_data.quantity

            reservation = InventoryReservation(
                product_id=product.id,
                warehouse_id=data.warehouse_id,
                order_id=order.id,
                quantity=item_data.quantity,
                status="Reserved",
            )

            self.db.add(reservation)

            total_amount += subtotal

        order.total_amount = total_amount

        fulfillment = Fulfillment(
            order_id=order.id,
            warehouse_id=data.warehouse_id,
            status="Pending",
        )

        self.db.add(fulfillment)

        self.db.commit()
        self.db.refresh(order)

        return order

    def update_status(
        self,
        order_id: int,
        data: OrderStatusUpdate,
    ) -> Order:
        order = self.get(order_id)

        current_status = order.status
        new_status = data.status

        allowed_transitions = {
            "Pending": {"Confirmed", "Cancelled"},
            "Confirmed": {"Processing", "Cancelled"},
            "Processing": {"Packed", "Cancelled"},
            "Packed": {"Shipped", "Cancelled"},
            "Shipped": {"Delivered"},
            "Delivered": set(),
            "Cancelled": set(),
            "Failed": set(),
            "Returned": set(),
        }

        allowed = allowed_transitions.get(current_status, set())

        if new_status not in allowed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Invalid order status transition: "
                    f"{current_status} -> {new_status}"
                ),
            )

        order.status = new_status

        if order.fulfillment:
            order.fulfillment.status = new_status

            if new_status == "Shipped":
                order.fulfillment.shipped_at = datetime.utcnow()

            if new_status == "Delivered":
                order.fulfillment.delivered_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(order)

        return order

    def cancel(self, order_id: int) -> Order:
        order = self.get(order_id)

        if order.status in {"Delivered", "Cancelled", "Returned"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Order cannot be cancelled from {order.status} status",
            )

        reservations = (
            self.db.execute(
                select(InventoryReservation).where(
                    InventoryReservation.order_id == order.id,
                    InventoryReservation.status == "Reserved",
                )
            )
            .scalars()
            .all()
        )

        for reservation in reservations:
            inventory_statement = (
                select(Inventory)
                .where(
                    Inventory.product_id == reservation.product_id,
                    Inventory.warehouse_id == reservation.warehouse_id,
                )
                .with_for_update()
            )

            inventory = (
                self.db.execute(inventory_statement)
                .scalar_one_or_none()
            )

            if inventory:
                inventory.reserved_quantity = max(
                    0,
                    inventory.reserved_quantity - reservation.quantity,
                )

            reservation.status = "Released"
            reservation.released_at = datetime.utcnow()

        order.status = "Cancelled"

        if order.fulfillment:
            order.fulfillment.status = "Cancelled"

        self.db.commit()
        self.db.refresh(order)

        return order
