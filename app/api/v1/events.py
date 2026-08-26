from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies import (
    get_event_usecase,
    get_seats_usecase,
)
from app.core.usecases import (
    EventNotFound,
    EventNotPublished,
    EventUseCase,
    GetSeatsUseCase,
    ProviderError,
)

router = APIRouter(prefix="/events", tags=["events"])


@router.get("")
async def list_events(
    date_from: Annotated[
        date | None,
        Query(description="YYYY-MM-DD"),
    ] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    usecase: EventUseCase = Depends(get_event_usecase),  # noqa: B008
):
    events, total = await usecase.get_events(
        date_from,
        page,
        page_size,
    )

    base_url = "/api/events"

    results = []

    for e in events:
        results.append(
            {
                "id": str(e.id),
                "name": e.name,
                "place": {
                    "id": str(e.place_id),
                    "name": e.place_name,
                    "city": e.place_city,
                    "address": e.place_address,
                },
                "event_time": (
                    e.event_time.isoformat()
                    if e.event_time
                    else None
                ),
                "registration_deadline": (
                    e.registration_deadline.isoformat()
                    if e.registration_deadline
                    else None
                ),
                "status": e.status,
                "number_of_visitors": e.number_of_visitors,
            }
        )

    next_page = (
        f"{base_url}?page={page + 1}&page_size={page_size}"
        if total > page * page_size
        else None
    )

    prev_page = (
        f"{base_url}?page={page - 1}&page_size={page_size}"
        if page > 1
        else None
    )

    return {
        "count": total,
        "next": next_page,
        "previous": prev_page,
        "results": results,
    }


@router.get("/{event_id}")
async def get_event_detail(
    event_id: str,
    usecase: EventUseCase = Depends(get_event_usecase),  # noqa: B008
):
    event = await usecase.get_event(event_id)

    if not event:
        raise HTTPException(
            status_code=404,
            detail="Event not found",
        )

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
        "event_time": (
            event.event_time.isoformat()
            if event.event_time
            else None
        ),
        "registration_deadline": (
            event.registration_deadline.isoformat()
            if event.registration_deadline
            else None
        ),
        "status": event.status,
        "number_of_visitors": event.number_of_visitors,
    }


@router.get("/{event_id}/seats")
async def get_available_seats(
    event_id: str,
    usecase: GetSeatsUseCase = Depends(get_seats_usecase),  # noqa: B008
):
    try:
        seats = await usecase.execute(event_id)

        return {
            "event_id": event_id,
            "available_seats": seats,
        }

    except EventNotFound:
        raise HTTPException(
            status_code=404,
            detail="Event not found",
        )

    except EventNotPublished:
        raise HTTPException(
            status_code=400,
            detail="Event is not published, cannot get seats",
        )

    except ProviderError:
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch seats from external provider",
        )