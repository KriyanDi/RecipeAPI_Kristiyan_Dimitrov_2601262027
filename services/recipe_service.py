from exceptions import NotFound, DublicationError
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from db.models import Recipe, RecipeIngredient
from services.author_service import AuthorService
from services.category_service import CategoryService
from services.ingredient_service import IngredientService

def get_recipe_service():
    return RecipeService()

class RecipeService:
    def _get(self, id: int, db_session: Session) -> Recipe:
        recipe = db_session.get(Recipe, id)
        if recipe is None:
            raise NotFound(f"Recipe with id {id} not found")
        return recipe

    def get_recipes(self, db_session: Session, title: str | None = None,
                    category_id: int | None = None,
                    max_time: int | None = None) -> list[Recipe]:
        stmt = select(Recipe)
        if title is not None:
            stmt = stmt.where(
                func.lower(Recipe.title).like(f"%{title.strip().lower()}%"))
        if category_id is not None:
            stmt = stmt.where(Recipe.category_id == category_id)
        if max_time is not None:
            stmt = stmt.where(Recipe.prep_time_minutes <= max_time)
        return db_session.scalars(stmt).all()

    def get_recipe(self, id: int, db_session: Session) -> Recipe:
        return self._get(id, db_session)

    def get_recipes_by_author(self, author_id: int, db_session: Session,
                              author_service: AuthorService) -> list[Recipe]:
        author = author_service.get_author(author_id, db_session)
        return db_session.scalars(
            select(Recipe).where(Recipe.author_id == author.id)).all()

    def create_recipe(self, data: dict, db_session: Session,
                      author_service: AuthorService,
                      category_service: CategoryService) -> Recipe:
        author = author_service.get_author(data["author_id"], db_session)
        category = None
        if data["category_id"] is not None:
            category = category_service.get_category(data["category_id"], db_session)

        check_recipe = db_session.scalars(
            select(Recipe).where(Recipe.author_id == author.id).where(
                func.lower(Recipe.title) == data["title"].lower())
                ).one_or_none()
        if check_recipe is not None:
            raise DublicationError(
                f"Author with id {author.id} already has a recipe with title {data['title']}")

        recipe = Recipe(title=data["title"], instructions=data["instructions"],
                        prep_time_minutes=data["prep_time_minutes"],
                        servings=data["servings"], author=author, category=category)
        db_session.add(recipe)
        db_session.commit()
        db_session.refresh(recipe)
        return recipe

    def update_recipe(self, id: int, data: dict, db_session: Session,
                      author_service: AuthorService,
                      category_service: CategoryService) -> Recipe:
        recipe = self._get(id, db_session)
        author = author_service.get_author(data["author_id"], db_session)
        category = None
        if data["category_id"] is not None:
            category = category_service.get_category(data["category_id"], db_session)

        check_recipe = db_session.scalars(
            select(Recipe).where(Recipe.id != id).where(
                Recipe.author_id == author.id).where(
                func.lower(Recipe.title) == data["title"].lower())
                ).one_or_none()
        if check_recipe is not None:
            raise DublicationError(
                f"Author with id {author.id} already has a recipe with title {data['title']}")

        recipe.title = data["title"]
        recipe.instructions = data["instructions"]
        recipe.prep_time_minutes = data["prep_time_minutes"]
        recipe.servings = data["servings"]
        recipe.author = author
        recipe.category = category
        db_session.commit()
        db_session.refresh(recipe)
        return recipe

    def delete_recipe(self, id: int, db_session: Session):
        recipe = self._get(id, db_session)
        db_session.delete(recipe)
        db_session.commit()

    def _get_link(self, recipe_id: int, ingredient_id: int,
                  db_session: Session) -> RecipeIngredient:
        recipe = self._get(recipe_id, db_session)
        link = db_session.scalars(
            select(RecipeIngredient).where(
                RecipeIngredient.recipe_id == recipe.id).where(
                RecipeIngredient.ingredient_id == ingredient_id)
                ).one_or_none()
        if link is None:
            raise NotFound(
                f"Ingredient with id {ingredient_id} is not in recipe with id {recipe_id}")
        return link

    def get_recipe_ingredients(self, recipe_id: int,
                               db_session: Session) -> list[RecipeIngredient]:
        recipe = self._get(recipe_id, db_session)
        return db_session.scalars(
            select(RecipeIngredient).where(
                RecipeIngredient.recipe_id == recipe.id)).all()

    def add_ingredient(self, recipe_id: int, data: dict, db_session: Session,
                       ingredient_service: IngredientService) -> RecipeIngredient:
        recipe = self._get(recipe_id, db_session)
        ingredient = ingredient_service.get_ingredient(data["ingredient_id"], db_session)
        check_link = db_session.scalars(
            select(RecipeIngredient).where(
                RecipeIngredient.recipe_id == recipe.id).where(
                RecipeIngredient.ingredient_id == ingredient.id)
                ).one_or_none()
        if check_link is not None:
            raise DublicationError(
                f"Ingredient with id {ingredient.id} is already in recipe with id {recipe_id}")
        link = RecipeIngredient(recipe=recipe, ingredient=ingredient,
                                quantity=data["quantity"], unit=data["unit"])
        db_session.add(link)
        db_session.commit()
        db_session.refresh(link)
        return link

    def update_ingredient(self, recipe_id: int, ingredient_id: int, data: dict,
                          db_session: Session) -> RecipeIngredient:
        link = self._get_link(recipe_id, ingredient_id, db_session)
        link.quantity = data["quantity"]
        link.unit = data["unit"]
        db_session.commit()
        db_session.refresh(link)
        return link

    def remove_ingredient(self, recipe_id: int, ingredient_id: int,
                          db_session: Session):
        link = self._get_link(recipe_id, ingredient_id, db_session)
        db_session.delete(link)
        db_session.commit()

    def get_scaled_recipe(self, id: int, servings: int, db_session: Session) -> dict:
        recipe = self._get(id, db_session)
        links = db_session.scalars(
            select(RecipeIngredient).where(
                RecipeIngredient.recipe_id == recipe.id)).all()
        ingredients = []
        for link in links:
            ingredients.append({
                "ingredient": {"id": link.ingredient.id, "name": link.ingredient.name},
                "quantity": round(link.quantity * servings / recipe.servings, 2),
                "unit": link.unit})
        return {"id": recipe.id, "title": recipe.title,
                "instructions": recipe.instructions,
                "prep_time_minutes": recipe.prep_time_minutes,
                "original_servings": recipe.servings, "servings": servings,
                "ingredients": ingredients}
