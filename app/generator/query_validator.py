import re

from app.db.models import MetadataObject


PARAMETER_PATTERN = re.compile(r"&([A-Za-zА-Яа-яЁё_][\w]*)")
TABLE_PATTERN = re.compile(
    r"\b(?:ИЗ|СОЕДИНЕНИЕ)\s+([А-Яа-яЁёA-Za-z_][\wА-Яа-яЁё.]*)",
    re.IGNORECASE,
)
FIRST_PATTERN = re.compile(r"\bПЕРВЫЕ\s+(\d+)\b", re.IGNORECASE)
FIRST_KEYWORD_PATTERN = re.compile(r"\bПЕРВЫЕ\b", re.IGNORECASE)
VIRTUAL_TABLES = (
    ".Обороты",
    ".ОборотыДтКт",
    ".Остатки",
    ".ОстаткиИОбороты",
    ".СрезПоследних",
    ".СрезПервых",
)
MAX_ROWS = 1000


def validate_query(
    query: str,
    params: dict,
    selected_objects: list[MetadataObject],
) -> str:
    if not query or not query.strip():
        raise ValueError("Запрос пустой")

    query = query.strip()
    if query.split(maxsplit=1)[0] != "ВЫБРАТЬ":
        raise ValueError("Запрос должен начинаться с ВЫБРАТЬ")

    if ";" in query:
        raise ValueError("В запросе не должно быть нескольких операторов")

    if not isinstance(params, dict):
        raise ValueError("Параметры запроса должны быть объектом")

    used_params = set(PARAMETER_PATTERN.findall(query))
    missing_params = used_params - params.keys()
    if missing_params:
        names = ", ".join(sorted(missing_params))
        raise ValueError(f"Не переданы параметры запроса: {names}")

    allowed_tables = set()
    for obj in selected_objects:
        allowed_tables.add(obj.name)
        allowed_tables.update(obj.name + suffix for suffix in VIRTUAL_TABLES)

    query_tables = TABLE_PATTERN.findall(query)
    if not query_tables:
        raise ValueError("В запросе не найдены таблицы после ИЗ или СОЕДИНЕНИЕ")

    unknown_tables = set(query_tables) - allowed_tables
    if unknown_tables:
        names = ", ".join(sorted(unknown_tables))
        raise ValueError(f"Запрос использует невыбранные таблицы: {names}")

    first_match = FIRST_PATTERN.search(query)
    if FIRST_KEYWORD_PATTERN.search(query) and not first_match:
        raise ValueError("После ПЕРВЫЕ должно быть указано число строк")

    if first_match:
        requested_rows = int(first_match.group(1))
        if requested_rows > MAX_ROWS:
            query = FIRST_PATTERN.sub(f"ПЕРВЫЕ {MAX_ROWS}", query, count=1)
    else:
        query = re.sub(r"^ВЫБРАТЬ\b", f"ВЫБРАТЬ ПЕРВЫЕ {MAX_ROWS}", query, count=1)

    return query
