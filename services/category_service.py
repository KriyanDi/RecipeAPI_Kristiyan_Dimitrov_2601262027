from exceptions import NotFound, DublicationError
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from db.models import Category

def get_category_service():
    return CategoryService()

class CategoryService:
    def _get(self, id: int, db_session: Session) -> Category:
        category = db_session.get(Category, id)
        if category is None:
            raise NotFound(f"Category with id {id} not found")
        return category

    def get_categories(self, db_session: Session) -> list[Category]:
        return db_session.scalars(select(Category)).all()

    def get_category(self, id: int, db_session: Session) -> Category:
        return self._get(id, db_session)

    def create_category(self, data: dict, db_session: Session) -> Category:
        check_category = db_session.scalars(
            select(Category).where(
                func.lower(Category.name) == data["name"].lower())
                ).one_or_none()
        if check_category is not None:
            raise DublicationError(
                f"Category with name {data['name']} already exists")
        category = Category(name=data["name"])
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)
        return category

    def update_category(self, id: int, data: dict, db_session: Session) -> Category:
        category = self._get(id, db_session)
        check_category = db_session.scalars(
            select(Category).where(Category.id != id).where(
                func.lower(Category.name) == data["name"].lower()
                )).one_or_none()
        if check_category is not None:
            raise DublicationError(
                f"Category with name {data['name']} already exists")
        category.name = data["name"]
        db_session.commit()
        db_session.refresh(category)
        return category

    def delete_category(self, id: int, db_session: Session):
        category = self._get(id, db_session)
        db_session.delete(category)
        db_session.commit()
