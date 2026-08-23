from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.repositories import EventRepository

router = APIRouter(prefix="/events", tags=["events"])

@router.get("")
async def list_events(
    date_from: str = Query(None, description="YYYY-MM-DD"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    repo = EventRepository(db)
    events, total = await repo.get_list(date_from, page, page_size)
    base_url = "/api/v1/events"
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
