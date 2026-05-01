from app.utils.ai_moderation import ai_moderate
from app.utils.local_moderation import moderate_recipe


async def moderate_recipe_full(title: str, description: str) -> str:
    local_result = moderate_recipe(title, description)

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

    return "pending"