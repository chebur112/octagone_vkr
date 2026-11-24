from sqlalchemy import select

from app.db.models import MetadataObject
from app.db.session import Session
from app.llm.client import YandexGPTClient
from app.generator.candidates import find_candidates


async def get_catalog():
    stmt = select(MetadataObject.name, MetadataObject.synonym)

    async with Session() as session:
        result = await session.execute(stmt)
        return result.all()

async def get_selected_objects(names: list[str]) -> list[MetadataObject]:
    stmt = select(MetadataObject).where(MetadataObject.name.in_(names))

    async with Session() as session:
        result = await session.scalars(stmt)
        return result.all()

def build_tables_schema(names: list[str]) -> dict:
    return {
        "type": "object",
        "properties": {
            "tables": {
                "type": "array",
                "items": {"type": "string", "enum": names},
            },
        },
        "required": ["tables"],
        "additionalProperties": False,
    }


async def select_tables(question: str, llm: YandexGPTClient) -> list[str]:
    catalog = await get_catalog()

    candidates = find_candidates(question, catalog)
    if not candidates:
        return []

    catalog_text = "\n".join(
        f"{name} — {synonym}" for name, synonym in candidates
    )

    prompt = f"""Выбери объекты метаданных 1С, которые нужны для ответа на вопрос.
Выбирай только полные имена из каталога. Не придумывай имена.
Выбери минимальный набор объектов, достаточный для ответа.
Если один объект полностью покрывает вопрос, выбери только его.
Выбирай несколько объектов, когда каждый из них нужен для отдельной части вопроса.

Вопрос руководителя:
{question}

Каталог объектов:
{catalog_text}
"""

    result = await llm.chat_json(
        [{"role": "user", "content": prompt}],
        schema=build_tables_schema([name for name, _ in candidates]),
        temperature=0.1,
    )

    tables = result["tables"]
    available_names = {name for name, _ in candidates}
    invalid_names = [name for name in tables if name not in available_names]
    if invalid_names:
        raise ValueError(f"YandexGPT вернула имена вне списка кандидатов: {invalid_names!r}")

    return tables
