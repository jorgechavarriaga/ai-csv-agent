from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from app.routers import agent, health, logs
from app.utils.db import engine, Base
from app.utils.error_handler import register_exception_handlers  
from app.services.vectorstore import get_all_vector_stores
from app.utils.logging.logger import get_logger
from fastapi.middleware.cors import CORSMiddleware
from app.utils.init_db import init_db
from app.config.settings import settings


logger = get_logger("AI Agent")

# FastAPI app with full Swagger docs
app = FastAPI(
    title="AI Agent with pgvector",
    description="""
    This API provides access to an AI-powered assistant restricted to a specific dataset
    (loaded from `data/cv_en.txt` and stored in PostgreSQL with pgvector).

    ## Endpoints
    - **/api/v1/ask** → Ask a question and get an answer based strictly on the dataset.
    - **/api/v1/status** → Health check endpoint.

    ## Behavior
    - Answers are generated **only** from the ingested dataset.
    - If the answer is not available in the dataset, the agent will respond politely
      indicating that the requested information is not present.
    """,
    version="1.1.0",
    docs_url=None,     
    redoc_url=None,    
    openapi_url=None   
)

init_db()

register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://www.chavazystem.tech", "http://localhost:8000"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    try:
        Base.metadata.create_all(bind=engine)
        app.state.vector_stores = get_all_vector_stores(force=settings.ENABLE_FORCE_SEED)  
        if app.state.vector_stores:
            logger.info("Vector stores initialized successfully.")
        else:
            logger.warning("Vector stores not available at startup.")
    except (SQLAlchemyError, OperationalError) as e:
        logger.error("Database not reachable during startup: %s", e)
        app.state.vector_stores = {}

@app.on_event("shutdown")
def on_shutdown():
    # If needed → close connections, cleanup, etc.
    pass

# Register routers
app.include_router(agent.router, prefix="/api/v1", tags=["Agent"])
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
# app.include_router(logs.router, prefix="/api/v1", tags=["Logs"])


# Redirect root to Swagger UI
@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="https://www.chavazystem.tech")

