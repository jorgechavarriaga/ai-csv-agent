from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError, OperationalError, ProgrammingError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.schemas import ErrorResponse
from app.utils.logging.logger import get_logger


logger = get_logger("AI Agent")

def register_exception_handlers(app: FastAPI) -> None:
    """
    Attach global exception handlers to the FastAPI app.
    Ensures all errors are returned as consistent JSON
    and logged with proper severity.
    """

    def error_response(status_code: int, message: str):
        return JSONResponse(
            status_code=status_code,
            content=ErrorResponse(error={"code": status_code, "message": message}).dict()
        )


    # --- FastAPI request validation errors ---
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning("Validation error: %s", str(exc).split("\n")[0])
        return error_response(422, "Validation failed. Please check your input.")
    

    # --- SQLAlchemy errors ---
    @app.exception_handler(OperationalError)
    async def operational_exception_handler(request: Request, exc: OperationalError):
        logger.error("Database operational error: %s", str(exc).split("\n")[0])
        return error_response(503, "Vector store not available")

    @app.exception_handler(ProgrammingError)
    async def programming_exception_handler(request: Request, exc: ProgrammingError):
        logger.error("Database programming error: %s", str(exc).split("\n")[0])
        return error_response(500, "A database query failed. Please contact support.")

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
        logger.error("Database error: %s", str(exc).split("\n")[0])
        return error_response(500, "A database error occurred. Please try again later.")
    

    # --- Unified handler for all HTTP exceptions ---
    @app.exception_handler(StarletteHTTPException)
    async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException):
        code = exc.status_code
        if code == 404:
            logger.warning("Not Found: %s %s", request.method, request.url.path)
            return error_response(404, "Endpoint not found")
        elif code == 405:
            logger.warning("Method Not Allowed: %s %s", request.method, request.url.path)
            return error_response(405, "Method not allowed")
        elif code == 401:
            logger.warning("Unauthorized: %s %s", request.method, request.url.path)
            return error_response(401, "Authentication required")
        elif code == 403:
            logger.warning("Forbidden: %s %s", request.method, request.url.path)
            return error_response(403, "Access denied")
        elif code == 413:
            logger.error("Payload too large on %s %s", request.method, request.url.path)
            return error_response(413, "Request payload too large")
        elif code == 429:
            logger.warning("Rate limit exceeded on %s %s", request.method, request.url.path)
            return error_response(429, "Rate limit exceeded. Try again later.")
        elif code == 504:
            logger.error("Gateway timeout on %s %s", request.method, request.url.path)
            return error_response(504, "Upstream service timed out. Please try again later.")

        # fallback for any other HTTP error
        logger.warning(f"HTTP error {code}: {exc.detail}")
        return error_response(code, exc.detail)


    # --- Catch-all ---
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.error("Unexpected error: %s", str(exc).split("\n")[0])
        return error_response(500, "An unexpected error occurred. Please try again later.")
    

