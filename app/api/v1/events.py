import logging
import time
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.clients import EventsProviderClient
from app.core.statuses import EventStatus  # ✅ импорт Enum
from app.db.repositories import EventRepository
from app.db.session import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/events", tags=["events"])

seats_cache = {}
CACHE_TTL = 30

def get_client():
    return EventsProviderClient(settings.EVENTS_PROVIDER_URL, settings.EVENTS_PROVIDER_API_KEY)


@router.get("")
async def list_events(
    date_from: Annotated[date | None, Query(description="YYYY-MM-DD")] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    db: AsyncSession = Depends(get_db),  # noqa: B008
):
    repo = EventRepository(db)
    events, total = await repo.get_list(date_from, page, page_size)
    base_url = "/api/events"
    results = []
    for e in events:
        results.append({
            "id": str(e.id),
            "name": e.name,
            "place": {
                "id": str(e.place_id),
                "name": e.place_name,
                "city": e.place_city,
                "address": e.place_address,
            },
            "event_time": e.event_time.isoformat() if e.event_time else None,
            "registration_deadline": e.registration_deadline.isoformat() if e.registration_deadline else None,
            "status": e.status,
            "number_of_visitors": e.number_of_visitors,
        })
    next_page = f"{base_url}?page={page+1}&page_size={page_size}" if total > page * page_size else None
    prev_page = f"{base_url}?page={page-1}&page_size={page_size}" if page > 1 else None
    return {
        "count": total,
        "next": next_page,
        "previous": prev_page,
        "results": results
    }


@router.get("/{event_id}")
async def get_event_detail(
    event_id: str,
    db: AsyncSession = Depends(get_db),  # noqa: B008
):
    repo = EventRepository(db)
    event = await repo.get(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return {
        "id": str(event.id),
        "name": event.name,
        "place": {
            "id": str(event.place_id),
            "name": event.place_name,
            "city": event.place_city,
            "address": event.place_address,
            "seats_pattern": event.seats_pattern,
        },
        "event_time": event.event_time.isoformat() if event.event_time else None,
        "registration_deadline": event.registration_deadline.isoformat() if event.registration_deadline else None,
        "status": event.status,
        "number_of_visitors": event.number_of_visitors,
    }


@router.get("/{event_id}/seats")
async def get_available_seats(
    event_id: str,
    db: AsyncSession = Depends(get_db),  # noqa: B008
):
    repo = EventRepository(db)
    event = await repo.get(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    # ✅ Исправлено: используем Enum для сравнения статуса
    if event.status != EventStatus.PUBLISHED.value:
        raise HTTPException(status_code=400, detail="Event is not published, cannot get seats")

    cache_key = f"seats_{event_id}"
    now = time.time()
    if cache_key in seats_cache and (now - seats_cache[cache_key]["timestamp"]) < CACHE_TTL:
        return {"event_id": event_id, "available_seats": seats_cache[cache_key]["seats"]}

    client = get_client()
    try:
        data = await client.get_seats(event_id)
        seats = data.get("seats", [])
        seats_cache[cache_key] = {"seats": seats, "timestamp": now}
        return {"event_id": event_id, "available_seats": seats}
    except Exception as e:  # noqa: BLE001
        logger.error("Error fetching seats for event %s: %s", event_id, e)
        raise HTTPException(status_code=500, detail="Failed to fetch seats from external provider")