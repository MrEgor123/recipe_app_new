from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = BASE_DIR / ".blocked_terms.txt"
EXAMPLE_FILE = BASE_DIR / "blocked_terms.example.txt"


BASE_WORDS = [
    # реклама / продвижение
    "telegram", "телеграм", "whatsapp", "ватсап", "instagram", "инстаграм",
    "discord", "дискорд", "youtube", "ютуб", "vk", "вконтакте",
    "промокод", "скидка", "купон", "акция", "розыгрыш", "подписывайся",
    "подпишись", "переходи", "переходите", "канал", "ссылка", "личку",
    "лс", "профиль", "пишите в лс", "пиши в лс", "заходи ко мне",
    "больше рецептов у меня", "смотрите у меня", "купить", "заказать",
    "доставка", "магазин", "услуги", "курс", "обучение",

    # деньги / мошенничество / азарт
    "казино", "ставки", "букмекер", "заработок", "заработать",
    "инвестиции", "инвест", "крипта", "криптовалюта", "биткоин",
    "быстрые деньги", "пассивный доход",

    # запрещённые вещества / опасные темы
    "наркотик", "наркотики", "мефедрон", "меф", "кокаин", "героин",
    "марихуана", "амфетамин", "экстази", "спайс", "закладка",
    "оружие", "пистолет", "автомат", "бомба", "взрыв", "взорвать",
    "яд", "отрава", "отравить", "терроризм", "теракт", "экстремизм",
    "незаконно", "убить", "убью", "насилие",

    # некулинарный мусор для рецептов
    "цемент", "бетон", "щебень", "кирпич", "асфальт", "краска", "клей",
    "унитаз", "туалет", "канализация", "раковина", "ванна", "слив",
    "доместос", "хлорка", "отбеливатель",

    # грубость / токсичность, без раздувания списка в коде приложения
    "идиот", "тупой", "тупая", "дебил", "кретин", "урод", "мразь",
    "скотина", "лох", "чмо", "петух", "мудак", "мудила",

    # мат и частые фрагменты для compact-поиска
    "бля", "блять", "блядь", "сука", "хуй", "пизда", "пиздец",
    "ебать", "ебаный", "ебаная", "еблан", "ебло", "нахуй", "похуй",
    "говно", "дерьмо",
]


REGEX_PATTERNS = [
    r"https?://",
    r"www\.",
    r"t\.me/",
    r"telegram\.me/",
    r"vk\.com/",
    r"youtube\.com/",
    r"youtu\.be/",
    r"instagram\.com/",
    r"discord\.gg/",
    r"@[\w\d_]{4,}",
    r"\b\d{10,12}\b",
    r"(.)\1{6,}",
    r"(.{2,5})\1{4,}",
]


SEPARATORS = ["", " ", ".", "-", "_", "*", "~", "|", "/", "\\", ":"]


def normalize_seed(word: str) -> str:
    return " ".join(word.lower().strip().split())


def make_spaced_variants(word: str) -> set[str]:
    variants = set()
    cleaned = normalize_seed(word)

    if not cleaned:
        return variants

    variants.add(cleaned)

    # Для фраз не делаем побуквенные варианты, иначе будет слишком мусорно.
    if " " in cleaned:
        variants.add(cleaned.replace(" ", "  "))
        variants.add(cleaned.replace(" ", "."))
        variants.add(cleaned.replace(" ", "-"))
        variants.add(cleaned.replace(" ", "_"))
        return variants

    if len(cleaned) < 3:
        return variants

    for sep in SEPARATORS:
        if sep:
            variants.add(sep.join(cleaned))

    return variants


def make_leet_variants(word: str) -> set[str]:
    variants = set()
    cleaned = normalize_seed(word)

    replacements = {
        "о": ["0", "o"],
        "а": ["@", "a"],
        "е": ["3", "e"],
        "з": ["3"],
        "ч": ["4"],
        "с": ["5", "$", "c"],
        "б": ["6"],
        "т": ["7", "t"],
        "в": ["8", "b"],
        "р": ["p"],
        "х": ["x"],
        "у": ["y"],
        "к": ["k"],
        "м": ["m"],
        "н": ["h"],
    }

    variants.add(cleaned)

    for index, char in enumerate(cleaned):
        for replacement in replacements.get(char, []):
            variants.add(cleaned[:index] + replacement + cleaned[index + 1:])

    return variants


def build_terms() -> list[str]:
    terms = set()

    for word in BASE_WORDS:
        word = normalize_seed(word)

        for variant in make_spaced_variants(word):
            terms.add(f"word:{variant}")

        for variant in make_leet_variants(word):
            terms.add(f"word:{variant}")

    for pattern in REGEX_PATTERNS:
        terms.add(f"regex:{pattern}")

    # Добавляем compact regex для частых рекламных доменов и контактов.
    domain_suffixes = ["ru", "com", "net", "org", "io", "me"]
    for suffix in domain_suffixes:
        terms.add(rf"regex:\.{suffix}\b")

    return sorted(terms)


def write_file(path: Path, terms: list[str]) -> None:
    header = [
        "# Служебный словарь локальной модерации.",
        "# Одна строка = одно слово, фраза или regex.",
        "# Форматы:",
        "# word:слово или фраза",
        "# regex:регулярное выражение",
        "#",
        "# Файл сгенерирован автоматически.",
        "# При необходимости можно дополнять вручную.",
        "",
    ]

    path.write_text("\n".join(header + terms) + "\n", encoding="utf-8")


def main() -> None:
    terms = build_terms()

    write_file(OUTPUT_FILE, terms)
    write_file(EXAMPLE_FILE, terms)

    print(f"Generated: {OUTPUT_FILE}")
    print(f"Generated: {EXAMPLE_FILE}")
    print(f"Terms count: {len(terms)}")


if __name__ == "__main__":
    main()
