import logging
from datetime import datetime, timezone

import httpx

from app.core.clients import EventsProviderClient
from app.core.mappers import EventMapper
from app.core.paginator import EventsPaginator
from app.db.repositories import EventRepository, SyncMetaRepository, TicketRepository

logger = logging.getLogger(__name__)

# Кастомные исключения для бизнес-логики
class EventNotFound(Exception):
    pass

class EventNotPublished(Exception):
    pass

class SeatAlreadyTaken(Exception):
    pass

class ProviderError(Exception):
    pass


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
            flat_event = EventMapper.from_provider(event)
            events_to_save.append(flat_event)

        if events_to_save:
            await self.event_repo.save_many(events_to_save)

        changed_values = [e["changed_at"] for e in events_to_save if e.get("changed_at")]
        max_changed = max(changed_values, default=changed_at)

        now = datetime.now(timezone.utc).isoformat()  # Исправлен часовой пояс
        await self.sync_meta_repo.update_meta(now, max_changed, "success")
        logger.info("Sync completed. Saved %d events", len(events_to_save))
        return {"saved": len(events_to_save)}


class CreateTicketUsecase:
    def __init__(self, client: EventsProviderClient, events_repo: EventRepository, tickets_repo: TicketRepository):
        self.client = client
        self.events_repo = events_repo
        self.tickets_repo = tickets_repo

    async def execute(self, event_id: str, first_name: str, last_name: str, email: str, seat: str) -> str:
        # 1. Проверка события в локальной БД
        event = await self.events_repo.get(event_id)
        if not event:
            raise EventNotFound(f"Event {event_id} not found")
        if event.status != "published":
            raise EventNotPublished(f"Event {event_id} is not published")

        # 2. Запрос к внешнему API с обработкой ошибок
        try:
            result = await self.client.register(event_id, first_name, last_name, email, seat)
            ticket_id = result.get("ticket_id")
            if not ticket_id:
                raise ProviderError("No ticket_id in response")
        except httpx.HTTPStatusError as e:
            # Специфические ошибки внешнего API
            if e.response.status_code == 404:
                raise EventNotFound(f"Event {event_id} not found in external API")
            if e.response.status_code == 400:
                # Предполагаем, что это может быть ошибка "место уже занято" или "невалидные данные"
                raise SeatAlreadyTaken("Seat is not available or invalid")
            # Другие HTTP ошибки (500, 429 и т.д.)
            logger.error("Provider HTTP error: %s", str(e))
            raise ProviderError(f"External API error: {e.response.status_code}")
        except Exception as e:  # noqa: BLE001 – осознанный перехват для логирования и проброса
            # Ошибки сети, таймауты, любые другие
            logger.error("Registration failed for event %s: %s", event_id, str(e))
            raise ProviderError(f"Registration failed: {e!s}")

        # 3. Сохранение билета в своей БД
        await self.tickets_repo.create(event_id, ticket_id, first_name, last_name, email, seat)
        await self.events_repo.increment_visitors(event_id)
        return ticket_id


class CancelTicketUsecase:
    def __init__(self, client: EventsProviderClient, tickets_repo: TicketRepository, events_repo: EventRepository):
        self.client = client
        self.tickets_repo = tickets_repo
        self.events_repo = events_repo

    async def execute(self, ticket_id: str):
        # 1. Найти билет в локальной БД
        ticket = await self.tickets_repo.get_by_ticket_id(ticket_id)
        if not ticket:
            raise ValueError("Ticket not found in local database")

        # 2. Отмена во внешнем API с обработкой ошибок
        try:
            await self.client.unregister(str(ticket.event_id), ticket_id)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                # Билет уже мог быть удалён во внешнем API – логируем, но продолжаем
                logger.warning("Ticket %s not found in external API, deleting locally", ticket_id)
            else:
                logger.error("Provider HTTP error on cancel: %s", str(e))
                raise ProviderError(f"Cancel failed: {e.response.status_code}")
        except Exception as e:  # noqa: BLE001 – осознанный перехват для логирования и проброса
            logger.error("Cancel failed for ticket %s: %s", ticket_id, str(e))
            raise ProviderError(f"Cancel failed: {e!s}")

        # 3. Удаление билета из своей БД
        await self.tickets_repo.delete(ticket)
        await self.events_repo.decrement_visitors(str(ticket.event_id))
