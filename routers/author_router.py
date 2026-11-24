from fastapi import APIRouter, Depends, status
from models.models import Author, CreateAuthor, UpdateAuthor, Recipe
from sqlalchemy.orm import Session
from db.database import get_db
from services.author_service import AuthorService, get_author_service
from services.recipe_service import RecipeService, get_recipe_service

router = APIRouter(prefix="/author", tags=["Authors"])

@router.get("/")
def get_authors(db_session: Session = Depends(get_db),
                author_service: AuthorService = Depends(get_author_service)) -> list[Author]:
    return author_service.get_authors(db_session)

@router.get("/{id}")
def get_author(id: int, db_session: Session = Depends(get_db),
               author_service: AuthorService = Depends(get_author_service)) -> Author:
    return author_service.get_author(id, db_session)

@router.get("/{id}/recipes")
def get_author_recipes(id: int, db_session: Session = Depends(get_db),
                       author_service: AuthorService = Depends(get_author_service),
                       recipe_service: RecipeService = Depends(get_recipe_service)) -> list[Recipe]:
    return recipe_service.get_recipes_by_author(id, db_session, author_service)

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_author(create_author: CreateAuthor, db_session: Session = Depends(get_db),
                  author_service: AuthorService = Depends(get_author_service)) -> Author:
    return author_service.create_author(create_author.model_dump(), db_session)

@router.put("/{id}")
def update_author(id: int, update_author: UpdateAuthor, db_session: Session = Depends(get_db),
                  author_service: AuthorService = Depends(get_author_service)) -> Author:
    return author_service.update_author(id, update_author.model_dump(), db_session)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_author(id: int, db_session: Session = Depends(get_db),
                  author_service: AuthorService = Depends(get_author_service)):
    author_service.delete_author(id, db_session)
