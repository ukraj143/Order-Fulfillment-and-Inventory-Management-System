from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.category import Category
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:
    def __init__(self, db: Session):
        self.repository = CategoryRepository(db)

    def create(self, data: CategoryCreate) -> Category:
        if self.repository.get_by_name(data.name):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Category already exists",
            )

        category = Category(
            name=data.name,
            description=data.description,
            is_active=data.is_active,
        )

        return self.repository.create(category)

    def get(self, category_id: int) -> Category:
        category = self.repository.get_by_id(category_id)

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )

        return category

    def get_all(self) -> list[Category]:
        return self.repository.get_all()

    def update(
        self,
        category_id: int,
        data: CategoryUpdate,
    ) -> Category:
        category = self.get(category_id)

        if data.name is not None and data.name != category.name:
            existing = self.repository.get_by_name(data.name)

            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Category already exists",
                )

            category.name = data.name

        if data.description is not None:
            category.description = data.description

        if data.is_active is not None:
            category.is_active = data.is_active

        return self.repository.update(category)

    def delete(self, category_id: int) -> None:
        category = self.get(category_id)
        self.repository.delete(category)