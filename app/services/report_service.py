from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.inventory import Inventory
from app.models.order import Order
from app.models.product import Product
from app.models.return_order import ReturnOrder


class ReportService:
    def __init__(self, db: Session):
        self.db = db

    def dashboard(self) -> dict:
        total_products = self.db.scalar(
            select(func.count(Product.id))
        ) or 0

        total_orders = self.db.scalar(
            select(func.count(Order.id))
        ) or 0

        pending_orders = self.db.scalar(
            select(func.count(Order.id)).where(
                Order.status == "Pending"
            )
        ) or 0

        completed_orders = self.db.scalar(
            select(func.count(Order.id)).where(
                Order.status == "Delivered"
            )
        ) or 0

        low_stock_items = self.db.scalar(
            select(func.count(Inventory.id)).where(
                Inventory.quantity <= Inventory.reorder_level
            )
        ) or 0

        total_returns = self.db.scalar(
            select(func.count(ReturnOrder.id))
        ) or 0

        total_sales = self.db.scalar(
            select(func.coalesce(func.sum(Order.total_amount), 0))
            .where(Order.status == "Delivered")
        ) or 0

        return {
            "total_products": total_products,
            "total_orders": total_orders,
            "pending_orders": pending_orders,
            "completed_orders": completed_orders,
            "low_stock_items": low_stock_items,
            "total_returns": total_returns,
            "total_sales": total_sales,
        }

    def order_status_report(self) -> list[dict]:
        statement = (
            select(
                Order.status,
                func.count(Order.id).label("count"),
            )
            .group_by(Order.status)
            .order_by(Order.status)
        )

        rows = self.db.execute(statement).all()

        return [
            {
                "status": row.status,
                "count": row.count,
            }
            for row in rows
        ]

    def inventory_report(self) -> list[dict]:
        statement = (
            select(
                Inventory.product_id,
                Inventory.warehouse_id,
                Inventory.quantity,
                Inventory.reserved_quantity,
                Inventory.reorder_level,
            )
            .order_by(Inventory.product_id)
        )

        rows = self.db.execute(statement).all()

        return [
            {
                "product_id": row.product_id,
                "warehouse_id": row.warehouse_id,
                "quantity": row.quantity,
                "reserved_quantity": row.reserved_quantity,
                "available_quantity": (
                    row.quantity - row.reserved_quantity
                ),
                "reorder_level": row.reorder_level,
                "low_stock": (
                    row.quantity <= row.reorder_level
                ),
            }
            for row in rows
        ]

    def sales_report(self) -> dict:
        total_sales = self.db.scalar(
            select(func.coalesce(func.sum(Order.total_amount), 0))
            .where(Order.status == "Delivered")
        ) or 0

        delivered_orders = self.db.scalar(
            select(func.count(Order.id)).where(
                Order.status == "Delivered"
            )
        ) or 0

        average_order_value = (
            total_sales / delivered_orders
            if delivered_orders
            else 0
        )

        return {
            "total_sales": total_sales,
            "delivered_orders": delivered_orders,
            "average_order_value": average_order_value,
        }