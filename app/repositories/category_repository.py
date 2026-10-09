from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Category


class CategoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, category_id: int) -> Category | None:
        return self.db.get(Category, category_id)

    def get_by_name(self, name: str) -> Category | None:
        statement = select(Category).where(Category.name == name)
        return self.db.scalar(statement)

    def get_all(self) -> list[Category]:
        statement = select(Category).order_by(Category.id)
        return list(self.db.scalars(statement).all())

    def get_active(self) -> list[Category]:
        statement = (
            select(Category)
            .where(Category.is_active.is_(True))
            .order_by(Category.name)
        )
        return list(self.db.scalars(statement).all())

    def create(self, category: Category) -> Category:
        self.db.add(category)
        self.db.flush()
        self.db.refresh(category)
        return category

    def update(self, category: Category) -> Category:
        self.db.flush()
        self.db.refresh(category)
        return category

    def delete(self, category: Category) -> None:
        self.db.delete(category)
        self.db.flush()