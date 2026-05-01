import httpx

from app.core.config import settings


async def ai_moderate(text: str) -> str:
    if not settings.gemini_api_key:
        print("NO GEMINI API KEY")
        return "pending"

    prompt = f"""
Ты система модерации пользовательских рецептов на кулинарном сайте.

Твоя задача — определить, можно ли публиковать рецепт.

Разрешай ТОЛЬКО:
- настоящие кулинарные рецепты;
- блюда, напитки, десерты, соусы, салаты, супы;
- обычные тексты, связанные с приготовлением еды;
- необычные, шуточные или авторские названия блюд, если описание связано с едой.

Запрещай:
- любые рецепты, которые не связаны с едой;
- строительные материалы, технику, предметы, вещества и любые некулинарные темы;
- наркотики и их названия, включая завуалированные написания;
- оружие;
- экстремизм;
- инструкции по созданию опасных веществ;
- незаконные действия;
- насилие;
- яды и отравляющие вещества.

Важно:
- если название похоже на еду, но описание не связано с приготовлением еды — rejected;
- если название не связано с едой, например "цемент", "бетон", "оружие", "наркотики" — rejected;
- если это обычный рецепт супа, салата, мяса, рыбы, выпечки, десерта или напитка — approved.

Ответь строго одним словом:
approved или rejected

Никаких объяснений не добавляй.

Текст рецепта:
{text}
"""

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemma-4-31b-it:generateContent",
                params={"key": settings.gemini_api_key},
                json={
                    "contents": [
                        {
                            "parts": [
                                {"text": prompt}
                            ]
                        }
                    ]
                },
            )

        print("GEMINI STATUS:", response.status_code)
        print("GEMINI RESPONSE:", response.text)

        if response.status_code != 200:
            return "pending"

        data = response.json()

        try:
            parts = data["candidates"][0]["content"]["parts"]
            answer = parts[-1]["text"].strip().lower()
        except Exception:
            return "pending"

        if "rejected" in answer:
            return "rejected"

        if "approved" in answer:
            return "approved"

        return "pending"

    except Exception as e:
        print("GEMINI ERROR:", str(e))
        return "pending"