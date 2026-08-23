import uuid
from datetime import date, datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import Event
from app.models.sync_meta import SyncMeta
from app.models.ticket import Ticket


class EventRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, event_data: dict[str, Any]):
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

    async def save_many(self, events_data: list[dict[str, Any]]):
        for data in events_data:
            event_id = data.get("id")
            if isinstance(event_id, str):
                event_id = uuid.UUID(event_id)
            stmt = select(Event).where(Event.id == event_id)
            result = await self.session.execute(stmt)
            existing = result.scalar_one_or_none()
            if existing:
                for key, value in data.items():
                    if key != "id" and hasattr(existing, key):
                        setattr(existing, key, value)
            else:
                self.session.add(Event(**data))
        await self.session.commit()

    async def get(self, event_id: str) -> Event | None:
        stmt = select(Event).where(Event.id == uuid.UUID(event_id))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_list(self, date_from: date | None = None, page: int = 1, page_size: int = 20):
        query = select(Event)
        if date_from:
            dt_from = datetime.combine(date_from, datetime.min.time())
            query = query.where(Event.event_time >= dt_from)
        total_query = select(func.count()).select_from(Event)
        if date_from:
            total_query = total_query.where(Event.event_time >= dt_from)

        total = await self.session.execute(total_query)
        count = total.scalar()

        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        result = await self.session.execute(query)
        events = result.scalars().all()
        return events, count

    async def increment_visitors(self, event_id: str):
        event = await self.get(event_id)
        if event:
            event.number_of_visitors += 1
            await self.session.commit()

    async def decrement_visitors(self, event_id: str):
        event = await self.get(event_id)
        if event and event.number_of_visitors > 0:
            event.number_of_visitors -= 1
            await self.session.commit()


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


class TicketRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, event_id: str, ticket_id: str, first_name: str, last_name: str, email: str, seat: str):
        new_ticket = Ticket(
            event_id=uuid.UUID(event_id),
            ticket_id=ticket_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            seat=seat
        )
        self.session.add(new_ticket)
        await self.session.commit()

    async def get_by_ticket_id(self, ticket_id: str) -> Ticket | None:
        stmt = select(Ticket).where(Ticket.ticket_id == ticket_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete(self, ticket: Ticket):
        await self.session.delete(ticket)
        await self.session.commit()
