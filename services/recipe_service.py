from exceptions import NotFound, DublicationError
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from db.models import Recipe
from services.author_service import AuthorService
from services.category_service import CategoryService

def get_recipe_service():
    return RecipeService()

class RecipeService:
    def _get(self, id: int, db_session: Session) -> Recipe:
        recipe = db_session.get(Recipe, id)
        if recipe is None:
            raise NotFound(f"Recipe with id {id} not found")
        return recipe

    def get_recipes(self, db_session: Session) -> list[Recipe]:
        return db_session.scalars(select(Recipe)).all()

    def get_recipe(self, id: int, db_session: Session) -> Recipe:
        return self._get(id, db_session)

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
