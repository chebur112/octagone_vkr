import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.bot.handlers import create_router
from app.config import settings
from app.db.catalog import catalog_size, load_catalog
from app.db.session import create_tables
from app.llm.client import YandexGPTClient
from app.onec.client import OneCClient


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    await create_tables()
    onec = OneCClient()
    llm = YandexGPTClient()

    try:
        if await catalog_size() == 0:
            await load_catalog(onec)

        bot = Bot(settings.bot_token)
        dp = Dispatcher()
        dp.include_router(create_router(onec, llm))

        await dp.start_polling(bot)
    finally:
        await onec.close()
        await llm.close()


if __name__ == "__main__":
    asyncio.run(main())
