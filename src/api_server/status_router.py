from fastapi import APIRouter

status_router = APIRouter()

TASKS = []


@status_router.get("/status")
async def status():
    """
    Get the status of the server
    """
    return {"status": "ok", "tasks": TASKS}
