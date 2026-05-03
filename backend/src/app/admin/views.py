from sqladmin import ModelView

from app.models.user import User
from app.models.user_report import UserReport
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
        User.is_blocked,
        User.blocked_until,
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
        User.is_blocked,
        User.blocked_until,
    ]
    form_columns = [
        User.email,
        User.username,
        User.first_name,
        User.last_name,
        User.avatar,
        User.status,
        User.bio,
        User.cover_image,
        User.is_admin,
        User.is_blocked,
        User.blocked_until,
        User.block_reason,
    ]

    column_labels = {
        User.id: "ID",
        User.email: "Email",
        User.username: "Логин",
        User.first_name: "Имя",
        User.last_name: "Фамилия",
        User.avatar: "Аватар",
        User.status: "Статус",
        User.bio: "Описание",
        User.cover_image: "Обложка",
        User.is_admin: "Администратор",
        User.is_blocked: "Заблокирован",
        User.blocked_until: "Заблокирован до",
        User.block_reason: "Причина блокировки",
    }


class UserReportAdmin(ModelView, model=UserReport):
    name = "Жалоба"
    name_plural = "Жалобы на пользователей"
    icon = "fa-solid fa-triangle-exclamation"

    page_size = 20
    page_size_options = [10, 20, 50, 100]
    column_default_sort = [(UserReport.id, True)]

    can_export = True
    can_create = False
    can_edit = True
    can_delete = True
    save_as = False

    column_list = [
        UserReport.id,
        UserReport.reported_user,
        UserReport.reporter,
        UserReport.reason,
        UserReport.status,
        UserReport.created_at,
    ]

    column_searchable_list = [
        UserReport.reason,
        UserReport.comment,
        UserReport.status,
    ]

    column_sortable_list = [
        UserReport.id,
        UserReport.reason,
        UserReport.status,
        UserReport.created_at,
    ]

    form_columns = [
        UserReport.reporter,
        UserReport.reported_user,
        UserReport.reason,
        UserReport.comment,
        UserReport.status,
    ]

    column_labels = {
        UserReport.id: "ID",
        UserReport.reporter: "Кто пожаловался",
        UserReport.reported_user: "На кого жалоба",
        UserReport.reason: "Причина",
        UserReport.comment: "Комментарий",
        UserReport.status: "Статус",
        UserReport.created_at: "Дата создания",
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
        Recipe.is_published,
        Recipe.moderation_status,
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
        Recipe.is_published,
        Recipe.moderation_status,
    ]
    form_columns = [
        Recipe.author,
        Recipe.title,
        Recipe.description,
        Recipe.cooking_time_minutes,
        Recipe.image,
        Recipe.is_published,
        Recipe.moderation_status,
    ]

    column_labels = {
        Recipe.id: "ID",
        Recipe.title: "Название",
        Recipe.author: "Автор",
        Recipe.description: "Описание",
        Recipe.cooking_time_minutes: "Время приготовления",
        Recipe.image: "Изображение",
        Recipe.is_published: "Опубликован",
        Recipe.moderation_status: "Статус модерации",
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