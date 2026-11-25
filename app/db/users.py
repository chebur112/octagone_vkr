from sqlalchemy import select

from app.db.models import User
from app.db.session import Session

async def is_user_allowed(telegram_id: int) -> bool:
    stmt = select(User.is_allowed).where(User.telegram_id == telegram_id)
    
    async with Session() as session:
        allowed = await session.scalar(stmt)
        
    return allowed is True 