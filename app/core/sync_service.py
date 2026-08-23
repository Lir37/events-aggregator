import asyncio
import logging

from app.core.clients import EventsProviderClient
from app.core.usecases import SyncEventsUsecase
from app.db.repositories import EventRepository, SyncMetaRepository
from app.db.session import AsyncSessionLocal

logger = logging.getLogger(__name__)

async def run_sync():
    """Запуск синхронизации"""
    async with AsyncSessionLocal() as session:
        client = EventsProviderClient()
        event_repo = EventRepository(session)
        sync_meta_repo = SyncMetaRepository(session)
        usecase = SyncEventsUsecase(client, event_repo, sync_meta_repo)
        await usecase.execute()

async def periodic_sync(interval_hours: int = 24):
    """Фоновая задача, запускающая синхронизацию каждые interval_hours"""
    while True:
        try:
            await run_sync()
        except Exception:
            logger.exception("Sync failed")
        await asyncio.sleep(interval_hours * 3600)