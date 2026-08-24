import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.clients import EventsProviderClient
from app.core.usecases import (
    CancelTicketUsecase,
    CreateTicketUsecase,
    EventNotFound,
    EventNotPublished,
    ProviderError,
    SeatAlreadyTaken,
)
from app.db.repositories import EventRepository, TicketRepository
from app.db.session import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tickets", tags=["tickets"])


class TicketCreateRequest(BaseModel):
    event_id: str
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    seat: str = Field(min_length=1)


class TicketResponse(BaseModel):
    ticket_id: str


class CancelResponse(BaseModel):
    success: bool


def get_client():
    return EventsProviderClient(settings.EVENTS_PROVIDER_URL, settings.EVENTS_PROVIDER_API_KEY)


@router.post("", response_model=TicketResponse, status_code=201)
async def create_ticket(
    data: TicketCreateRequest,
    db: AsyncSession = Depends(get_db),  # noqa: B008
):
    logger.info("Creating ticket for event %s, seat %s, email %s", data.event_id, data.seat, data.email)
    client = get_client()
    events_repo = EventRepository(db)
    tickets_repo = TicketRepository(db)
    usecase = CreateTicketUsecase(client, events_repo, tickets_repo)

    try:
        ticket_id = await usecase.execute(
            data.event_id,
            data.first_name,
            data.last_name,
            data.email,
            data.seat
        )
        return TicketResponse(ticket_id=ticket_id)
    except EventNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except EventNotPublished as e:
        raise HTTPException(status_code=400, detail=str(e))
    except SeatAlreadyTaken as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ProviderError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:  # noqa: BLE001
        logger.error("Unexpected error in create_ticket: %s", str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{ticket_id}", response_model=CancelResponse)
async def cancel_ticket(
    ticket_id: str,
    db: AsyncSession = Depends(get_db),  # noqa: B008
):
    client = get_client()
    tickets_repo = TicketRepository(db)
    events_repo = EventRepository(db)
    usecase = CancelTicketUsecase(client, tickets_repo, events_repo)

    try:
        await usecase.execute(ticket_id)
        return CancelResponse(success=True)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ProviderError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:  # noqa: BLE001
        logger.error("Unexpected error in cancel_ticket: %s", str(e))
        raise HTTPException(status_code=500, detail="Internal server error")



