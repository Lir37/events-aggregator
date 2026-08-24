import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.v1 import events, health, sync, tickets
from app.config import settings
from app.core.sync_service import periodic_sync


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(periodic_sync(settings.SYNC_INTERVAL_HOURS))
    yield
    task.cancel()
    await task

app = FastAPI(title="Events Aggregator", lifespan=lifespan)

# Глобальный обработчик ошибок валидации Pydantic
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    # Берём первое сообщение об ошибке для простоты
    message = errors[0].get("msg", "Invalid request") if errors else "Invalid request"
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": message},
    )

app.include_router(health.router, prefix="/api")
app.include_router(events.router, prefix="/api")
app.include_router(sync.router, prefix="/api")
app.include_router(tickets.router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "Events Aggregator is running"}
