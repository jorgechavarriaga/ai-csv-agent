from app.utils.db import engine, Base
from app.models.logs import AgentLog
from app.utils.logging.logger import get_logger


logger = get_logger("AI Agent")

def init_db():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
