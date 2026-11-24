from exceptions import NotFound, DublicationError, ConflictError
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from db.models import Author, Recipe

def get_author_service():
    return AuthorService()

class AuthorService:
    def _get(self, id: int, db_session: Session) -> Author:
        author = db_session.get(Author, id)
        if author is None:
            raise NotFound(f"Author with id {id} not found")
        return author

    def get_authors(self, db_session: Session) -> list[Author]:
        return db_session.scalars(select(Author)).all()

    def get_author(self, id: int, db_session: Session) -> Author:
        return self._get(id, db_session)

    def create_author(self, data: dict, db_session: Session) -> Author:
        check_author = db_session.scalars(
            select(Author).where(
                func.lower(Author.email) == data["email"].lower())
                ).one_or_none()
        if check_author is not None:
            raise DublicationError(
                f"Author with email {data['email']} already exists")
        author = Author(name=data["name"], email=data["email"])
        db_session.add(author)
        db_session.commit()
        db_session.refresh(author)
        return author

    def update_author(self, id: int, data: dict, db_session: Session) -> Author:
        author = self._get(id, db_session)
        check_author = db_session.scalars(
            select(Author).where(Author.id != id).where(
                func.lower(Author.email) == data["email"].lower()
                )).one_or_none()
        if check_author is not None:
            raise DublicationError(
                f"Author with email {data['email']} already exists")
        author.name = data["name"]
        author.email = data["email"]
        db_session.commit()
        db_session.refresh(author)
        return author

    def delete_author(self, id: int, db_session: Session):
        author = self._get(id, db_session)
        has_recipes = db_session.scalars(
            select(Recipe).where(Recipe.author_id == id)
                ).first()
        if has_recipes is not None:
            raise ConflictError(
                f"Author with id {id} has recipes and can not be deleted")
        db_session.delete(author)
        db_session.commit()
