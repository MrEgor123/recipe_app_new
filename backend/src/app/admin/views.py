from sqladmin import ModelView

from app.models.user import User
from app.models.recipe import Recipe
from app.models.tag import Tag
from app.models.ingredient import Ingredient


class UserAdmin(ModelView, model=User):
    name = "Пользователь"
    name_plural = "Пользователи"
    icon = "fa-solid fa-users"

    page_size = 20
    page_size_options = [10, 20, 50, 100]
    column_default_sort = [(User.id, True)]

    can_export = True
    can_create = True
    can_edit = True
    can_delete = True
    save_as = False

    column_list = [
        User.id,
        User.email,
        User.username,
        User.first_name,
        User.last_name,
        User.is_admin,
    ]
    column_searchable_list = [
        User.email,
        User.username,
        User.first_name,
        User.last_name,
    ]
    column_sortable_list = [
        User.id,
        User.email,
        User.username,
        User.first_name,
        User.last_name,
        User.is_admin,
    ]
    form_columns = [
        User.email,
        User.username,
        User.first_name,
        User.last_name,
        User.avatar,
        User.is_admin,
    ]

    column_labels = {
        User.id: "ID",
        User.email: "Email",
        User.username: "Логин",
        User.first_name: "Имя",
        User.last_name: "Фамилия",
        User.avatar: "Аватар",
        User.is_admin: "Администратор",
    }


class RecipeAdmin(ModelView, model=Recipe):
    name = "Рецепт"
    name_plural = "Рецепты"
    icon = "fa-solid fa-utensils"

    page_size = 20
    page_size_options = [10, 20, 50, 100]
    column_default_sort = [(Recipe.id, True)]

    can_export = True
    can_create = True
    can_edit = True
    can_delete = True
    save_as = False

    column_list = [
        Recipe.id,
        Recipe.title,
        Recipe.author,
        Recipe.cooking_time_minutes,
    ]
    column_searchable_list = [
        Recipe.title,
        Recipe.description,
    ]
    column_sortable_list = [
        Recipe.id,
        Recipe.title,
        Recipe.author_id,
        Recipe.cooking_time_minutes,
    ]
    form_columns = [
        Recipe.author,
        Recipe.title,
        Recipe.description,
        Recipe.cooking_time_minutes,
        Recipe.image,
    ]

    column_labels = {
        Recipe.id: "ID",
        Recipe.title: "Название",
        Recipe.author: "Автор",
        Recipe.description: "Описание",
        Recipe.cooking_time_minutes: "Время приготовления",
        Recipe.image: "Изображение",
    }


class TagAdmin(ModelView, model=Tag):
    name = "Тег"
    name_plural = "Теги"
    icon = "fa-solid fa-tags"

    page_size = 20
    page_size_options = [10, 20, 50, 100]
    column_default_sort = [(Tag.id, True)]

    can_export = True
    can_create = True
    can_edit = True
    can_delete = True
    save_as = False

    column_list = [
        Tag.id,
        Tag.name,
        Tag.slug,
    ]
    column_searchable_list = [
        Tag.name,
        Tag.slug,
    ]
    column_sortable_list = [
        Tag.id,
        Tag.name,
        Tag.slug,
    ]
    form_columns = [
        Tag.name,
        Tag.slug,
    ]

    column_labels = {
        Tag.id: "ID",
        Tag.name: "Название",
        Tag.slug: "Slug",
    }


class IngredientAdmin(ModelView, model=Ingredient):
    name = "Ингредиент"
    name_plural = "Ингредиенты"
    icon = "fa-solid fa-carrot"

    page_size = 20
    page_size_options = [10, 20, 50, 100]
    column_default_sort = [(Ingredient.id, True)]

    can_export = True
    can_create = True
    can_edit = True
    can_delete = True
    save_as = False

    column_list = [
        Ingredient.id,
        Ingredient.name,
        Ingredient.unit,
    ]
    column_searchable_list = [
        Ingredient.name,
        Ingredient.unit,
    ]
    column_sortable_list = [
        Ingredient.id,
        Ingredient.name,
        Ingredient.unit,
    ]
    form_columns = [
        Ingredient.name,
        Ingredient.unit,
    ]

    column_labels = {
        Ingredient.id: "ID",
        Ingredient.name: "Название",
        Ingredient.unit: "Единица измерения",
    }