from sqladmin import ModelView

from app.models.user import User
from app.models.recipe import Recipe
from app.models.tag import Tag
from app.models.ingredient import Ingredient


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.email, User.username, User.is_admin]
    column_searchable_list = [User.email, User.username]
    form_excluded_columns = ["password_hash"]


class RecipeAdmin(ModelView, model=Recipe):
    column_list = [Recipe.id, Recipe.title, Recipe.cooking_time_minutes]
    column_searchable_list = [Recipe.title]


class TagAdmin(ModelView, model=Tag):
    column_list = [Tag.id, Tag.name, Tag.slug]
    column_searchable_list = [Tag.name, Tag.slug]


class IngredientAdmin(ModelView, model=Ingredient):
    column_list = [Ingredient.id, Ingredient.name, Ingredient.unit]
    column_searchable_list = [Ingredient.name]