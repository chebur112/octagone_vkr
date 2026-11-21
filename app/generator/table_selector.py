from sqlalchemy import select

from app.db.models import MetadataObject
from app.db.session import Session

async def get_catalog():
    stmt = select(MetadataObject.name, MetadataObject.synonym)
    
    async with Session() as session:
        result = await session.execute(stmt)
        return result.all()
    
    
