from exceptions import NotFound, DublicationError, ConflictError
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from db.models import Ingredient, RecipeIngredient

def get_ingredient_service():
    return IngredientService()

class IngredientService:
    def _get(self, id: int, db_session: Session) -> Ingredient:
        ingredient = db_session.get(Ingredient, id)
        if ingredient is None:
            raise NotFound(f"Ingredient with id {id} not found")
        return ingredient

    def get_ingredients(self, db_session: Session) -> list[Ingredient]:
        return db_session.scalars(select(Ingredient)).all()

    def get_ingredient(self, id: int, db_session: Session) -> Ingredient:
        return self._get(id, db_session)

    def create_ingredient(self, data: dict, db_session: Session) -> Ingredient:
        check_ingredient = db_session.scalars(
            select(Ingredient).where(
                func.lower(Ingredient.name) == data["name"].lower())
                ).one_or_none()
        if check_ingredient is not None:
            raise DublicationError(
                f"Ingredient with name {data['name']} already exists")
        ingredient = Ingredient(name=data["name"])
        db_session.add(ingredient)
        db_session.commit()
        db_session.refresh(ingredient)
        return ingredient

    def update_ingredient(self, id: int, data: dict, db_session: Session) -> Ingredient:
        ingredient = self._get(id, db_session)
        check_ingredient = db_session.scalars(
            select(Ingredient).where(Ingredient.id != id).where(
                func.lower(Ingredient.name) == data["name"].lower()
                )).one_or_none()
        if check_ingredient is not None:
            raise DublicationError(
                f"Ingredient with name {data['name']} already exists")
        ingredient.name = data["name"]
        db_session.commit()
        db_session.refresh(ingredient)
        return ingredient

    def delete_ingredient(self, id: int, db_session: Session):
        ingredient = self._get(id, db_session)
        used = db_session.scalars(
            select(RecipeIngredient).where(
                RecipeIngredient.ingredient_id == id)
                ).first()
        if used is not None:
            raise ConflictError(
                f"Ingredient with id {id} is used in a recipe and can not be deleted")
        db_session.delete(ingredient)
        db_session.commit()
