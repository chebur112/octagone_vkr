import json

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.llm.client import LLMError, YandexGPTClient
from app.onec.client import OneCClient

from app.generator.query_generator import generate_query
from app.generator.query_validator import validate_query
from app.generator.table_selector import get_selected_objects, select_tables

from app.db.users import is_user_allowed

import logging

log = logging.getLogger(__name__)

async def check_access(message: Message) -> bool:
    sender = message.from_user
    if sender is None or message.sender_chat is not None:
        await message.answer("Доступ закрыт")
        return False
    
    try:
        allowed = await is_user_allowed(sender.id)
    except Exception:
        log.exception("Не удалось проверить доступ к Базе Данных")
        await message.answer("Не удалось проверить доступ к Базе Данных")
        return False
    if not allowed:
        await message.answer("Доступ закрыт")
        return False
    return True

def create_router(onec: OneCClient, llm: YandexGPTClient) -> Router:
    router = Router()

    @router.message(CommandStart())
    async def start(message: Message) -> None:
        if not await check_access(message):
            return
        await message.answer(
            "Задайте вопрос о продажах, закупках, деньгах или запасах обычным текстом."
        )

    @router.message(F.text)
    async def question(message: Message) -> None:
        if not await check_access(message):
            return
        question_text = message.text

        try:
            selected_names = await select_tables(question_text, llm)
            if not selected_names:
                await message.answer(
                    "Уточните, что хотите узнать. Например, «Сколько всего продали в январе 2021?»"
                )
                return
            objects = await get_selected_objects(selected_names)
            generated = await generate_query(question_text, objects, llm)
            log.info("YandexGPT сгенерировала запрос: %s", generated)

            try:
                generated["query"] = validate_query(
                    generated["query"],
                    generated["params"],
                    objects,
                )
            except ValueError as error:
                await message.answer(f"Запрос не прошёл проверку: {error}")
                return

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
Ответь руководителю коротко.

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
            log.exception("Ошибка обработки вопроса")
            await message.answer("Не удалось обработать вопрос.")

    return router
