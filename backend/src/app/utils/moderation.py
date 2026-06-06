from app.utils.ai_moderation import ai_moderate, ai_moderate_comment
from app.utils.local_moderation import moderate_comment, moderate_recipe


async def moderate_recipe_full(title: str, description: str) -> str:
    local_result = moderate_recipe(title, description)

    if local_result == "approved":
        return "approved"

    if local_result == "rejected":
        return "rejected"

    text = f"""
Название рецепта:
{title}

Описание рецепта:
{description}
"""

    ai_result = await ai_moderate(text)

    if ai_result == "approved":
        return "approved"

    if ai_result == "rejected":
        return "rejected"

    return "approved"


async def moderate_comment_full(text: str) -> str:
    local_result = moderate_comment(text)

    if local_result == "rejected":
        return "rejected"

    ai_result = await ai_moderate_comment(text)

    if ai_result == "rejected":
        return "rejected"

    if ai_result == "approved":
        return "approved"

    return "approved"