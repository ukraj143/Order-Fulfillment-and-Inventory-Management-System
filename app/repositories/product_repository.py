from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import Product


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, product_id: int) -> Product | None:
        return self.db.get(Product, product_id)

    def get_by_sku(self, sku: str) -> Product | None:
        statement = select(Product).where(Product.sku == sku)
        return self.db.scalar(statement)

    def get_all(self) -> list[Product]:
        statement = select(Product).order_by(Product.id)
        return list(self.db.scalars(statement).all())

    def get_active(self) -> list[Product]:
        statement = (
            select(Product)
            .where(Product.is_active.is_(True))
            .order_by(Product.name)
        )
        return list(self.db.scalars(statement).all())

    def get_by_category(self, category_id: int) -> list[Product]:
        statement = (
            select(Product)
            .where(Product.category_id == category_id)
            .order_by(Product.name)
        )
        return list(self.db.scalars(statement).all())

    def create(self, product: Product) -> Product:
        self.db.add(product)
        self.db.flush()
        self.db.refresh(product)
        return product

    def update(self, product: Product) -> Product:
        self.db.flush()
        self.db.refresh(product)
        return product

    def delete(self, product: Product) -> None:
        self.db.delete(product)
        self.db.flush()