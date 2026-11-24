from typing import Literal
from pydantic import BaseModel, Field, ConfigDict, EmailStr

class Author(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr

class CreateAuthor(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1)
    email: EmailStr

class UpdateAuthor(CreateAuthor):
    pass

class Category(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str

class CreateCategory(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1)

class UpdateCategory(CreateCategory):
    pass

class Ingredient(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str

class CreateIngredient(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1)

class UpdateIngredient(CreateIngredient):
    pass

class Recipe(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    instructions: str
    prep_time_minutes: int
    servings: int
    difficulty: str
    author_id: int
    category_id: int | None

class CreateRecipe(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1)
    instructions: str = Field(min_length=1)
    prep_time_minutes: int = Field(gt=0)
    servings: int = Field(gt=0)
    difficulty: Literal["easy", "medium", "hard"]
    author_id: int
    category_id: int | None = None

class UpdateRecipe(CreateRecipe):
    pass

class RecipeIngredient(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ingredient: Ingredient
    quantity: float
    unit: str

class AddRecipeIngredient(BaseModel):
    ingredient_id: int
    quantity: float = Field(gt=0)
    unit: Literal["g", "ml", "pcs"]

class UpdateRecipeIngredient(BaseModel):
    quantity: float = Field(gt=0)
    unit: Literal["g", "ml", "pcs"]

class ScaledRecipe(BaseModel):
    id: int
    title: str
    instructions: str
    prep_time_minutes: int
    difficulty: str
    original_servings: int
    servings: int
    ingredients: list[RecipeIngredient]
