from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.clients import EventsProviderClient
from app.core.usecases import EventUseCase, GetSeatsUseCase
from app.db.repositories import EventRepository
from app.db.session import get_db


async def get_event_usecase(
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> EventUseCase:
    repository = EventRepository(db)

    return EventUseCase(repository)


def get_seats_client() -> EventsProviderClient:
    return EventsProviderClient(
        settings.EVENTS_PROVIDER_URL,
        settings.EVENTS_PROVIDER_API_KEY,
    )


async def get_seats_usecase(
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> GetSeatsUseCase:
    event_repository = EventRepository(db)

    client = get_seats_client()

    return GetSeatsUseCase(
        client=client,
        event_repo=event_repository,
    )