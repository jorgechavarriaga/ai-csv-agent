from fastapi import APIRouter, Query
from typing import Union
from app.services.log_service import get_logs
from app.utils.logging.logger import get_logger
from app.schemas import LogsResponse, ErrorResponse

router = APIRouter(tags=["Logs"])
logger = get_logger("AI Agent")


@router.get(
    "/logs",
    summary="Retrieve agent logs",
    response_model=Union[LogsResponse, ErrorResponse],
    responses={
        200: {"description": "List of interaction logs", "model": LogsResponse},
        500: {"description": "Unexpected error", "model": ErrorResponse},
    },
)
def fetch_logs(limit: int = Query(50, ge=1, le=200, description="Max number of logs to return")):
    """
    Retrieve the latest interaction logs.

    - Results are ordered by `created_at` descending (newest first).
    - Default limit: 50 (max 200).
    """
    try:
        logs = get_logs(limit)
        return LogsResponse(data={"logs": logs})
    except Exception as e:
        logger.error("Failed to fetch logs: %s", str(e).split("\n")[0])
        return ErrorResponse(
            error={"code": 500, "message": "Failed to fetch logs. Please try again later."}
    )

