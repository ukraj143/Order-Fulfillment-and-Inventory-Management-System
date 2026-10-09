from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.product import Product
from app.repositories.category_repository import CategoryRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate


class ProductService:
    def __init__(self, db: Session):
        self.repository = ProductRepository(db)
        self.category_repository = CategoryRepository(db)

    def create(self, data: ProductCreate) -> Product:
        category = self.category_repository.get_by_id(data.category_id)

        if not category or not category.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or inactive category",
            )

        if self.repository.get_by_sku(data.sku):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="SKU already exists",
            )

        product = Product(
            category_id=data.category_id,
            sku=data.sku,
            name=data.name,
            description=data.description,
            price=data.price,
            is_active=data.is_active,
        )

        return self.repository.create(product)

    def get(self, product_id: int) -> Product:
        product = self.repository.get_by_id(product_id)

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )

        return product

    def get_all(self) -> list[Product]:
        return self.repository.get_all()

    def update(
        self,
        product_id: int,
        data: ProductUpdate,
    ) -> Product:
        product = self.get(product_id)

        if data.category_id is not None:
            category = self.category_repository.get_by_id(
                data.category_id
            )

            if not category or not category.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid or inactive category",
                )

            product.category_id = data.category_id

        if data.sku is not None and data.sku != product.sku:
            existing = self.repository.get_by_sku(data.sku)

            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="SKU already exists",
                )

            product.sku = data.sku

        if data.name is not None:
            product.name = data.name

        if data.description is not None:
            product.description = data.description

        if data.price is not None:
            product.price = data.price

        if data.is_active is not None:
            product.is_active = data.is_active

        return self.repository.update(product)

    def activate(self, product_id: int) -> Product:
        product = self.get(product_id)

        if product.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product is already active",
            )

        product.is_active = True

        return self.repository.update(product)

    def deactivate(self, product_id: int) -> Product:
        product = self.get(product_id)

        if not product.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product is already inactive",
            )

        product.is_active = False

        return self.repository.update(product)

    def delete(self, product_id: int) -> None:
        product = self.get(product_id)
        self.repository.delete(product)
