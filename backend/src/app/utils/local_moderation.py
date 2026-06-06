import re
from functools import lru_cache
from pathlib import Path


APPROVED = "approved"
REJECTED = "rejected"
PENDING = "pending"

MODERATION_DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "moderation"
PRIVATE_BLOCKED_TERMS_FILE = MODERATION_DATA_DIR / ".blocked_terms.txt"
EXAMPLE_BLOCKED_TERMS_FILE = MODERATION_DATA_DIR / "blocked_terms.example.txt"


@lru_cache(maxsize=1)
def load_blocked_terms() -> tuple[list[str], list[str]]:
    """
    Загружает внешний служебный словарь модерации.

    Поддерживаемый формат:
    word:слово или фраза
    regex:регулярное выражение

    Также можно писать просто строку без префикса — она будет считаться word.
    Пустые строки и строки с # игнорируются.
    """
    words: list[str] = []
    regex_patterns: list[str] = []

    file_path = (
        PRIVATE_BLOCKED_TERMS_FILE
        if PRIVATE_BLOCKED_TERMS_FILE.exists()
        else EXAMPLE_BLOCKED_TERMS_FILE
    )

    if not file_path.exists():
        return words, regex_patterns

    try:
        for raw_line in file_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()

            if not line or line.startswith("#"):
                continue

            if line.startswith("regex:"):
                pattern = line.removeprefix("regex:").strip()
                if pattern:
                    regex_patterns.append(pattern)
                continue

            if line.startswith("word:"):
                word = line.removeprefix("word:").strip()
                if word:
                    words.append(word)
                continue

            words.append(line)

    except Exception as e:
        print("MODERATION DICTIONARY LOAD ERROR:", str(e))
        return [], []

    return words, regex_patterns


def normalize_text(text: str) -> str:
    replacements = {
        "0": "о",
        "1": "и",
        "3": "з",
        "4": "ч",
        "5": "с",
        "6": "б",
        "7": "т",
        "8": "в",
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


def compact_text(text: str) -> str:
    """
    Нормализация для поиска обходов:
    убирает пробелы, точки, символы и заменяет похожие латинские буквы.
    """
    replacements = {
        "ё": "е",
        "0": "о",
        "1": "и",
        "3": "з",
        "4": "ч",
        "5": "с",
        "6": "б",
        "7": "т",
        "8": "в",
        "@": "а",
        "$": "с",
        "a": "а",
        "e": "е",
        "o": "о",
        "p": "р",
        "c": "с",
        "x": "х",
        "y": "у",
        "k": "к",
        "m": "м",
        "t": "т",
        "b": "в",
        "h": "н",
    }

    text = (text or "").lower()

    for old, new in replacements.items():
        text = text.replace(old, new)

    return re.sub(r"[\s\W_]+", "", text, flags=re.IGNORECASE)


def get_tokens(text: str) -> list[str]:
    return [token for token in normalize_text(text).split() if token]


def has_word(text: str, words: list[str]) -> bool:
    normalized_text = normalize_text(text)
    tokens = set(normalized_text.split())

    for word in words:
        normalized_word = normalize_text(word)

        if not normalized_word:
            continue

        if normalized_word in tokens:
            return True

        if " " in normalized_word and normalized_word in normalized_text:
            return True

    return False


def has_external_blocked_terms(text: str) -> bool:
    """
    Проверяет текст по внешнему словарю.
    Срабатывает по обычным словам, фразам, regex и compact-проверке.
    """
    words, regex_patterns = load_blocked_terms()

    if not words and not regex_patterns:
        return False

    raw_text = text or ""
    lowered = raw_text.lower()
    normalized = normalize_text(raw_text)
    compact = compact_text(raw_text)

    for word in words:
        normalized_word = normalize_text(word)
        compact_word = compact_text(word)

        if normalized_word and has_word(normalized, [normalized_word]):
            return True

        if compact_word and len(compact_word) >= 5 and compact_word in compact:
            return True

    for pattern in regex_patterns:
        try:
            if re.search(pattern, lowered, flags=re.IGNORECASE):
                return True
        except re.error:
            print("MODERATION BAD REGEX:", pattern)

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
        consonants_count = len(
            re.findall(r"[бвгджзйклмнпрстфхцчшщbcdfghjklmnpqrstvwxz]", token)
        )

        has_vowels = vowels_count > 0
        has_too_few_vowels = vowels_count / max(len(token), 1) < 0.18
        has_too_many_consonants = consonants_count >= 5 and vowels_count <= 1
        has_repeated_letters = re.search(r"(.)\1\1", token) is not None

        if (
            not has_vowels
            or has_too_few_vowels
            or has_too_many_consonants
            or has_repeated_letters
        ):
            suspicious_tokens += 1

    long_tokens = [token for token in tokens if len(token) >= 4]

    if not long_tokens:
        return False

    return suspicious_tokens >= max(1, len(long_tokens))


def looks_like_comment_spam(text: str) -> bool:
    raw_text = (text or "").strip()
    normalized = normalize_text(raw_text)
    compact = compact_text(raw_text)
    tokens = get_tokens(raw_text)

    if not raw_text:
        return True

    if len(raw_text) < 2:
        return True

    if len(normalized) < 2:
        return True

    if re.fullmatch(r"[\W\d_]+", raw_text):
        return True

    if re.search(r"(.)\1{5,}", raw_text.lower()):
        return True

    if re.search(r"(.{2,5})\1{4,}", compact):
        return True

    if len(tokens) == 1 and len(tokens[0]) >= 8 and looks_like_gibberish(tokens[0]):
        return True

    if looks_like_gibberish(raw_text):
        return True

    return False


def moderate_recipe(title: str, description: str) -> str:
    title_text = normalize_text(title)
    description_text = normalize_text(description)
    full_text = normalize_text(f"{title or ''} {description or ''}")

    if has_external_blocked_terms(f"{title or ''} {description or ''}"):
        return REJECTED

    if not title_text:
        return REJECTED

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

    has_food_context = has_word(full_text, food_words)
    has_cooking_context = has_word(description_text, cooking_words)

    if looks_like_gibberish(title_text) and not has_food_context:
        return REJECTED

    if len(title_text) >= 10 and len(title_text.split()) == 1 and not has_food_context:
        return REJECTED

    if not has_food_context and not has_cooking_context:
        return REJECTED

    if has_food_context and has_cooking_context:
        return APPROVED

    if has_food_context and len(description_text) >= 15:
        return APPROVED

    return PENDING


def moderate_comment(text: str) -> str:
    if has_external_blocked_terms(text):
        return REJECTED

    if looks_like_comment_spam(text):
        return REJECTED

    return APPROVED