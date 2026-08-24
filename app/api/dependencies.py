from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.usecases import EventUseCase
from app.db.repositories import EventRepository
from app.db.session import get_db


async def get_event_usecase(
    db: AsyncSession = Depends(get_db), # noqa: B008
) -> EventUseCase: 
    repository = EventRepository(db)

    return EventUseCase(repository)