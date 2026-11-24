import json

from datetime import datetime
from zoneinfo import ZoneInfo

from app.db.models import MetadataObject
from app.llm.client import YandexGPTClient

my_timezone = ZoneInfo("Asia/Irkutsk")

QUERY_SCHEMA = {
    "type": "object",
    "properties": {
        "query": {"type": "string"},
        "params": {"type": "object"},
    },
    "required": ["query", "params"],
    "additionalProperties": False,
}

async def generate_query(
    question: str,
    objects: list[MetadataObject],
    llm: YandexGPTClient
) -> dict:
     
    today = datetime.now(my_timezone).date()
    
    description = [
        {
            "name": obj.name,
            "synonym": obj.synonym,
            "schema": obj.schema
        }
        for obj in objects
    ]
    
    objects_text = json.dumps(description, ensure_ascii=False, indent=4)
    
    prompt = f"""Ты пишешь запрос на языке запросов 1С.
Используй только переденные объекты и поля.
Передавай значения через параметры. 

Для каждого параметра &Имя в тексте запроса добавь в params ключ «Имя» без символа &.
Имя ключа должно точно совпадать с именем в запросе.
Для относительных периодов вычисли обе даты по текущей дате и передай их в params.

Каждое значение в params должно быть JSON-объектом с описанием параметра.
Для даты используй поля type со значением "date" и value со строкой в формате YYYY-MM-DDTHH:MM:SS.
Для полного периода указывай начало первого дня в 00:00:00 и конец последнего дня в 23:59:59.

В виртуальной таблице .Обороты для полей с ролью «Ресурс» добавляй к имени суффикс «Оборот».
Границы периода передавай первыми двумя аргументами .Обороты(&Начало, &Конец, , ).

Для остатка на момент используй виртуальную таблицу .Остатки(&Дата, ).
В .Остатки добавляй к имени ресурса суффикс «Остаток».
Для остатка на конец дня, месяца или года передавай начало следующего дня в 00:00:00.

Текущая дата в часовом поясе {my_timezone}: {today}.
Определяй относительные периоды по этой дате.
«Прошлый месяц» означает предыдущий календарный месяц целиком.

Вопрос:
{question}

Объекты и схемы:
{objects_text}

Верни JSON с ключами query и params
"""

    result = await llm.chat_json(
        [{"role": "user", "content": prompt}],
        schema=QUERY_SCHEMA,
        temperature=0.1,
    )
    
    return result
