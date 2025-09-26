from fastapi import APIRouter
from app.schemas import HealthResponse, HealthData, ErrorResponse, SuccessResponse
from app.utils.logging.logger import get_logger
from app.utils.llm import get_chat_status

logger = get_logger("AI Agent")
router = APIRouter(tags=["Health"])


@router.get(
    "/health",
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
    

@router.get(
    "/health/ai",
    summary="Health check for OpenAI API",
    response_model=SuccessResponse,
    responses={
        200: {"description": "LLM is online", "model": SuccessResponse},
        503: {"description": "LLM is offline", "model": ErrorResponse},
    }
)
def ai_health_check():
    """
    Checks the availability of the LLM providers (OpenAI, OpenRouter, Gemini).
    Returns 'online' or 'offline' plus provider info.
    """
    try:
        status_info = get_chat_status()  

        if status_info["status"] == "online":
            return SuccessResponse(data=status_info)
        else:
            logger.warning("LLM service reported as offline.")
            return ErrorResponse(
                status="error",
                error={"code": 503, "message": "LLM service unavailable"}
            )

    except Exception as e:
        logger.error("LLM health check failed: %s", str(e).split("\n")[0])
        return ErrorResponse(
            status="error",
            error={"code": 500, "message": "Unexpected error in LLM health check"}
        )