from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.event import Event
from app.models.sync_meta import SyncMeta
from typing import List, Dict, Any, Optional
import uuid

class EventRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, event_data: Dict[str, Any]):
        """Сохраняет одно событие (добавляет или обновляет)"""
        event_id = event_data.get("id")
        if isinstance(event_id, str):
            event_id = uuid.UUID(event_id)
        stmt = select(Event).where(Event.id == event_id)
        result = await self.session.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            for key, value in event_data.items():
                if key != "id" and hasattr(existing, key):
                    setattr(existing, key, value)
        else:
            new_event = Event(**event_data)
            self.session.add(new_event)
        await self.session.commit()

    async def save_many(self, events_data: List[Dict[str, Any]]):
        for data in events_data:
            await self.save(data)

    async def get(self, event_id: str) -> Optional[Event]:
        stmt = select(Event).where(Event.id == uuid.UUID(event_id))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_list(self, date_from: Optional[str] = None, page: int = 1, page_size: int = 20):
        query = select(Event)
        if date_from:
            query = query.where(Event.event_time >= date_from)
        total_query = select(func.count()).select_from(Event)
        if date_from:
            total_query = total_query.where(Event.event_time >= date_from)

        total = await self.session.execute(total_query)
        count = total.scalar()

        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        result = await self.session.execute(query)
        events = result.scalars().all()
        return events, count

class SyncMetaRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_meta(self) -> SyncMeta:
        stmt = select(SyncMeta).limit(1)
        result = await self.session.execute(stmt)
        meta = result.scalar_one_or_none()
        if not meta:
            meta = SyncMeta(last_sync_time=None, last_changed_at="2000-01-01", status="idle")
            self.session.add(meta)
            await self.session.commit()
            await self.session.refresh(meta)
        return meta

    async def update_meta(self, last_sync_time, last_changed_at, status):
        meta = await self.get_meta()
        meta.last_sync_time = last_sync_time
        meta.last_changed_at = last_changed_at
        meta.status = status
        await self.session.commit()