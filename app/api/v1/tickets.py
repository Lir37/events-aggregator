from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.db.session import get_db
from app.db.repositories import EventRepository, TicketRepository
from app.core.clients import EventsProviderClient
from app.core.usecases import CreateTicketUsecase, CancelTicketUsecase
from app.config import settings

router = APIRouter(prefix="/tickets", tags=["tickets"])

class TicketCreateRequest(BaseModel):
    event_id: str
    first_name: str
    last_name: str
    email: str
    seat: str

class TicketResponse(BaseModel):
    ticket_id: str

class CancelResponse(BaseModel):
    success: bool

def get_client():
    return EventsProviderClient(settings.EVENTS_PROVIDER_URL, settings.EVENTS_PROVIDER_API_KEY)

@router.post("", response_model=TicketResponse, status_code=201)
async def create_ticket(
    data: TicketCreateRequest,
    db: AsyncSession = Depends(get_db)
):
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
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{ticket_id}", response_model=CancelResponse)
async def cancel_ticket(
    ticket_id: str,
    db: AsyncSession = Depends(get_db)
):
    client = get_client()
    tickets_repo = TicketRepository(db)
    events_repo = EventRepository(db)
    usecase = CancelTicketUsecase(client, tickets_repo, events_repo)
    try:
        await usecase.execute(ticket_id)
        return CancelResponse(success=True)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
