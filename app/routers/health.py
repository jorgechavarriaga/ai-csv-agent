from fastapi import APIRouter
from app.schemas import HealthResponse, HealthData, ErrorResponse
from app.utils.logging.logger import get_logger


logger = get_logger("AI Agent")

router = APIRouter(tags=["Health"])

@router.get(
    "/status",
    summary="Health check endpoint",
    response_model=HealthResponse,
    responses={
        200: {"description": "API is up and running", "model": HealthResponse},
        500: {"description": "Unexpected error", "model": ErrorResponse},
    }
)
def health():
    """
    Verify that the API is alive and connected.

    - Returns a JSON response with `status=success` and `data={"status": "ok"}`.
    - Monitoring tools or load balancers can use this for health checks.
    """
    try:
        return HealthResponse(data=HealthData(status="ok"))
    except Exception as e:
        logger.error("Failed to fetch status: %s", str(e).split("\n")[0])
        return ErrorResponse(
            error={"code": 500, "message": "Unexpected error in health check"}
        )