import json

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.llm.client import LLMError, YandexGPTClient
from app.onec.client import OneCClient

import logging

log = logging.getLogger(__name__)

QUERY_SCHEMA = {
    "type": "object",
    "properties": {
        "query": {"type": "string"},
        "params": {"type": "object"},
    },
    "required": ["query", "params"],
    "additionalProperties": False,
}


def create_router(onec: OneCClient, llm: YandexGPTClient) -> Router:
    router = Router()

    @router.message(CommandStart())
    async def start(message: Message) -> None:
        await message.answer(
            "Задайте вопрос о продажах, закупках, деньгах или запасах обычным текстом."
        )

    @router.message(F.text)
    async def question(message: Message) -> None:
        question_text = message.text

        prompt = f"""
Ты пишешь запрос на языке запросов 1С.

Вопрос руководителя:
{question_text}

Используй виртуальную таблицу регистра строго в таком виде:

РегистрНакопления.Продажи.Обороты(&Начало, &Конец, , )

Период передаётся только через параметры виртуальной таблицы.
Запрещено фильтровать период через ГДЕ.
Запрещено использовать РегистрНакопления.Продажи.Обороты без круглых скобок.

Для общей суммы продаж запрос должен иметь вид:

ВЫБРАТЬ
    СУММА(СуммаОборот) КАК Сумма
ИЗ
    РегистрНакопления.Продажи.Обороты(&Начало, &Конец, , )
Верни только JSON без пояснений:
{{
  "query": "текст запроса 1С",
  "params": {{
    "Начало": {{"type": "date", "value": "ISO-дата"}},
    "Конец": {{"type": "date", "value": "ISO-дата"}}
  }}
}}

Для вопроса о январе 2021 используй даты:
Начало = 2021-01-01T00:00:00
Конец = 2021-01-31T23:59:59
"""

        try:
            generated = await llm.chat_json(
                [{"role": "user", "content": prompt}],
                schema=QUERY_SCHEMA,
                temperature=0.1,
            )
            log.info("YandexGPT сгенерировала запрос: %s", generated)

            log.info("Отправляем запрос в 1С")

            result = await onec.query(
                generated["query"],
                generated.get("params", {}),
            )

            log.info("1С вернула результат: %s", result)

            if not result.get("ok"):
                await message.answer(
                    "1С не выполнила запрос:\n"
                    f"{result.get('error', 'неизвестная ошибка')}"
                )
                return

            answer_prompt = f"""
Ответь руководителю коротко и по-русски.

Вопрос:
{question_text}

Результат запроса 1С:
{json.dumps(result, ensure_ascii=False)}

Сформулируй ответ в одном-двух предложениях.
Не упоминай JSON, Python, YandexGPT или технические детали.
"""
            answer = await llm.chat(
                [{"role": "user", "content": answer_prompt}],
                temperature=0.2,
            )
            log.info("Итоговый ответ сформирован")
            await message.answer(answer)

        except KeyError:
            await message.answer("YandexGPT вернула запрос в неправильном формате.")
        except LLMError as error:
            await message.answer(str(error))
        except Exception:
            await message.answer("Не удалось обработать вопрос.")

    return router
