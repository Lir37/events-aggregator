import logging
from datetime import datetime
from typing import Optional
from app.core.clients import EventsProviderClient
from app.core.paginator import EventsPaginator
from app.db.repositories import EventRepository, SyncMetaRepository

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