import asyncio
import logging

from sqlalchemy import delete, func, insert, select

from app.db.models import MetadataObject
from app.db.session import Session, create_tables
from app.onec.client import OneCClient

log = logging.getLogger(__name__)


async def load_catalog(onec: OneCClient) -> int:
    objects = await onec.metadata()
    rows = [
        {
            "name": o["name"],
            "type": o["type"],
            "synonym": o["synonym"],
            "schema": {k: v for k, v in o.items() if k not in ("name", "type", "synonym")},
        }
        for o in objects
    ]
    async with Session.begin() as session:
        await session.execute(delete(MetadataObject))
        await session.execute(insert(MetadataObject), rows)
    log.info("Каталог 1С загружен: %d объектов", len(rows))
    return len(rows)


async def catalog_size() -> int:
    async with Session() as session:
        return await session.scalar(select(func.count()).select_from(MetadataObject))


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    await create_tables()
    onec = OneCClient()
    try:
        await load_catalog(onec)
    finally:
        await onec.close()


if __name__ == "__main__":
    asyncio.run(main())
