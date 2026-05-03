import re


def normalize_text(text: str) -> str:
    replacements = {
        "0": "о",
        "1": "и",
        "3": "з",
        "4": "ч",
        "5": "с",
        "6": "б",
        "7": "т",
        "@": "а",
        "$": "с",
        "ё": "е",
    }

    text = (text or "").lower()

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"[^а-яa-z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def get_tokens(text: str) -> list[str]:
    return [token for token in normalize_text(text).split() if token]


def has_word(text: str, words: list[str]) -> bool:
    normalized_text = normalize_text(text)
    tokens = set(normalized_text.split())

    for word in words:
        normalized_word = normalize_text(word)

        if normalized_word in tokens:
            return True

        if " " in normalized_word and normalized_word in normalized_text:
            return True

    return False


def looks_like_gibberish(text: str) -> bool:
    tokens = get_tokens(text)

    if not tokens:
        return True

    suspicious_tokens = 0

    for token in tokens:
        if len(token) < 4:
            continue

        vowels_count = len(re.findall(r"[аеёиоуыэюяaeiouy]", token))
        consonants_count = len(re.findall(r"[бвгджзйклмнпрстфхцчшщbcdfghjklmnpqrstvwxz]", token))

        has_vowels = vowels_count > 0
        has_too_few_vowels = vowels_count / max(len(token), 1) < 0.18
        has_too_many_consonants = consonants_count >= 5 and vowels_count <= 1
        has_repeated_letters = re.search(r"(.)\1\1", token) is not None

        if not has_vowels or has_too_few_vowels or has_too_many_consonants or has_repeated_letters:
            suspicious_tokens += 1

    long_tokens = [token for token in tokens if len(token) >= 4]

    if not long_tokens:
        return False

    return suspicious_tokens >= max(1, len(long_tokens))


def moderate_recipe(title: str, description: str) -> str:
    title_text = normalize_text(title)
    description_text = normalize_text(description)
    full_text = normalize_text(f"{title or ''} {description or ''}")

    if not title_text:
        return "rejected"

    hard_banned_words = [
        "наркотик",
        "наркотики",
        "мефедрон",
        "меф",
        "кокаин",
        "героин",
        "марихуана",
        "амфетамин",
        "экстази",
        "оружие",
        "пистолет",
        "автомат",
        "бомба",
        "взрыв",
        "взорвать",
        "убить",
        "убийство",
        "яд",
        "отрава",
        "отравить",
        "экстремизм",
        "терроризм",
        "теракт",
        "незаконно",
    ]

    hard_non_food_words = [
        "цемент",
        "бетон",
        "щебень",
        "песок",
        "кирпич",
        "асфальт",
        "краска",
        "клей",
        "бензин",
        "солярка",
        "пластик",
        "железо",
        "металл",
        "гвоздь",
        "шуруп",
        "болт",
        "гайка",
        "стекло",
        "резина",
        "туалет",
        "унитаз",
        "бачок",
        "канализация",
        "слив",
        "ершик",
        "ванна",
        "раковина",
        "мыло хозяйственное",
        "стиральный порошок",
        "отбеливатель",
        "хлорка",
        "доместос",
        "шампунь",
        "зубная паста",
        "телефон",
        "компьютер",
        "ноутбук",
        "машина",
        "автомобиль",
        "двигатель",
        "колесо",
        "диван",
        "стул",
        "шкаф",
        "кровать",
    ]

    food_words = [
        "еда",
        "блюдо",
        "рецепт",
        "готовить",
        "приготовить",
        "варить",
        "жарить",
        "запекать",
        "тушить",
        "выпекать",
        "смешать",
        "нарезать",
        "добавить",
        "посолить",
        "поперчить",
        "суп",
        "борщ",
        "щи",
        "солянка",
        "салат",
        "каша",
        "омлет",
        "яичница",
        "пельмени",
        "вареники",
        "котлета",
        "котлеты",
        "мясо",
        "курица",
        "рыба",
        "говядина",
        "свинина",
        "фарш",
        "картофель",
        "картошка",
        "морковь",
        "лук",
        "чеснок",
        "помидор",
        "огурец",
        "капуста",
        "тесто",
        "мука",
        "сахар",
        "соль",
        "перец",
        "масло",
        "молоко",
        "сливки",
        "сыр",
        "творог",
        "яйцо",
        "яйца",
        "рис",
        "гречка",
        "макароны",
        "лапша",
        "соус",
        "майонез",
        "сметана",
        "хлеб",
        "булочка",
        "пирог",
        "пирожок",
        "торт",
        "кекс",
        "печенье",
        "десерт",
        "крем",
        "корж",
        "коржи",
        "шоколад",
        "напиток",
        "чай",
        "кофе",
        "компот",
        "морс",
        "лимонад",
        "сок",
        "наполеон",
        "цезарь",
        "оливье",
        "мимоза",
        "шарлотка",
        "плов",
        "рагу",
        "гуляш",
        "блин",
        "блины",
        "сырник",
        "сырники",
        "запеканка",
    ]

    cooking_words = [
        "варить",
        "сварить",
        "жарить",
        "обжарить",
        "запекать",
        "запечь",
        "тушить",
        "потушить",
        "выпекать",
        "испечь",
        "смешать",
        "перемешать",
        "нарезать",
        "порезать",
        "добавить",
        "посолить",
        "поперчить",
        "готовить",
        "приготовить",
        "залить",
        "замесить",
        "раскатать",
        "сформировать",
        "отварить",
    ]

    if has_word(full_text, hard_banned_words):
        return "rejected"

    if has_word(full_text, hard_non_food_words):
        return "rejected"

    has_food_context = has_word(full_text, food_words)
    has_cooking_context = has_word(description_text, cooking_words)

    if looks_like_gibberish(title_text) and not has_food_context:
        return "rejected"

    if len(title_text) >= 10 and len(title_text.split()) == 1 and not has_food_context:
        return "rejected"

    if not has_food_context and not has_cooking_context:
        return "rejected"

    return "pending"