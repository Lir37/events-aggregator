from fastapi import APIRouter, BackgroundTasks
from app.core.sync_service import run_sync

router = APIRouter(prefix="/sync", tags=["sync"])

@router.post("/trigger")
async def trigger_sync(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_sync)
    return {"status": "sync started"}
