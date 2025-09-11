# app/services/log_service.py
from datetime import datetime, timezone
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.utils.db import SessionLocal
from app.models.logs import AgentLog
from app.schemas import LogEntry
from app.utils.logging.logger import get_logger

logger = get_logger("AI Agent")

def save_log(question: str, answer: str) -> None:
    """Persist interaction log into Postgres."""
    try:
        with SessionLocal() as session:
            log = AgentLog(
                question=question,
                answer=answer,
                created_at=datetime.now(timezone.utc),
            )
            session.add(log)
            session.commit()
    except SQLAlchemyError as e:
        logger.error("Failed to save log: %s", str(e).split("\n")[0])
        raise


def get_logs(limit: int = 50):
    """
    Retrieve the latest logs from the database.
    Args:
        limit (int): Maximum number of logs to return (default: 50).
    Returns:
        List[Log]: SQLAlchemy model instances (mapped to schema later).
    """
    try:
        with SessionLocal() as session:
            logs = (
                session.query(AgentLog)
                .order_by(AgentLog.created_at.desc())
                .limit(limit)
                .all()
            )
            # map ORM → schema
            return [
                LogEntry(
                    id=log.id,
                    question=log.question,
                    answer=log.answer,
                    created_at=log.created_at.isoformat()
                )
                for log in logs
            ]
    except SQLAlchemyError as e:
        logger.error("Failed to fetch logs: %s", str(e).split("\n")[0])
        raise