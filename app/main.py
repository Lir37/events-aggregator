import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

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

app.include_router(health.router, prefix="/api")
app.include_router(events.router, prefix="/api")
app.include_router(sync.router, prefix="/api")
app.include_router(tickets.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Events Aggregator is running"}
