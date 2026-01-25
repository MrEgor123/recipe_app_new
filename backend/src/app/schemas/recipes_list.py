from typing import List

from app.schemas.pagination import PageResponse
from app.schemas.recipes import RecipeRead


class RecipeListResponse(PageResponse):
    items: List[RecipeRead]