import logging
from datetime import datetime
from typing import Optional
from app.core.clients import EventsProviderClient
from app.core.paginator import EventsPaginator
from app.db.repositories import EventRepository, SyncMetaRepository, TicketRepository

logger = logging.getLogger(__name__)

class SyncEventsUsecase:
    def __init__(self, client: EventsProviderClient, event_repo: EventRepository, sync_meta_repo: SyncMetaRepository):
        self.client = client
        self.event_repo = event_repo
        self.sync_meta_repo = sync_meta_repo

    async def execute(self, manual: bool = False):
        logger.info("Starting sync (manual=%s)", manual)
        meta = await self.sync_meta_repo.get_meta()
        changed_at = meta.last_changed_at or "2000-01-01"

        paginator = EventsPaginator(self.client, changed_at)
        events_to_save = []
        async for event in paginator:
            place = event.get("place", {})
            flat_event = {
                "id": event["id"],
                "name": event["name"],
                "place_id": place.get("id"),
                "place_name": place.get("name"),
                "place_city": place.get("city"),
                "place_address": place.get("address"),
                "seats_pattern": place.get("seats_pattern"),
                "event_time": event.get("event_time"),
                "registration_deadline": event.get("registration_deadline"),
                "status": event.get("status"),
                "number_of_visitors": event.get("number_of_visitors", 0),
                "changed_at": event.get("changed_at"),
                "created_at": event.get("created_at"),
                "status_changed_at": event.get("status_changed_at"),
            }
            events_to_save.append(flat_event)

        for ev in events_to_save:
            await self.event_repo.save(ev)

        now = datetime.now().isoformat()
        max_changed = max([e["changed_at"] for e in events_to_save]) if events_to_save else changed_at
        await self.sync_meta_repo.update_meta(now, max_changed, "success")
        logger.info("Sync completed. Saved %d events", len(events_to_save))
        return {"saved": len(events_to_save)}

class CreateTicketUsecase:
    def __init__(self, client: EventsProviderClient, events_repo: EventRepository, tickets_repo: TicketRepository):
        self.client = client
        self.events_repo = events_repo
        self.tickets_repo = tickets_repo

    async def execute(self, event_id: str, first_name: str, last_name: str, email: str, seat: str) -> str:
        # Проверяем событие
        event = await self.events_repo.get(event_id)
        if not event:
            raise ValueError("Event not found")
        if event.status != "published":
            raise ValueError("Event is not published")

        # Регистрация во внешнем API
        try:
            result = await self.client.register(event_id, first_name, last_name, email, seat)
            ticket_id = result.get("ticket_id")
            if not ticket_id:
                raise ValueError("No ticket_id in response")
        except Exception as e:
            raise ValueError(f"Registration failed: {str(e)}")

        # Сохраняем у себя
        await self.tickets_repo.create(event_id, ticket_id, first_name, last_name, email, seat)
        # Увеличиваем счётчик посетителей
        await self.events_repo.increment_visitors(event_id)
        return ticket_id

class CancelTicketUsecase:
    def __init__(self, client: EventsProviderClient, tickets_repo: TicketRepository, events_repo: EventRepository):
        self.client = client
        self.tickets_repo = tickets_repo
        self.events_repo = events_repo

    async def execute(self, ticket_id: str):
        # Находим запись в БД
        ticket = await self.tickets_repo.get_by_ticket_id(ticket_id)
        if not ticket:
            raise ValueError("Ticket not found")

        # Отменяем во внешнем API
        try:
            await self.client.unregister(str(ticket.event_id), ticket_id)
        except Exception as e:
            raise ValueError(f"Cancel failed: {str(e)}")

        # Удаляем запись из БД
        await self.tickets_repo.delete(ticket)
        # Уменьшаем счётчик посетителей
        await self.events_repo.decrement_visitors(str(ticket.event_id))
