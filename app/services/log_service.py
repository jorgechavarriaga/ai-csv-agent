# app/services/log_service.py
from datetime import datetime, timezone
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.utils.db import SessionLocal
from app.models.logs import AgentLog
from app.schemas import LogEntry
from app.utils.logging.logger import get_logger

logger = get_logger("AI Agent")


def save_log(session_id: str, question: str, answer: str, client_ip: str) -> None:
    """Persist interaction log into Postgres."""
    try:
        with SessionLocal() as session:
            log = AgentLog(
                session_id=session_id,
                question=question,
                answer=answer,
                ip_address= client_ip,
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
                    ip_address=log.ip_address, 
                    answer=log.answer,
                    created_at=log.created_at.isoformat()
                )
                for log in logs
            ]
    except SQLAlchemyError as e:
        logger.error("Failed to fetch logs: %s", str(e).split("\n")[0])
        raise


def get_last_messages(session_id: str, limit: int = 5):
    """
    Return the last N question/answer pairs for a given session_id.
    Ordered from oldest to newest.
    """
    try:
        with SessionLocal() as session:
            logs = (
                session.query(AgentLog)
                .filter(AgentLog.session_id == session_id)
                .order_by(AgentLog.created_at.desc())
                .limit(limit)
                .all()
            )
        # reverse so they're in order: oldest → newest
        return list(reversed(logs))
    except SQLAlchemyError as e:
        logger.error("Failed to get session history: %s", str(e).split("\n")[0])
        return []
